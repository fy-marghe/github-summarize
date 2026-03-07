# GitHub Repository SEO Site - コンテンツ生成品質・評価基盤仕様書

## 1. 目的と課題
本サイト（GitHub Repository SEO Site）が検索エンジンから「低品質」「重複（Thin Content）」とみなされるリスクを防ぐため、Quality Checker（品質評価基盤）を定義・実装する。
高品質で独自性のあるページのみをインデックスさせ、低品質なページは再生成・破棄・またはNoIndexとなる仕組みを構築する。

**主な課題と解決策**:
- **薄いページを防ぐ**: 最小文字数の厳格なチェック。
- **READMEの焼き直しを防ぐ**: READMEとの類似度測定（高すぎても低すぎてもNG）。
- **一般論ばかりのページを防ぐ**: リポジトリ特有の固有語・アーキテクチャ・依存ライブラリ名の出現率を測定。
- **重複ページ量産を防ぐ**: Title/Meta Description、およびサイト内他ページとの本文類似度によるカニバリゼーション制御。
- **noindex判定を妥当化する**: スコア（0〜100）ベースでの明確な線引き。

---

## 2. 品質評価指標とチェック項目定義 (仕様)

これらのチェックは、LLMによって生成された記事（HTML化前、またはプレーンテキスト抽出後）に対して実行される。

### 2.1. 基礎品質 (Basic Quality)
*   **最小文字数 (Minimum Character Count)**
    *   **定義**: 記事本文（コードブロックやHTMLタグを除外）の純粋なテキスト文字数。
    *   **実装粒度**: `strip_tags()` 後に `length` を取得。
    *   **閾値**: 1500文字以上を推奨。800文字未満は減点大。
*   **セクション欠落 (Missing Sections)**
    *   **定義**: 記事内に必須の見出し（LLMプロンプトで指定した構成）が含まれているか。
    *   **実装粒度**: 必須構成のキーワード（「概要と主な特徴」「背景と文脈」「内部アーキテクチャ」「代替ツール」「ユースケース」「まとめ」など）が本文や見出しに含まれるかを部分一致で抽出。
    *   **閾値**: 必須セクションが2つ以上欠落している場合はマイナス評価。
*   **内部リンク有無 (Internal Links Presence)**
    *   **定義**: サイト内の他の関連リポジトリ・タグページへのリンク (`<a>`タグや markdown `[]()`) が存在するか。
    *   **実装粒度**: href属性に自サイトのドメイン（または相対パス）が含まれるリンク数をカウント。
    *   **閾値**: SEO上の重要性が高いため、0件は `-10`、1件は `0`（基準）、2件以上で `+5` のスコア調整を行う。

### 2.2. 独自性・付加価値 (Originality & Value-Add)
*   **README類似率 (README Similarity Score)**
    *   **定義**: 元リポジトリのREADME（プレーンテキスト）と生成記事本文の類似度。
    *   **実装粒度**: N-gramベース（例: Trigram）のJaccard係数、または軽量なレーベンシュタイン距離による一致率。
    *   **閾値**:
        *   **80%超え**: 「ただの翻訳・コピペ（焼き直し）」として強い減点。
        *   **50%〜80%**: 「直訳寄り」として軽い減点。
        *   **10%〜50%**: 「適正な整理・文脈化」がされているとしてOK（減点なし）。
        *   **10%未満**: 「ハルシネーション」の疑いとして強い減点。
*   **Repo固有語出現率 (Repo-Specific Term Frequency)**
    *   **定義**: READMEに含まれる特徴的な名詞（リポジトリ名自身、独自概念、機能名など）が生成記事にどれくらい含まれているか。
    *   **実装粒度**: README側からTF-IDFまたは正規表現で固有名詞を抽出し、生成記事内での出現回数(TF)をチェック。
    *   **閾値**: 全く出現しない場合は「一般論だけの薄い記事」として減点。
*   **主要ファイル名/依存ライブラリ名出現率 (Code & Dependency Extracted Context)**
    *   **定義**: GitHub APIから取得した言語情報(`languages.json`)や、`package.json`/`requirements.txt` の依存ライブラリ名が記事内に言及されているか。
    *   **実装粒度**: リポジトリの主な依存関係配列（例: `['react', 'axios', 'express']`）と記事のテキストを突合。
    *   **閾値**: 依存ライブラリの言及が1〜2個以上あれば加点（技術的深みがあると見なす）。

