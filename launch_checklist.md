# 最短公開向けチェックリスト (MVP Launch Checklist)

このプロジェクトのMVP構築が完了し、バックエンド(Python)からフロントエンド(Next.js)へのデータ連携と静的ページ生成が通ることを確認しました。
今後、実際に本番公開（ホスティング）して運用を開始するために、以下の手順を進めてください。

## 1. Secretsの設定 (API キー等の取得)
LLMによる自動生成やGitHub Rate Limit 回避のため、必要な各種Token・APIキーを取得します。
- [ ] **(必須)** GitHubのDeveloper Settingsから `Personal Access Token`（読取権限のみ）を発行する。
- [ ] **(任意)** OpenAIやAnthropic等、外部LLMプロバイダーを利用する場合のみAPIキーを発行する（デフォルトの `rule_based` プロバイダーを利用する場合は不要）。
- [ ] `backend/.env` を作成し、ローカル開発用に `GITHUB_TOKEN=your_token_here` 等を記述する。

## 2. 初回バッチの実行と生成結果の確認
- [ ] `backend/src/main.py` に記述されている `targets` のリストを、初期として狙いたいリポジトリ（10〜30件程度）に書き換える。
- [ ] または `llm_generator.py` の Provider 設定を自分の環境（`rule_based`, `local_model`, `openai`）に合わせて調整する。
- [ ] バックエンドディレクトリにて `python src/main.py` を実行する。
- [ ] バックエンドの実行結果として `backend/output/` または同期後の `frontend/content/` にJSONが正しく出力されているか確認する。

## 3. フロントエンドの UI / コンテンツ調整
現在のフロントエンドは「SEO検証用・連携用」のベースUIです。
- [ ] JSONデータから動的生成される Topic (`/topic/...`) や Language (`/language/...`) 画面のレンダリングが正しく行われているか確認する。
- [ ] `layout.tsx` やCSSで、サイト名 (`GitHub SEO`) やロゴ、テーマカラーを自分好みに調整する。
- [ ] Google Analytics または Google Search Console 用のタグ（メタタグ）を `next.config.ts` やルートレイアウトに追加する。

## 5. ホスティング環境へのデプロイ
Next.jsの Static Export 機能 (`next build` 時に `out/` フォルダへHTML出力) を利用して、無料でホスティングします。
- **推奨ホスティング**: Cloudflare Pages, Vercel, GitHub Pages など
- [ ] GitHub等にこのプロジェクトのリポジトリ（全体、またはfrontend部分のみでも可）をPushする。
- [ ] ホスティングサービス側で Build Command を `npm run build`、Output Directory を `out/` に設定してデプロイを実行する。
- [ ] 公開されたURLにアクセスし、ページ（特に `/repo/...` の動的生成ページ）が正しく表示されるか確認する。

## 6. 計測タグの導入 (Google Search Console / Analytics)
サイトのSEOパフォーマンスとユーザーアクセスを計測するための設定を行います。
- [ ] Googleアカウントを作成・用意し、Google Analytics (GA4) のプロパティを作成。測定ID(`G-XXXXXXXXXX`)を取得する。
- [ ] Next.jsの環境変数にGAのIDを設定し、`app/layout.tsx` など全ページ共通部分にgtagスクリプトを埋め込む。
- [ ] Google Search Console に独自ドメインを登録し、TXTレコード等で所有権の確認を完了する。
- [ ] 今後サイトマップ (`sitemap.xml`) をSearch Consoleに送信する準備をしておく。

## 7. 公開前チェックリスト (Pre-launch Checklist)
本番自動運用を開始する前の最終確認リストです。これをクリアしたら公開となります。
- [ ] [デザイン・UI] サイトのロゴ・メタ情報（DescriptionやOGP画像）が正しく設定されている。
- [ ] [インフラ] Cloudflare Pages プロジェクト（例: `github-seo-site`）をダッシュボードから作成しておく（自動ビルドの設定は行わず「アセットの直接アップロード」用として準備）。
- [ ] [自動化・Secrets] GitHub リポジトリの `Settings > Secrets and variables > Actions > Secrets` に以下を登録する。
  **【必須】**
  - `GITHUB_TOKEN`: GitHubのPersonal Access Token（Rate Limit回避用）
  - `CLOUDFLARE_API_TOKEN`: Cloudflare Pages へのデプロイ権限（Edit権限）を持つ API トークン
  - `CLOUDFLARE_ACCOUNT_ID`: Cloudflare のアカウント ID
  **【任意】**
  - `OPENAI_API_KEY`: OpenAIのAPIを利用する設定(`llm_generator.py`)にした場合のみ設定
