# Secrets / .env 管理方針

ローカル環境とCI/CD環境における機密情報（APIキーなど）の管理方針を明確にします。

## 1. 必要なシークレット一覧

| 変数名 | 用途 | 必須環境 |
|---|---|---|
| `OPENAI_API_KEY` | LLM（ChatGPT等）によるコンテンツ自動生成 | Local / CI |
| `GITHUB_TOKEN` | GitHub APIのRate Limit回避、リポジトリ検索および情報取得。CI環境ではコミットのPush機能 | Local / CI |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare PagesへのCLI/Action経由でのデプロイ認証 | CI |
| `CLOUDFLARE_API_TOKEN` | Cloudflare PagesへのCLI/Action経由でのデプロイ認証 | CI |
| `NEXT_PUBLIC_GA_ID` | (必須ではないが推奨) Google Analyticsの測定ID | Local / CI |

## 2. ローカル開発環境の管理 (.env)

- **ルール制限**: `*.env` ファイル（例: `.env`, `.env.local`）はすべて `.gitignore` に登録し、**絶対にGitリポジトリにコミットしない**ようにします。
- **テンプレート**: 開発者がすぐにセットアップできるよう、ダミー値を入れた `.env.example` または `.env.template` をリポジトリにコミットしておきます。
  ```env
  # .env.example
  OPENAI_API_KEY=your_openai_api_key_here
  GITHUB_TOKEN=your_github_personal_access_token_here
  NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
  ```

## 3. CI/CD環境の管理 (GitHub Repository Secrets)

GitHub Actions上で安全に機密情報を扱うための設定です。

1. GitHubリポジトリの **Settings** > **Secrets and variables** > **Actions** を開く。
2. **New repository secret** をクリックし、必要な変数（上記リストのCIで必要なもの）を登録します。
3. GitHub Actions の `.yml` ファイルからは以下のように呼び出します。
   ```yaml
   env:
     OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
     GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
   ```
   ※ GitHub Actionsがリポジトリへコードをプッシュする際の一時トークンには、デフォルトで提供される `${{ secrets.GITHUB_TOKEN }}` を使いますが、別途強力な権限が必要な場合は `PERSONAL_ACCESS_TOKEN` をSecretに登録して使用します。

## 4. トークンの権限最小化 (Principle of Least Privilege)

セキュリティリスクを避けるため、発行するトークンの権限は必要最小限にとどめます。

- **GitHub Token (Personal Access Token)**: リポジトリの読み取り権限（Public Repoへのアクセス用）のみ。
- **Cloudflare API Token**: アカウント全体の管理権限ではなく、「Cloudflare Pages の編集・デプロイ権限」にスコープを絞ったカスタムトークンを発行します。
- **OpenAI API Key**: アカウント利用上限（Usage Limit）を設定し、万が一漏洩した場合でも被害額を最小（例: 月額$10〜$50のハードリミット）に留める設定を必ず行います。
