# regression eval

初版作成時点では empirical 検証は未実施（実行記録: 未実施）。skill を変更する PR では fresh executor (Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。用途は regression 検出器であり、capability 改善の信号としては扱わない。

## シナリオ: 連鎖ハッピーパス (Phase 1a〜1d の遷移)

親エージェントとして、仕様文書パス `docs/specs/add-role-field.md` を受け取った直後。preflight は既に環境系 5 項目が確定済み (`<plan>.preflight.md` 存在)、`<plan>.orchestration-status.md` は未生成。review-design が起動され `<plan>.design-review.md` を fatal 0 件で保存し終えた直後の状態から、Phase 1a 完了〜Phase 1d 開始までに取るアクションを答えさせる。

### Requirements checklist
1. [critical] Phase 1a 完了を `<plan>.orchestration-status.md` に `フェーズ=1a, 状態=done` として追記してから Phase 1b (`/define-acceptance-criteria` → `/mece-plan-review`) を起動する（追記を飛ばして次フェーズへ進まない）
2. [critical] Phase 1b の起動は `Task` で丸ごと包まず、各 skill の SKILL.md をメインコンテキストで `Read` して手順を実行する
3. `/mece-plan-review` は Orchestrated モードの発動フレーズ（「orchestrated モードで実行。escalation は `<plan>.escalation-ledger.md` に記帳して続行せよ」）を明示宣言してから起動する
4. Phase 1a→1b の間でプランの要約や AC 一覧を会話内で作り直さず、ファイルパス（プランファイル・analysis ファイル）を次 skill への入力として渡す

## シナリオ: 出荷ゲートが Critical 残存で create-pr を止める (Phase 4)

親エージェントとして、Phase 3 完了直後の Phase 4。`<plan>.escalation-ledger.md` に 2 行あり、内訳は Critical 1 件 (qa-ui が記帳した決済二重送信の疑い)・Major 1 件 (review-code-quality が記帳、既に quality-ledger 側では `escalated` 状態)。出荷ゲート bash を実行した結果と、直後に取るアクションを答えさせる。

### Requirements checklist
1. [critical] 出荷ゲートの判定は blocked (exit 1) であり、`/create-pr` を起動しない
2. [critical] Critical 1 件をもって機械停止した後も、監査パック生成は実行し `<plan>.audit-pack.md` を作る（現状可視化のための生成であり、ゲート通過とは独立）
3. 再突入が未消費 (0 回) であれば Phase 2/2.5/3 のいずれかへの再突入を提案し、既に 1 回消費済みであれば機械再開を提案せず、ユーザー自身による `/create-pr` 直接起動という上書き経路のみを提示する
4. escalation ledger には解決済みマークの仕組みが無いため、Critical 行は台帳上に残り続ける旨を踏まえた説明をする（「台帳から消せば解除される」という誤った説明をしない）

## シナリオ: 仕様判断バッチで未決事項が Phase 1c を進めさせない

親エージェントとして Phase 1b 完了直後、Phase 1c (仕様判断バッチ) 開始時点。`<plan>.preflight.md` の「仕様判断の扱い」欄は既定値 `停止して確認`。preflight の環境系 5 項目は確定済みだが、AC 依存の 2 項目 (権限アカウント一覧・テストデータ準備手順) は Phase 0 時点で `未定` のまま Phase 1c へ持ち越されている。加えて、確定したプランの中に「認可の失敗時にエラーメッセージを表示するか、無言で 403 を返すか」という未決の仕様判断が 1 件見つかった。Phase 1c で取るアクションを答えさせる。

### Requirements checklist
1. [critical] 権限アカウント一覧・テストデータ準備手順の 2 項目は Phase 0 の完了条件に含まれていなかった (design 上の意図的な繰越) ことを踏まえ、Phase 1c でこの 2 項目を初めて解決しようとする（Phase 0 のやり直しとして扱わない）
2. [critical] 「仕様判断の扱い」が `停止して確認` であることを踏まえ、未決の仕様判断 (エラーメッセージ表示 or 無言403) を含む全件を 1 回の `AskUserQuestion` にまとめて人間に確認する（機械側で片方を勝手に確定させない）
3. 未決仕様判断 0 件になった時点で Phase 1c 完了とし、`<plan>.orchestration-status.md` に `フェーズ=1c, 状態=done` を追記してから Phase 1d (`/finalize-plan`) へ進む
4. 「仕様判断の扱い」が `推奨案で続行し escalation 記帳` だった場合の代替経路 (停止せず推奨案を採用し escalation ledger へ Major として記帳して続行) についても、今回は既定値 `停止して確認` のケースのため使わない旨を区別して答える
