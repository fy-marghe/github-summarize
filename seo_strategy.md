# GitHub SEO Site - SEO Strategy & Information Architecture

## 1. 現在のページ構造のレビューとSEO上の弱点

現在のフロントエンド（MVP）実装（`app/page.tsx`, `app/layout.tsx`, `app/repo/[owner]/[repo]/page.tsx`, index系ページ）をレビューした結果、以下の課題（弱点）が確認されました。

1. **Top, Topic, Languageページの静的・薄いコンテンツ化**
   - 現在の `topic/page.tsx` や `language/page.tsx` はプレースホルダーのリストがハードコードされており、Hub（ハブ）ページとしての情報量が極めて薄いです。
   - このままだと「薄いコンテンツ（Thin Content）」として評価されず、 टॉपिकや言語系のミドルキーワードでの流入が獲得できません。
2. **内部リンク（回遊構造）の欠如と孤立ページの発生**
   - Repoページの下部に `Related Topics` のリンクがありますが、Topicページ側から関連Repoへのリンク網が自動生成される仕組み（Paginationやカテゴリ別Sort）がMVPには欠けています。
   - クローラーが特定のマイナーなRepoページに到達するための経路（クロールパス）が不足しています。
3. **動的なTitle / Descriptionのフォールバックの甘さ**
   - `layout.tsx` のデフォルトDescriptionが固定（"Understand any GitHub repository in minutes..."）です。
   - `repo/.../page.tsx` でデータが無い・取得失敗時のメタデータフォールバックや、Topic/Languageページにおける動的Title/Descriptionの生成ロジックが不足しています。
4. **パンくずリスト（Breadcrumbs）の構造化データ（JSON-LD）未対応**
   - UI上は `Topic › [Topic Name]` と表示されていますが、Schema.orgの `BreadcrumbList` としてGoogleに伝達されていません。
5. **Comparison（比較）や Tutorialへの導線設計の不在**
   - 将来的に機能拡張する余地（ナビゲーションやRepoページからの「〇〇と比較する」というリンク枠）が現状のレイアウトに存在しません。

---

## 2. 内部リンク最適化ルール (Repo / Topic / Language)

「サイト内リンクジュースをいかにHub（Topic/Language）とSpoke（Repo）に循環させるか」が重要です。

- **Topic / Language ページ (Hub)**
  - トップページから全Topic / Languageへのインデックスページへリンク（既にMVPで実装予定）。
  - 各Topic / Languageページには、紐づく **Top Repositories (Star数順で上位20件程度)** をリスト表示。
  - さらに「Recently Updated (最近更新されたリポジトリ)」枠を作り、クローラーに新規ページを素早く認識させる。
- **Repo ページ (Spoke)**
  - パンくずリスト: `Home > Topic > [Primary Topic] > [Owner]/[Repo]`
  - パンくずリスト: `Home > Language > [Primary Language] > [Owner]/[Repo]`
  - `Related Topics`: 該当リポジトリが持つサブTopicタグへのリンク。
  - `Similar Repositories`: 同じPrimary Topicを持ち、特徴ベクトルの近い（または単にStar数が近い）リポジトリ3〜5件へのリンクを設置（非常に重要）。これによりRepo間の横移動を促す。
- **将来の Comparison ページへのリンク**
  - Repoページのサイドバーまたはコンテンツ直下に `Compare [Repo A] with...` という枠を設け、似たリポジトリ（同TopicのTop3など）との比較ページへのリンクを張る。

---

## 3. Page Templates & Information Architecture

| ページ種別 | タグ | テンプレート |
| :--- | :--- | :--- |
| **Repo** | Title | `{Owner}/{Repo} Review & Architecture - {Primary_Topic} \| GitHub SEO` |
| | Desc | Read our AI-generated explanation, architecture overview, and usage guide for {repo} by {owner}. A popular {primary_language} repository for {primary_topic}. |
| | H1 | `{Owner}/{Repo}` |
| | H2 | What it does, Key Features, Architecture Overview, How to run, Important Files, Related Topics |
| **Topic** | Title | `Top {Topic_Name} GitHub Repositories & Tools \| GitHub SEO` |
| | Desc | Explore the best {Topic_Name} open source projects on GitHub. Compare features, architectures, and get started with top-rated repositories. |
| | H1 | `Top {Topic_Name} Open Source Repositories` |
| | H2 | What is {Topic_Name}?, Top Repositories, Recently Added, Related Topics |
| **Language** | Title | `Best {Language} GitHub Repositories & Open Source Projects \| GitHub SEO` |
| | Desc | Discover trending and most starred {language} open source frameworks, libraries, and tools on GitHub. |
| | H1 | `Best {Language} Repositories` |
| | H2 | Top {Language} Frameworks, New {Language} Projects, Popular Topics |

