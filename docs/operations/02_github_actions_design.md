# GitHub Actions 設計

全自動で定期的にコンテンツを拡充・更新するためのフローを設計します。

## 1. ワークフロー概要

- **ファイルパス**: `.github/workflows/generate-and-deploy.yml`
- **トリガー (Triggers)**:
  - `schedule`: 定期実行。例として毎日深夜2時 (JST) -> `cron: '0 17 * * *'` (UTC)
  - `workflow_dispatch`: 手動実行用。任意のタイミングで生成・デプロイを再開可能にします。

## 2. 処理フロー (Jobs & Steps)

**【重要】無限ループ対策とシンプル化**:
自動生成したコンテンツを `main` ブランチに直接Commit & Pushすると、ワークフローが無限ループするリスクがあります。
これを防ぐため、**「Actionsの中で生成したデータはリポジトリ（Git）にはコミットせず、その場でビルドしてCloudflare Pagesへ直接デプロイ（Upload）するのみ」** という最もシンプルで安全な構成（単一フロー）を採用します。

### 全体ワークフロー定義 (例)

```yaml
name: Generate and Deploy

on:
  schedule:
    - cron: '0 17 * * *' # 毎日JST 2:00
  workflow_dispatch: # 手動実行

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout main branch
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Python dependencies
        run: pip install -r backend/requirements.txt

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install Node dependencies
        run: npm ci
        working-directory: ./frontend

      - name: Data Generation (repo収集 & 生成)
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python src/main.py
        working-directory: ./backend

      - name: Quality Check (品質計測)
        run: python src/tools/quality_check.py
        working-directory: ./backend

      - name: Sync generated content
        # Stale content（古い生成物）が残るのを防ぐため、同期前に既存の対象ディレクトリをクリーンアップする
        run: |
          rm -rf frontend/content/repos frontend/content/topics frontend/content/languages
          mkdir -p frontend/content
          cp -r backend/output/* frontend/content/


      - name: Build Next.js
        run: npm run build
        working-directory: ./frontend

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: 'github-seo-site'
          directory: 'frontend/out' # ビルド成果物を直接デプロイ
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

## 3. デプロイ方式の統一とディレクトリ同期 (単一フロー)

デプロイフローは **「GitHub Actions 上で生成からビルドまで行い、成果物を Cloudflare Pages へ直接デプロイする」** 方式に完全統一します。
（deployブランチなどのGitへの書き戻しは一切行いません）

**バックエンドとフロントエンドの分離 (Content Sync)**:
データ生成（Python側）は `backend/output/` へ出力し、ビルド前（Next.js側）に `frontend/content/` へコピー（同期）する構成としています。
**理由**:
- **責務の分離**: Backendは「データを生成・出力するだけ」、Frontendは「配置されたデータを表示するだけ」と責務が完全に分離されます。
- **Stale Content (古いデータ) の排除**: `cp` の前に `rm -rf` を挟むことで、前回生成されて今回除外された（削除済み）リポジトリやトピックのJSONがフロントエンドのビルドに混入する事故を完全に防ぎ、実データと静的出力の整合性を毎ビルドごとに100%保証(ステートレス化)します。
- **CIでの明示性**: YAML上で明示的に同期ステップを踏むことで、「ここで依存関係が渡されること」と「クリーンな状態からビルドされること」が追いやすくなります。

**理由 (単一フロー化)**:
- **二重管理の排除**: Gitリポジトリへの成果物PushとCloudflareへのDeployという二重系統をなくし、運用をシンプルにします。
- **無限ループの防止**: GitへのPushが発生しないため、意図せぬワークフローの再帰呼び出しを完全に防げます。
- **状態を持たない (Stateless)**: 毎回 `main` のコードを正として動的にJSONを生成・ビルドするため、依存関係やコンフリクトの問題が起きません。

## 4. リトライと失敗時の再実行

- **GitHub Actionsレベル**:
  - 一時的なネットワークエラーやAPIの500エラー対策として、再実行を手動で容易に行える `workflow_dispatch` を用意しています。
- **スクリプトレベル (Python)**:
  - GitHub APIおよびOpenAI API呼び出し時には、ライブラリ（`tenacity`や`backoff`等）を用いて**Exponential Backoffによる自動リトライ**（最大3回程度）を実装します。これにより一時的なRate Limitエラーなどを吸収します。