### 2.3. 重複・カニバリゼーション防止 (Duplication & Cannibalization)
*   **Title / Meta Description重複 (Title/Meta Duplication)**
    *   **定義**: データベースに登録済みの他の既存ページとTitleやMeta Descriptionが完全一致（または高類似度）していないか。
    *   **実装粒度**: SQL/DB内での完全一致検索、またはTri-gramインデックス検索。
    *   **閾値**: 一致した場合は重大エラー（Duplicate）。
*   **本文類似率 (Body Content Duplication)**
    *   **定義**: 生成された記事が、既にある他の記事と似すぎていないか（ボイラープレート化による低品質化）を2段階で評価する。
    *   **実装粒度**: MinHash や LSH (Locality-Sensitive Hashing) 、ベクトル検索を用いたドキュメント間類似度計算。
    *   **閾値**:
        1.  **同一Topic内**: 競合しやすいため厳しく判定（例: 類似度70%を超える場合は重複・ペナルティ）。
        2.  **全Repo**: サイト全体のボイラープレート化を防ぐ（例: 類似度80%を超える場合は重複・ペナルティ）。
*   **Topic妥当性 (Topic Alignment)**
    *   **定義**: そのリポジトリに付与されたトピック（タグ）が、当サイトが注力すべきTopic群と一致しているか。
    *   **実装粒度**: 生成されたTopicリストと、サイト運営用のマスターTopicリストの照合。異常な（検索ボリューム皆無の）Topicが生成されたら修正。

---

## 3. quality_score 算出ルールと Index 制御

全体の `quality_score` を 100点満点 で算出し、減点方式と加点方式を組み合わせる。

### スコア算出式
`BaseScore` (初期100点)
**加点要素 (Max +15):**
- 依存ライブラリへの具体的な言及あり: +10
- 内部リンクが2件以上: +5

**減点要素スコア (Penalty):**
- **内部リンク**:
  - 0件: -10
- **文字数不足**:
  - 800字未満: -50 (致命的)
  - 800〜1499字: -20
- **README類似度**:
  - > 80% (コピー・焼き直し): -40 (強い減点)
  - 50%〜80% (直訳寄り): -15 (軽い減点)
  - 10%〜50%: 0 (適正な文脈化・まとめでOK)
  - < 10% (ハルシネーション疑惑): -30
- **重複設定**:
  - Title/Meta重複: -50 (致命的)
  - 本文類似度高（同一Topic内で>70%、または全Repoで>80%）: -40
- **構成不備**:
  - 必須セクション欠落: 欠落1つにつき -15
  - Repo固有語・依存ライブラリの言及が皆無: -20

`Final Score` = `BaseScore` + `加点` - `Penalty` (※最小0点、最大100点として丸める)

### Index / NoIndex / Skip ルール
この算出したスコアに基づき、生成ページの状態を決定する。

| Score Range | 判定ステータス | アクションと運用理由 |
| :--- | :--- | :--- |
| **80 〜 100** | `INDEX` (🟢 High Quality) | SEOに貢献する独自コンテンツ。Sitemapに登録し、通常通り公開。 |
| **50 〜 79** | `NOINDEX` (🟡 Mediocre) | 要約にとどまる、または少し薄いページ。ユーザーの回遊用（UX上）には公開するが、`noindex, follow`を付与し、Googleのサイト全体評価が下がるのを防ぐ。将来的には再生成対象。 |
| **0 〜 49** | `ERROR / SKIP` (🔴 Low Quality) | 本文量不足や重複など使い物にならないゴミページ。DBには原則保存せず、**対象リポジトリまたはTopicを「要再生成キュー」に戻すか、処理をスキップ**する。 |

---

## 4. LLM Prompt 改善案

READMEの翻訳に留まってしまう現行課題を解決し、「技術的な整理・文脈化・類似ツールとの比較」を出力させる。