---

## 4. Sitemap Priority & Update Frequency 方針

| URL Type | Priority | Changefreq | 対象ページ例 |
| :--- | :--- | :--- | :--- |
| **Topic** | `0.9` | `daily` | `/topic/llm-framework` (List updates frequently) |
| **Language**| `0.8` | `daily` | `/language/python` (List updates frequently) |
| **Repo** | `0.6` | `weekly` | `/repo/langchain-ai/langchain` (Static content, rarely changes) |
| Top | `1.0` | `daily` | `/` |

---

## 5 & 6. 情報設計 (IA) テンプレート

Hubページおよび将来の拡張ページが検索意図（Search Intent）を満たせるよう、独自のコンテンツ（AIによるサマリなど）を持たせます。

### 5.1. Topic ページ (IA テンプレート)
Topicページは単なるリストではなく「その分野のガイド」となるべきです。
* **H1:** Top [Topic_Name] Open Source Repositories
* **概要セクション (AI生成):** そのTopic（例: Vector Database）が何であるか、現在のトレンドは何かを200〜300文字で解説。
* **トップリポジトリ (List):** Star数順上位10件（Title, 1行サマリ, Star数, 言語）。
* **比較への導線 (将来):** "Compare Top [Topic] Tools (e.g., Milvus vs Qdrant)"
* **最新追加セクション:** サイトに最近追加された同TopicのRepo。

### 5.2. Language ページ (IA テンプレート)
* **H1:** Best [Language] Repositories
* **概要セクション:** その言語の主要なユースケース（例: Python=AI/Data, Rust=Systems）の解説。
* **カテゴリ(Topic)別リスト:** その言語で人気のあるTopicごとのTop 3リポジトリ（例: Python > Web Frameworks, Python > LLM tools）。
* **トップリポジトリ (List):** 言語全体でのStar数順リスト。

### 5.3. Comparison ページ (将来IA)
* **URL:** `/compare/[repo-a]-vs-[repo-b]`
* **H1:** `[Repo A] vs [Repo B]: Which [Topic] tool is better?`
* **TL;DR (AI生成):** 結論。どちらをどういうケースで使うべきか。
* **Feature Comparison (表):** 言語、ライセンス、Star数、サポートOS・環境、主な機能の有無などをテーブル比較。
* **Architecture Difference:** それぞれのアーキテクチャの思想の違い。
* **Performance / Search Trends:** (可能なら) トレンドの比較。

### 5.4. Tutorial ページ (将来IA)
* **URL:** `/tutorial/[repo]`
* **H1:** `How to build a [App Type] using [Repo]`
* **Prerequisites:** 必要な環境（Node, Pythonなど）。
* **Step-by-Step Guide:** コードブロックを用いた環境構築〜Hello Worldまでの実践ガイド。
* **Common Errors & Troubleshooting:** よくあるエラーの解決法（StackOverflow等からAIが要約）。

---

## 7. 初期Topic拡張案 (全42トピック)

SEO拡張を視野に入れ、初期のAI/ML領域からDevTools、Web領域まで網羅的にカバーします。

**AI & ML Core**
1. `machine-learning`
2. `deep-learning`
3. `computer-vision`
4. `nlp` (Natural Language Processing)
5. `diffusion-models`

**LLM & Generative AI**
6. `llm-framework` (LangChain, LlamaIndex)
7. `llm-tools`
8. `local-llm` (Ollama, llama.cpp)
9. `prompt-engineering`
10. `fine-tuning` (PEFT, Unsloth)
11. `rag` (Retrieval-Augmented Generation)

**AI Agents & Autonomous**
12. `ai-agents`
13. `autonomous-agents`
14. `multi-agent-systems`

**Data Engineering & Vector DBs**
15. `data-engineering`
16. `vector-database` (Milvus, Qdrant)
17. `etl` (Extract, Transform, Load)
18. `data-pipeline`
19. `orchestration` (Airflow, Prefect)

