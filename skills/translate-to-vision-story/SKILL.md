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