```text
あなたは世界の最新OSS（GitHubリポジトリ）を技術者向けに分かりやすく解説する、シニアエンジニア兼テクニカルライターです。
与えられたリポジトリ情報（README、言語、依存ライブラリ）を【単に要約・直訳するのではなく】、以下の要件を満たし「整理・文脈化・比較」を行い、技術者が「なぜ・いつこれを使うべきか」が分かる詳細な記事を生成してください。

【厳守事項】
1. 一般論やポエム、不要な挨拶を排除し、技術的な具体性（アーキテクチャ、使用されている依存関係、具体的なユースケース）に焦点を当てること。
2. 対象リポジトリを「既存の類似技術や代替ツール」と比較して、強みと弱み、使い分けのポイントを独自に考察して記述すること。
3. 提供された「依存ライブラリ一覧」や「使用言語」の情報（例：React, Tailwind, Rust等）を読み解き、READMEには書かれていない『技術スタックや実装面での特徴』を推測・補完すること。
4. 単なるREADMEのコピペ・翻訳は固く禁じます。あなたの言葉で構造化し直してください。

【出力要件（必須セクション構成）】
出力は以下のMarkdown構造に必ず従うこと（これ以外の見出し名にしないこと）：
# {リポジトリ名}とは？概要と主な特徴
## どのような課題を解決するのか（背景と文脈）
## 技術スタックと内部アーキテクチャ（依存ライブラリからの考察）
## 代替ツール・競合との比較（例: 既存のXと比較して何が優れているか）
## 具体的なユースケースと導入のメリット
## 技術的なまとめと評価

【入力データ】
- リポジトリ名: {repo_name}
- 主要言語・関連技術: {languages}
- 依存ライブラリ(package.json等): {dependencies}
- README本文(抜粋): {readme_content}
```

---

## 5. チェックの実装案・疑似コード (Python例)

生成された記事を評価し、`quality_check_report.json` 用のデータを返す評価器の関数イメージ。

```python
import re

def calculate_quality_score(generated_content, repo_data, analysis_db):
    score = 100
    report = { "metrics": {}, "flags": {}, "warnings": [] }

    # 1. 最小文字数チェック（プレーンテキスト化後）
    text_body = strip_markdown_and_html(generated_content["body"])
    length = len(text_body)
    report["metrics"]["content_length"] = length
    if length < 800:
        score -= 50
        report["warnings"].append("文字数が極端に不足しています(800字未満)。")
    elif length < 1500:
        score -= 20
        
    # 2. 内部リンク評価
    internal_links_count = count_internal_links(generated_content["body"])
    report["metrics"]["internal_links_count"] = internal_links_count
    if internal_links_count == 0:
        score -= 10
        report["warnings"].append("内部リンクが存在しません。SEO観点でマイナスです。")
    elif internal_links_count >= 2:
        score += 5
    
    # 3. 重複チェック (Title & 本文類似度 - 2段階)
    if generated_content["title"] in analysis_db["existing_titles"]:
        score -= 50
        report["flags"]["is_title_duplicate"] = True
    else:
        report["flags"]["is_title_duplicate"] = False

    max_sim_same_topic = get_max_similarity(text_body, analysis_db["same_topic_bodies"])
    max_sim_all_repos = get_max_similarity(text_body, analysis_db["all_repo_bodies"])
    
    if max_sim_same_topic > 0.70:
        score -= 40
        report["warnings"].append("同一Topic内に非常に類似した記事が存在します(>70%)。")
    elif max_sim_all_repos > 0.80:
        score -= 40
        report["warnings"].append("サイト内の他の記事と非常に類似しています(>80%)。")

    # 4. README類似率
    similarity = jaccard_similarity(text_body, repo_data["readme_text"])
    report["metrics"]["readme_similarity"] = similarity
    if similarity > 0.80:
        score -= 40
        report["warnings"].append("READMEとの類似度が高く、コピペ・焼き直しの疑いがあります(>80%)。")
    elif similarity >= 0.50:
        score -= 15
        report["warnings"].append("READMEの直訳になっている可能性があります(50%〜80%)。")
    elif similarity < 0.10:
        score -= 30
        report["warnings"].append("READMEの内容がほとんど反映されていません(ハルシネーション疑惑、<10%)。")

    # 5. 依存ライブラリや技術の言及チェック
    tech_stack = repo_data.get("dependencies", []) + repo_data.get("languages", [])
    mentioned_techs = [tech for tech in tech_stack if tech.lower() in text_body.lower()]
    report["metrics"]["dependencies_mentioned"] = mentioned_techs
    if len(tech_stack) > 0:
        if len(mentioned_techs) == 0:
            score -= 20
            report["warnings"].append("技術スタック（依存ライブラリ）への言及が皆無です。")
        elif len(mentioned_techs) >= 2:
            score += 10 # 加点

    # 6. セクション欠落チェック (プロンプトの必須見出しと整合)
    required_sections = [
        "概要と主な特徴",
        "背景と文脈",
        "技術スタックと内部アーキテクチャ",
        "代替ツール・競合との比較",
        "具体的なユースケース",
        "技術的なまとめと評価"
    ]
    missing = [sec for sec in required_sections if sec not in generated_content["body"]]
    if len(missing) >= 2:
        score -= (len(missing) * 15)
        report["flags"]["missing_sections"] = missing

    # 最終判定
    final_score = max(0, min(100, score))
    report["quality_score"] = final_score
    
    if final_score >= 80:
        report["action"] = "INDEX"
    elif final_score >= 50:
        report["action"] = "NOINDEX"
    else:
        report["action"] = "SKIP_AND_REGENERATE"

    return report
```

