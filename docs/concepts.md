# Minarai Concepts

Minaraiは、AIが人間と仕事をしながらExperienceを蓄積し、複数の時間スケールで継続的に学習することを基本方針とします。

## Experience

仕事中に発生した、

```text
Situation → Action → Result → Evaluation → Human Feedback
```

をExperienceとして保存します。

ExperienceはすぐにRuleへ変換しません。

また、`testing`、`design`、`debugging`のような意味カテゴリを人間が事前に与えることを前提としません。Experience同士の関係や抽象化は、可能な限りAI側で形成します。

## Learning

Minaraiでは、学習速度の異なる複数の層を持つことを基本仮説とします。

```text
Experience
    ↓
Fast Neural Memory
    ↓
繰り返し有効な経験
    ↓
Consolidation
    ↓
Slow Memory / Project Adapter
```

### Fast Neural Memory

新しいExperienceから高速に学習する領域です。

人間からの指摘や予想外の結果を、次の類似した仕事へすぐ反映することを目指します。

### Slow Learning

繰り返し有効であることが確認されたExperienceを、より長期的な能力へ定着させます。

一度の例外的なExperienceによってAI全体の振る舞いが変化することを避けます。

この考え方はTitans、MIRAS、Nested Learningなどの研究を参考にします。

具体的なMemory構造、更新則、Adapter方式は実装と実験を通して決定します。

## Learned Capability

学習によってAI内部に形成された能力です。

例えば、

* 過去の失敗に似た状況へ気付く
* 必要な確認観点を考える
* 経験を適切に一般化する
* 関係のない状況では過去の経験を使わない

などです。

Learned Capabilityは、人間が大量の手順として記述することを前提としません。

## Project Knowledge

人間とAIが明示的に共有すべき情報です。

例えば、

* 要件
* 設計
* 仕様
* プロジェクト標準
* Workflow
* ライブラリ仕様
* 現在のプロジェクト状態

などです。

これらはAI内部のMemoryだけに依存させません。

## Project Standard

プロジェクトとして明示的に決定されたルールです。

AIがExperienceから仕事を学ぶことと、Project Standardが変更されることは別です。

> AIが賢くなることと、プロジェクトのルールが変わることを分離する。

## Evidence

AIの仕事を人間が確認するために残す情報です。

例えば、

* Test Result
* Diff
* Traceability
* Decision
* Risk

などです。

AI内部のすべての推論を残すのではなく、人間との協業や品質保証に必要な情報を残します。

## Private / Public Experience

Private Experienceは利用者のローカル環境に保存します。

Public Experienceは、共有可能と判断されたExperienceのみをRepositoryで管理します。

Experienceを長期的な資産とし、Neural MemoryやAdapterはそこから生成される学習状態として扱います。

## Foundation Model

Foundation Modelは一般能力を提供します。

MinaraiではFoundation Modelを毎回大きく更新するのではなく、まずFast Neural MemoryやProject-levelの学習層を更新する構成を基本とします。

Foundation Model自体は将来より良いモデルへ交換できることを前提とします。

## Principles

1. Experienceを学習の基本単位とする
2. ExperienceをすぐにRuleへ変換しない
3. Experienceの意味構造を人間が先に固定しない
4. 高速学習と低速学習を分離する
5. 一度のExperienceで長期能力を過度に変更しない
6. Project StandardとLearned Capabilityを分離する
7. AI内部の学習と、人間との共有情報を分離する
8. Experienceを長期資産として扱う
9. Foundation Modelは交換可能とする
10. AIが上手になるためのHowを必要以上に固定しない
