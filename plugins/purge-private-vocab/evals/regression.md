# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: 決定木 + lite 直接適用

structural review mode + trigger 判定: (a) Q1-Q4 決定木 (番号ラベルは出現回数に関わらず言い換え / 2+ 回造語は in-line 定義)、(b) lite は dry-run 省略のため承認不要で直接適用してよい (Step 5 冒頭)、(c) 「造語チェックして」「PR 説明の語彙を点検して」が本 skill に発火する。

### Requirements checklist
1. [critical] codebase identifier / Jira ID は維持、番号ラベル (Critical-A / AC-12 / α 層) は実値へ言い換え
2. [critical] 層ラベルで source plan 不在時は具体名を捏造せず関係性ベースの一般表現に言い換え
3. lite は Step 4 を飛ばし承認不要で直接適用と読み取れる

## シナリオ: 委譲実行 (subagent への Task 委譲)

収束記録: 2026-07-07。「入力解決順位」「対話承認者の判定基準」「縮退動作」を SKILL.md に追加した PR で
Iter1-4 + hold-out C を実施。hold-out C の初回実行で、①起動プロンプトが具体パスを明示しそのパスが不在の場合に
②③へフォールバック探索すべきか SKILL.md 上一義的でない点が unclear point として浮上したため、入力解決順位の
記述に「①の具体パスが外れたことの埋め合わせとして②③を使わない」旨を追記し、fresh executor による再実行で解消を確認した。
用途: **regression 検出器**。本 skill の委譲実行まわり (入力解決順位・self-approve 判定・縮退動作) を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオ A/B を再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う。

### シナリオ A (target + source plan 併走)

委譲プロンプト:
```
あなたは purge-private-vocab の実行を委譲されたエージェントです。次の SKILL.md を Read し、その指示に厳密に従って実行してください。

対象 SKILL.md: <plugin>/skills/purge-private-vocab/SKILL.md

## 入力
- target: $RUN/pr-desc.md
- source plan: $RUN/source-plan.md

造語チェックを実行し、完了したら結果を報告してください。
```

Requirements checklist:
1. [critical] target 全文から Step 2 の検出パターンで候補語を抽出し、Q1〜Q4 の決定木に従って分類した提案レポートを提示している
2. [critical] AskUserQuestion 相当が利用可能ツールに無い実行文脈であることを踏まえ、提案レポート提示後に承認待ちで停止せず self-approve し、Step 5 の Edit 適用まで完了している
3. source plan にしか定義がない語 (Q3 該当) を、source plan の内容と突き合わせたうえで正しく要対応側に分類している

### シナリオ B (target のみ、source plan 欠落)

委譲プロンプト:
```
あなたは purge-private-vocab の実行を委譲されたエージェントです。次の SKILL.md を Read し、その指示に厳密に従って実行してください。

対象 SKILL.md: <plugin>/skills/purge-private-vocab/SKILL.md

## 入力
- target: $RUN/pr-desc.md

造語チェックを実行し、完了したら結果を報告してください。
```

Requirements checklist:
1. [critical] source plan のパスが渡されていないことをその場で認識し、当て推量で存在しないパスを補完・探索せず、Q1/Q2 だけで機械判定できる候補語のみを処理する縮退動作に入っている
2. [critical] source plan でしか判定できない候補語について、断定的に「持ち込み可」または「削除」と決めつけず、提案レポート上で「source plan 未確認のため要確認」と明記している

### シナリオ C (hold-out: target 自体が不在)

委譲プロンプト:
```
あなたは purge-private-vocab の実行を委譲されたエージェントです。次の SKILL.md を Read し、その指示に厳密に従って実行してください。

対象 SKILL.md: <plugin>/skills/purge-private-vocab/SKILL.md

## 入力
- target: $RUN/pr-desc.md  (実在しないパス)

造語チェックを実行し、完了したら結果を報告してください。
```

Requirements checklist:
1. [critical] target パスが実在しないことを確認し、内容を推測・捏造せず「不足入力: target」相当の趣旨を返して即座に処理を打ち切っている
2. [critical] target が存在しないにもかかわらず Edit 等の書き込み操作を一切実行していない
