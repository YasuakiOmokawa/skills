---
name: translate-to-vision-story
description: プロジェクト活動 (commits/PRs/README/ADR) を `~/.claude/skills-config/vision.md` のビジョン要素と照合し、対話型 draft → revise loop で Zenn 記事下書きを生成する。プロジェクト単位の物語化・キャリアブランディング・月次記事執筆時に使用。
---

# translate-to-vision-story

**プロジェクト単位の活動を、ビジョン整合した Zenn 記事下書きに翻訳する。**

## 何を解決するか

プロジェクトでやったこと (taimei-auth, freee-mcp, ID統合設計など) を、自分のビジョンに繋がる物語として記事化したい。しかし「何をどう書けばビジョンと整合するか」を毎回ゼロから考えるのは負担で、結果としてふりかえりが「単なる技術深掘り」で終わり、ブランディングに繋がらない。

このスキルは、`~/.claude/skills-config/vision.md` に書かれたビジョン要素と照合しながら、5 ステップの対話フローで Zenn 記事下書きを生成する。

## 入出力

- **入力**: プロジェクトディレクトリのパス (例: `~/mydev/taimei`)
- **出力**: Zenn 記事下書き Markdown ファイル (デフォルト: `<project-path>/docs/draft/YYYY-MM-DD-<title>.md`)

## 前提

- `~/.claude/skills-config/vision.md` が存在すること
  - 存在しない場合は `references/vision-config-template.md` をコピーして編集を促す

## 5 ステップ対話フロー

### Step 1: 文脈把握

#### 入力受け取り

ユーザーが `/translate-to-vision-story <project-path>` または「物語化したい」と発話したら起動する。`<project-path>` を引数または対話で受け取る。

#### 必須読み込み

1. `~/.claude/skills-config/vision.md` を Read
   - 存在しなければ `${CLAUDE_PLUGIN_ROOT}/skills/translate-to-vision-story/references/vision-config-template.md` をコピーする旨をユーザーに提案、ユーザー承認後にコピー、編集を促してから skill を再実行
2. `<project-path>/README.md` を Read (存在すれば)
3. `<project-path>` の `git log --oneline -50` で直近 50 コミットを取得
4. `<project-path>` の `gh pr list --state merged --limit 30` で直近 30 PR を取得 (gh が利用可能な場合)
5. `<project-path>/docs/adr/` または親ディレクトリの ADR ファイルを Glob で探索

#### 「肝 3 点」初期提案

収集した情報から、AI が「このプロジェクトの肝はこの 3 点」を初期提案する。形式:

```
このプロジェクトの肝は以下の 3 点と推定しました:

1. **(技術的判断 1)** — (1-2 行の説明)
   - 関連活動: (commit hash / PR# / ADR-N 等)
   - 推定整合ビジョン要素: V_x

2. **(技術的判断 2)** — ...
3. **(技術的判断 3)** — ...

この 3 点で物語化を進めて良いですか? 違うなら指摘してください。
```

→ Step 2 (柱確認) へ。

### Step 2: 物語の柱の確認 (=最重要)

#### ユーザー応答パターン

| ユーザー応答 | 動作 |
|---|---|
| 「OK」「いいよ」「進めて」 | 3 点を確定し Step 3 へ |
| 「(別の柱を提示)」 | 提示された柱で再構成、再度ユーザー確認 |
| 「○番を変えたい」 | 該当番号のみ AI が再生成、再度ユーザー確認 |
| 「3 点じゃなくて 2 点でいい」 | 数を調整して再構成、再度ユーザー確認 |

**柱の合意なしに Step 3 (下書き生成) に進んではならない。** 誤った柱で進むと revise loop が無限化する。

#### 確定後の処理

確定した柱ごとに、`vision.md` のビジョン要素 (V1-V7 等) と紐付ける。整合する要素が複数ある場合は全て列挙する。整合する要素がゼロの柱は「ビジョンに整合しない柱」としてマークし、Step 3 で「失敗した点 / ビジョンに整合しなかった点」セクションに含めることを提案する。

確定結果のフォーマット:

```
柱が確定しました:

1. (柱 1) → V1, V4
2. (柱 2) → V5
3. (柱 3) → 整合要素なし (失敗談として扱う)

下書きを生成します...
```

→ Step 3 へ。

### Step 3: 下書き生成

#### 出力先パスの決定

デフォルト: `<project-path>/docs/draft/YYYY-MM-DD-<title>.md`

- `<title>` は柱から自動生成 (例: 「taimei-auth-separation」「freee-mcp-namespace-pattern」)
- ファイル名候補をユーザーに提示し、変更を許可
- `<project-path>/docs/draft/` ディレクトリが存在しなければ作成する

#### 下書きの 3 段構成

`${CLAUDE_PLUGIN_ROOT}/skills/translate-to-vision-story/references/zenn-article-structure.md` の構造に従う:

1. **背景** (200-400 字) — なぜこのプロジェクトを始めたか / 解決したい課題 / ビジョン要素との繋がりを 1 文
2. **取り組み** (1500-3000 字) — 技術詳細 / 重要な設計判断 (検討した代替案と却下理由) / コード例
3. **ビジョンへの繋がり** (200-400 字) — どのビジョン要素を前進させたか / 次の手

「ビジョンに整合しなかった柱」がある場合は、3. の前に「失敗した点 / ビジョンに整合しなかった点」セクションを追加する。

#### Frontmatter

```yaml
---
title: "(自動生成)"
emoji: "💭"
type: "tech"
topics: ["claudecode"]  # 柱から推定して追加
published: false
---
```

#### ファイル書き出し

Write ツールでファイル作成。書き出し後、ユーザーに以下を提示:

```
下書きを生成しました: <output-path>

変更したい箇所があれば教えてください:
- 「ここ弱い」「ここ強調」「この技術詳細追加」「カット」 などの FB を受け付けます
- 「OK」と言えば完了処理に進みます
```

→ Step 4 へ。

### Step 4: revise loop

#### ユーザー FB の解釈

| FB パターン | 動作 |
|---|---|
| 「○○を強調」 | 該当箇所を 50% 程度厚くする (Edit でファイル更新) |
| 「○○弱い / 詳細追加」 | 該当箇所に技術詳細・コード例・図を追加 |
| 「○○カット」 | 該当箇所を削除、前後を接続 |
| 「○○を別の言い方で」 | 該当箇所を書き換え |
| 「ビジョン要素 V_x への繋がりが弱い」 | 該当ビジョン要素について追記 |
| 「OK」「これで完了」 | Step 5 へ |

#### revise の単位

- 1 FB につき 1 ファイル更新 (Edit) で対応
- 大規模な書き換えが必要な場合は Write で全文書き直し
- 各 revise の後、変更要約をユーザーに提示してから次の FB を待つ

#### revision-log の記録

Step 5 で revision-log を記録するため、各 revise の内容を内部的に保持する。形式:

```
- (revise 1) ユーザー FB: "○○強調" → 該当段落を厚くした
- (revise 2) ユーザー FB: "V_x への繋がり弱い" → 該当ビジョン要素について追記
- ...
```

#### loop 終了

ユーザーが「OK」「これで完了」「いいよ」と発話したら Step 5 へ進む。

→ Step 5 へ。