**MLOps**
20. `mlops`
21. `model-serving`
22. `experiment-tracking`

**Web Frameworks**
23. `frontend-framework` (React, Next.js, Vue)
24. `backend-framework` (FastAPI, NestJS, Gin)
25. `full-stack`
26. `static-site-generator`

**Databases & ORMs**
27. `database` (PostgreSQL, MySQL tools)
28. `orm` (Prisma, Drizzle, SQLAlchemy)
29. `caching` (Redis)

**DevTools & Infrastructure**
30. `devtools`
31. `cli-tools`
32. `terminal`
33. `devops`
34. `infrastructure-as-code` (Terraform, Pulumi)
35. `ci-cd` (GitHub Actions, ArgoCD)
36. `observability`

**Security & Auth**
37. `authentication` (NextAuth, Supabase)
38. `security-tools`

**Web3 & Others**
39. `web3`
40. `smart-contracts`
41. `state-management`
42. `headless-cms`

---

## 8. 初期repo収集条件 (2段階構造)

インデックス品質を保ちつつ、初期データボリュームを確保するための2段階（Tier）運用とします。

**Tier 1（高品質・シード層）**
- **Stars**: `> 5,000`
- 条件: 知名度が高く、確実に検索ボリュームがあり質の高い解説が生成できるリポジトリ。まずはここから優先的に処理する。

**Tier 2（準高品質・ロングテール層）**
- **Stars**: `> 1,000`
- **README有無**: 必須（情報量確保のため）
- **Last Update**: `< 2 years` (過去2年以内に更新あり)
- 条件: トピック特化型（Vector DBやLLM Tool等）で、ニッチだが一定のシェアと品質（Star 1000〜5000層）を持つアクティブなリポジトリ。

*※ 対象言語は Python, TypeScript, JavaScript, Rust, Go, C/C++ を中心に行う。*

---

## 9. Search Console / Analytics KPI 設計

初期フェーズで追うべき指標。

- **Google Search Console**:
  - `インデックス作成されたページ数`: 生成した/repoページが正しくインデックスされているか（Hubページの強さが試される）。
  - `表示回数 (Impressions)`: まずはクリックよりもインデックスと表示回数の伸びを追う。ターゲットTopic名や "repo architectue" 等で表示されるか。
  - `CTR (Click Through Rate)`: Title/Descriptionテンプレートが魅力的かどうかの検証。
- **Google Analytics (GA4)**:
  - `セッションあたりのページビュー (Pages / Session)`: > 1.5 を目標。RepoページからTopicページへ、または Similar Repoへの回遊（内部リンク）が機能しているか。
  - `エンゲージメント時間`: ユーザーがAI生成の「Architecture Overview」を実際に読んでいるか（直帰していないか）。

---

## 10. 実装チームへ渡すべき具体タスク (Next Steps)

フロントエンドおよびバックエンドへの改修タスクリストです。

1. **Frontend: SEO Metaタグの動的化**
   - `app/repo/[owner]/[repo]/page.tsx` の `generateMetadata` で、設計したTitle/Descriptionテンプレートを適用する。
2. **Frontend: JSON-LD (構造化データ) の追加**
   - パンくずリスト(`BreadcrumbList`)と、Repoページ用の `SoftwareSourceCode` または `Article` スキーマを `<script type="application/ld+json">` で追加する。
3. **Frontend: Hubページの強化**
   - `Topic` および `Language` ページで、ハードコードを撤廃し、ビルド時にトップRepoリスト（とAI生成のカテゴリ概要）を描画するように変更する。
4. **Frontend: Repoページの内部リンク強化**
   - Repoページの下部に `Similar Repositories` コンポーネントを追加する。（バックエンド側で同じTopicを持つRepoを数件ピックアップしてJSONに含める改修が必要）。
5. **Backend: バッチ取得ロジックの改善**
   - `stars:>5000 pushed:>2023-01-01 topic:rag` のようなGitHub APIのSearchクエリを構築し、初期収集条件に合致するリポジトリのみを自動フェッチする仕組みを作る。
6. **Frontend: Sitemap自動生成**
   - `next-sitemap` を導入し、設計したPriorityとChangefreqに従って分割サイトマップを生成・出力する。
