# デプロイ設計 (Deployment Design)

本基盤の目的は「低コスト」「運用負荷の最小化」「SEO最適化」であるため、フルマネージドかつ静的サイトホスティングに優れた構成を採用します。

## 1. 推奨ホスティング環境: Cloudflare Pages

VercelやGitHub Pagesも候補になりますが、以下の理由から **Cloudflare Pages** を最有力として推奨します。

- **理由**:
  - **帯域幅料金が無料 (Egress Free)**: 将来的にアクセスが急増したり、大量の画像/リソースを配信することになっても課金によるダウンや高額請求のリスクがありません。
  - **高速なCDN**: グローバルエッジネットワークにより、SEOに重要なコアウェブバイタル (Core Web Vitals) のスコアを維持しやすい。
  - **Next.js Static Exportとの親和性**: `next build` で出力される `out/` ディレクトリをそのままデプロイでき、非常にシンプルです。

## 2. デプロイフローの完全単一化

**デプロイ方式: GitHub Actions でのビルド＆直接デプロイ** に統一して運用します。

Cloudflare側の自動ビルド（GitHubリポジトリ連携によるPushトリガーでのビルド）は「無効」にし、すべての制御をGitHub Actionsに寄せます。また、Gitリポジトリへの自動コミット（deployブランチ等）も行いません。

1. **データ生成**: GitHub Actions上でPythonスクリプトを実行し、リポジトリ収集・記事生成（JSON）を行います。
2. **静的ビルド**: 同じWorkflow内で Next.js をビルドし、生成されたデータを元に `out/` ディレクトリにHTMLを生成します。
3. **直接デプロイ**: Actions内で `cloudflare/pages-action` を実行し、API経由で `out/` ディレクトリを直接Cloudflare Pagesにアップロード（デプロイ）します。

この方式により、「GitPushの無限ループ」や「二重系統による障害切り分けの複雑化」を根本から防ぎます。

## 3. 初期セットアップ手順

このA方式を実現するためのCloudflare側・GitHub側の初回設定手順です。

1. **Cloudflare ダッシュボードでの作業**:
   - 「Workers & Pages」>「Pages」で「アセットをアップロード (`Direct Upload`)」プロジェクトを新規作成する。（「GitHubに接続」は使用しません）
   - プロジェクト名を決定（例: `github-seo-site`）。
   - マイプロフィール > API Tokens から、対象アカウント＆Pagesの「編集」権限を持ったカスタムトークンを発行する。
   - Account IDをメモする。
2. **GitHub Repository での作業**:
   - リポジトリの Settings > Secrets and variables > Actions を開く。
   - `CLOUDFLARE_API_TOKEN` と `CLOUDFLARE_ACCOUNT_ID` をSecretとして追加する。
   - 上記設定後、`.github/workflows/generate-and-deploy.yml`（Actions設計書参照）をコミットし、`workflow_dispatch` で手動実行してデプロイが通るか確認する。
3. **動作確認**:
   - Actionsが成功したら、発行された `*.pages.dev` ドメインにアクセスし、ページが正しく表示されるか確認する。
   - (オプション) 独自ドメインをCloudflareで設定する。