- [ ] [自動化・Variables] GitHub リポジトリの `Settings > Secrets and variables > Actions > Variables` に以下を登録する。
  - `NEXT_PUBLIC_SITE_URL`: （例: `https://github-seo.example.com`）。SEO上のCanonical設定や Sitemap 生成に必須。
- [ ] [自動化・Workflow] `.github/workflows/generate-and-deploy.yml` 内の `npx wrangler@3` コマンドで指定されている `--project-name=github-seo-site` がCloudflare側と一致していることを確認する。
- [ ] [デプロイ完了] GitHub Actions から `Generate and Deploy` ワークフローを `workflow_dispatch`（手動実行）でトリガーし、WranglerのログがSuccessとなるか確認する。

## 8. 本番公開後チェックリスト (Post-launch Verification)
デプロイが完了した直後に、ブラウザを開いて手動で以下の項目を確認します（これがすべてOKなら本番公開成功です）。

- [ ] **Home**: トップページにアクセスし正しく画面・プレースホルダーが表示されるか。
- [ ] **Dynamic pages**: `/repo/...`, `/topic/...`, `/language/...` のURLをランダムにいくつか叩き、静的静的エクスポートされたHTMLが正しくルーティングされているか確認。
- [ ] **404 Routing**: 存在しないURLを叩き、Next.jsのカスタム404ページ（またはCloudflareのデフォルト404）が正しく返るか。
- [ ] **Sitemap**: `/sitemap.xml` にアクセスし、生成された全ページが `NEXT_PUBLIC_SITE_URL` ベースのフルURLでリストされているか。
- [ ] **Robots**: `/robots.txt` にアクセスし、sitemapの場所が正しく指し示されているか。
- [ ] **Metadata**: トップページのソースまたはDevToolsを開き、`<link rel="canonical">` が正しいURLを向いているか。
- [ ] **Noindex**: 品質チェック等で除外・noindexの判定を受けたコンテンツがある場合、そのページのソースに `<meta name="robots" content="noindex" />` が付与されているか（実装がある場合）。

## 9. 公開後30日運用計画 (Post-launch 30-day Plan)
公開直後〜1ヶ月間で注力すべきタスクのスケジュールです。

### Week 1: 監視と安定化・インデックス促進
- [ ] **Day 1**: Google Search Console に `sitemap.xml` を送信。
- [ ] **Day 2-3**: GitHub Actionsの定期実行（cron）が毎日正しくエラーなく回っているか、Actionsログを確認。生成失敗している場合はリトライ/修正。
- [ ] **Day 7**: Google Analytics にアクセスし、自身以外のトラフィック（Bot含む）が記録され始めているかダッシュボードで確認。

### Week 2-3: エラー対応と品質調整
- [ ] **Day 14**: Search Consoleの「カバレッジレポート」を確認。インデックス未登録になっているページの原因を探り（ソフト404やリダイレクトエラー等）、ソースコードを修正。
- [ ] 自動生成された記事をいくつか読み、LLMの出力品質（フォーマット崩れや内容の薄さ）をチェック。問題があれば `llm_generator.py` のプロンプトをチューニング。

### Week 4: サイトの拡張とマネタイズ準備
- [ ] **Day 25**: 検索クエリ（どんなキーワードで流入しているか）をSearch Consoleで分析。伸びているジャンルがあれば、それに沿ったリポジトリを自動収集のターゲット（Targetsリスト）に多めに追加する。
- [ ] **Day 30**: トラフィックが一定数入っていれば、Google AdSenseの「サイト」にドメインを追加し、審査を申し込む。プライバシーポリシーページ（広告掲載に必須）を作成しておくこと。
