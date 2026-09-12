# Minarai

Minaraiは、**人間と一緒に仕事をしながら、経験から継続的に学び、徐々に仕事が上手くなるAI**を作るプロジェクトです。

現在のAIエージェントは、プロジェクト固有の知識や仕事のやり方をPromptやSkillとして人間が記述することで適応させることが多くあります。

しかし、仕事を続けるほどルールが増え、重複や矛盾が発生し、メンテナンスも難しくなります。

Minaraiでは、人間がすべての仕事のやり方を事前に記述するのではなく、

```text
仕事
 ↓
結果
 ↓
評価・人間からのフィードバック
 ↓
Experience
 ↓
学習
 ↓
次の仕事
```

という循環によって、AI自身がプロジェクトに適応していく仕組みを目指します。

一方で、要件・設計書・プロジェクト標準・テストケース・レビュー証跡など、人間とAIが明示的に共有すべき情報は外部に残します。

長期的には、

> 「Aをして、次にBをして、Cを確認してください」

ではなく、

> 「この目的を達成してください。この制約は守ってください。」

という、人間のチームメンバーに近い形で仕事を依頼できる状態を目指します。

## Repository

```text
minarai/
├── experience/
│   ├── public/
│   └── schema/
├── artifacts/
│   ├── examples/
│   └── schema/
├── reviews/
├── src/
├── viewer/
├── docs/
├── README.md
└── AGENTS.md
```

Minaraiは現在、初期開発段階です。

設計上の主要な考え方は `docs/concepts.md` にまとめます。

## Artifact Review (MVP)

設計書やテストケースなどをYAML Artifactとして記述し、ブラウザでレビューしながら人間がコメントを残すための最小限の機能です。

```text
YAML Artifact (Source of Truth)
  ↓
HTMLへ変換（人間向けの派生View）
  ↓
ブラウザで表示・各Sectionへコメント
  ↓
Review Feedback として reviews/ に保存
  ↓
AIが後からコメントを読み取って修正可能
```

セットアップ:

```bash
pip install -e .
```

Artifactをレビューする:

```bash
minarai review artifacts/examples/sample-design.yaml
```

ブラウザで `http://localhost:8000` を開くと、Artifactが表示され、各Sectionへコメントを追加できます。コメントは `reviews/<artifact_id>.yaml` に保存されます。

AI/CLIからコメントを確認する:

```bash
minarai review list artifacts/examples/sample-design.yaml
minarai review list artifacts/examples/sample-design.yaml --json
```

コメントのStatusを更新する（`open` / `addressed` / `resolved`）:

```bash
minarai review update review-001 --status addressed
```

Artifact YAMLがSchemaに従っているか検証する:

```bash
minarai artifact validate artifacts/examples/sample-design.yaml
```

HTMLはYAMLから常に再生成される派生Viewであり、HTMLを直接編集してArtifactを更新する仕組みはありません。
