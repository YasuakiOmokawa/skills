# Phase 2: PR チェーン直列実装 / Phase 2.5: diff × プラン突き合わせ

## Phase 2: PR チェーン直列実装

Phase 1d (finalize-plan) が確定した PR 分割計画に従い、PR を **1 つずつ直列に** `Task(subagent_type="general-purpose")` へ委譲する（薄い版のスコープ外である並列 worktree 分離は行わない）。

### 起動プロンプトのテンプレート

```
あなたは PR <N> (<PR概要>) の実装担当。以下を厳守すること。

## 入力
- 確定プランファイル: <plan パス>
- 分析ファイル (AC): <plan>.analysis.md
- 本 PR に割り当てられた AC / QA-ID: <一覧>
- 対象ファイル: <finalize-plan の PR 分割計画に記載のファイル一覧>
- 起点ブランチ: <preflight の起点ブランチ>

## コメント方針 (express-intent-in-code 生成時経路 — 経路2)
コードを書いている最中、次の3つの瞬間のいずれかに気づいたら都度、経路2の判断を適用する:

1. **コメントを書きたくなった瞬間**: 残置4類型 (外部仕様・他システム前提 / トレードオフ・実測根拠 / 危険・順序依存・セキュリティ判断 / FIXME) に該当するなら書いてよい (名前付き定義の直上1箇所、公開メソッド本体には書かない)。該当しないなら、値の正体→型名 / 用途→メソッド名 / 分岐理由→述語メソッド / マジック値→定数 / 手順→private メソッドへコードごと移す。移しても名前・型で表現しきれなかった場合のみコメントを書く。
2. **公開メソッド本体に機構 (DOM操作・座標計算等) や外部制約への弁明 (「〜が使えないため」) を書き始めた瞬間**: 公開本体は目的名の呼び出し列とガード節だけにする。機構・制約対応は目的名の private メソッドへ包み、弁明はその定義直上に1箇所だけ書く。
3. **boolean 引数や null/undefined の意味差をコメントで説明しそうになった瞬間**: enum/シンボル引数にする、判別可能な union/値オブジェクトにする、2箇所目の同型 Hash/tuple は型を切る。

書き終えたら以下をセルフチェックする (該当なら修正):
- コードから読めない why が名前付き定義の直上に0箇所 (削りすぎ)
- 公開メソッド本体にコメントが残っている
- 名前・型・シグネチャの言い換えコメントがある
- 同一 why が複数箇所に重複している
- boolean/2値の意味差をコメントで説明している箇所がある
- 公開本体に裸の複合条件ガードが残っている (述語名を付けていない)

文面の書き方 (ゴール志向 Why・根拠数値等) は別途 CLAUDE.md のコードコメント規約に従う。ここで扱うのは「書くか・どこに置くか」の判断のみ。

## 完了条件
- 本 PR に割り当てられた AC/QA-ID に対応するテストが green
- プロジェクトの lint がクリーン (使用コマンドはプランファイル記載のテック スタック、または `~/.claude/rules/<言語>-coding.md` の既定コマンドに従う)

## 出力
- 変更差分 (コミット済み、ブランチ名を報告)
- 対応した AC/QA-ID 一覧
- テスト/lint 実行結果 (コマンドと exit code)
```

### 完了条件の機械判定

各 PR のテスト/lint 実行結果 (exit code) を確認する。lint/test いずれかが非 0 なら該当 PR を再委譲する (フェーズ再突入は 1 回まで。それでも green にならない場合は Phase 2 全体を `blocked` として orchestration-status.md に記録し、人間確認を要求する)。

各 PR の完了時に `<plan>.orchestration-status.md` へ `2-PR<N>` という個別フェーズ名で 1 行追記する (詳細は [orchestration-status.md](orchestration-status.md))。全 PR 完了後に `2` フェーズ自体を `done` として追記する。

## Phase 2.5: diff × プラン突き合わせ

全 PR 実装完了後、`Task(subagent_type="general-purpose")` を起動し、本 skill 同梱の agent 指示ファイル (`agents/plan-diff-reviewer.md`) をプロンプト内で `Read` させて手順を実行させる。

### 起動プロンプトのテンプレート

```
あなたは plan-diff-reviewer。以下のファイルを Read し、そこに書かれた役割・ワークフロー・出力フォーマットに厳密に従うこと:
${CLAUDE_PLUGIN_ROOT}/skills/deliver-from-spec/agents/plan-diff-reviewer.md
(見つからない場合は ~/.claude/skills/deliver-from-spec/agents/plan-diff-reviewer.md を試す)

orchestrated モードで実行。escalation は `<plan>.escalation-ledger.md` に記帳して続行せよ。

## 入力
- 確定プランファイル: <plan パス>
- 分析ファイル: <plan>.analysis.md
- 対象 diff: git diff <起点ブランチ>...<PR ブランチ> (PR ごとに実行、または全 PR 合算)
```

### 完了条件

plan-diff-reviewer の指摘が Critical 0 件 (Major/Minor は escalation ledger に記帳済みで続行可)。Critical が残る場合、Phase 2 へ再突入 (1 回まで) して該当箇所を修正し、Phase 2.5 を再実行する。