---

## 6. サンプル `quality_check_report.json`

このJSON出力は、生成プロセスの中でログとして保存し、後日問題のある記事を特定・再生成するためのデータソースとして利用する。

```json
{
  "repo_name": "facebook/react",
  "generation_id": "gen_20260308_002",
  "timestamp": "2026-03-08T02:40:00Z",
  "quality_score": 75,
  "action": "NOINDEX",
  "metrics": {
    "content_length": 1600,
    "readme_similarity": 0.65,
    "internal_links_count": 0,
    "dependencies_mentioned": [
      "schedule",
      "loose-envify"
    ]
  },
  "flags": {
    "is_title_duplicate": false,
    "missing_sections": ["代替ツール・競合との比較", "具体的なユースケース"]
  },
  "warnings": [
    "内部リンクが存在しません。SEO観点でマイナスです。",
    "READMEの直訳になっている可能性があります(50%〜80%)。"
  ]
}
```

---

## 7. 実装チームへ渡す変更タスク (再生成が必要なページの抽出ルール含む)

この仕様をもとに、以下のチケット（Issue）を起票し開発・運用に乗せる。

### [Ticket 1] Quality Checker 基盤関数の実装
- **内容**: Python または TypeScript で `calculate_quality_score` 関数を実装・単体テスト作成。
- **入力**: LLMの出力結果(Title, Meta, Body), 対象Repoのメタデータ(README文字, Dependency等)
- **出力**: 本仕様に沿った `quality_check_report.json` フォーマットでの結果。

### [Ticket 2] LLM生成パイプラインへのQuality Checker組み込みと再生成ロジック
- **内容**: 記事生成バッチの中で Checker を走らせる。
- **ロジック**: 
  - `action == 'INDEX'` → DBに`status='published', robots='index'`で保存。
  - `action == 'NOINDEX'` → DBに`status='published', robots='noindex'`で保存。
  - `action == 'SKIP_AND_REGENERATE'` → 今回は保存せず、最大2回まで別プロンプト（または上位LLMモデル）で再生成をリトライする。それでも駄目ならDBに`status='error'`で保存しスキップ。

### [Ticket 3] 新規プロンプトの適用と評価用データの挿入
- **内容**: 第4項の「改善版プロンプトテンプレート」を適用。
- **改修点**: GitHub APIから取得した `dependencies` や `languages` をプロンプト変数としてLLMに渡せるよう前処理を実装する。

### [Ticket 4] 既存ページの品質一斉チェックと再生成（バッチ運用ルール）
- **内容**: 現在DBに保存されているMVP時代の既存記事に対して、Quality Checkerをバッチ実行し、スコアを再評価するスクリプトを作成。
- **再生成が必要なページの抽出ルール（SQL等）**:
  1. `score < 50` と判定された既存ページ（＝即刻削除または下書き化）
  2. `score >= 50 AND score < 80` のページ群（= `noindex` に変更しつつ、順次再生成キューへ送る）
  3. `content_length < 1000` などの単純な閾値で絞り込んだ後、アクセス数(GA4等)が0のものを優先して再生成対象とする。
- **副次タスク**: 上記で抽出されたページのURLリストをエクスポートし、新しいパイプラインで定期的に上書き生成を行う機能を追加。
