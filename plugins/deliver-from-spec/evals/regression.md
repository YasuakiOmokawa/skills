# regression eval

収束記録: 2026-07-06 (v0.1.0 PR)。3 シナリオ × Iter1-3 の 9 実行で fresh executor が全 [critical] ○ / skill 修正 0 回 / retries 0。skill を変更する PR では fresh executor (Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。用途は regression 検出器であり、capability 改善の信号としては扱わない。

**v0.2.0 追記**: preflight から「仕様判断の扱い」選択式項目 (full-auto 経路) を削除し、Phase 1c を常に停止して人間確認する仕様へ一本化した (利用者決定 2026-07-06)。これに伴い下記「仕様判断バッチ」シナリオの checklist を改訂した。収束記録 (v0.2.0): 2026-07-06。連鎖ハッピーパス・出荷ゲートの再実行、仕様判断バッチ改訂版と新規「スライスの可逆性判定」の Iter1-3 (各 3 実行)、計 10 実行で fresh executor が全 [critical] ○ / skill 修正 0 回。

## シナリオ: 連鎖ハッピーパス (Phase 1a〜1d の遷移)

親エージェントとして、仕様文書パス `docs/specs/add-role-field.md` を受け取った直後。preflight は既に環境系 4 項目が確定済み (`<plan>.preflight.md` 存在)、`<plan>.orchestration-status.md` は未生成。review-design が起動され `<plan>.design-review.md` を fatal 0 件で保存し終えた直後の状態から、Phase 1a 完了〜Phase 1d 開始までに取るアクションを答えさせる。

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

親エージェントとして Phase 1b 完了直後、Phase 1c (仕様判断バッチ) 開始時点。Phase 1c は仕様判断について常に停止して人間確認する仕様 (v0.2.0 で preflight の「仕様判断の扱い」選択式項目は削除済み)。preflight の環境系 4 項目は確定済みだが、AC 依存の 2 項目 (権限アカウント一覧・テストデータ準備手順) は Phase 0 時点で `未定` のまま Phase 1c へ持ち越されている。加えて、確定したプランの中に「認可の失敗時にエラーメッセージを表示するか、無言で 403 を返すか」という未決の仕様判断が 1 件見つかった。Phase 1c で取るアクションを答えさせる。

### Requirements checklist
1. [critical] 権限アカウント一覧・テストデータ準備手順の 2 項目は Phase 0 の完了条件に含まれていなかった (design 上の意図的な繰越) ことを踏まえ、Phase 1c でこの 2 項目を初めて解決しようとする（Phase 0 のやり直しとして扱わない）
2. [critical] Phase 1c は常に停止して確認する仕様であることを踏まえ、未決の仕様判断 (エラーメッセージ表示 or 無言403) を含む全件を 1 回の `AskUserQuestion` にまとめて人間に確認する（機械側で片方を勝手に確定させない）
3. 未決仕様判断 0 件になった時点で Phase 1c 完了とし、`<plan>.orchestration-status.md` に `フェーズ=1c, 状態=done` を追記してから Phase 1d (`/finalize-plan`) へ進む

(改訂注記: v0.2.0 で「仕様判断の扱い」欄の full-auto 選択肢 (`推奨案で続行し escalation 記帳`) を preflight から削除したことに伴い、旧 checklist item 4 (full-auto 経路の代替説明を求める項目) を削除した。改訂版は Iter1-3 で再収束済み — 冒頭の v0.2.0 収束記録を参照)

## シナリオ: スライスの可逆性判定 (Phase 0)

親エージェントとして、Phase 0 実行中。preflight 収集と PRD 分解 (進捗台帳への全行起票) が終わり、「スライスの可逆性判定」に入った直後。対象スライスは 2 つ:

- スライス A: 「ユーザー一覧画面に検索フィルタ UI を追加する」(既存 API のクエリパラメータを 1 つ増やすのみ。DB スキーマ変更なし、公開 API 契約変更なし、チーム間境界なし)
- スライス B: 「注文テーブルに `refund_status` カラムを追加し、返金 API を新設する」(DB migration を伴い、他チームが利用中の公開 API に新フィールドが乗る)

この 2 スライスをそれぞれどちらの経路 (Phase 1a design-first / `/iterate-with-prototypes`) へ振り分けるかを答えさせる。

### Requirements checklist
1. [critical] スライス B (DB migration + 公開 API 契約変更) は不可逆決定を含むと判定し、`/iterate-with-prototypes` へは分岐させず現行どおり Phase 1a (design-first、`/review-design`) を起動する
2. [critical] 判定基準は `/iterate-with-prototypes` の適用条件 (「危険な未知が戻しにくい決定 (DB スキーマ/migration/公開API契約/チーム間境界) を含むなら code-first は不可」) をそのまま使う。新しい基準を作ったり、一部の要素だけを恣意的に抜粋したりしない
3. スライス A (可逆・小 blast radius) は Phase 1a を起動せず `/iterate-with-prototypes` を起動する
4. スライス A と B を一括で同じ経路に倒さず、それぞれ個別に判定する

収束記録: 2026-07-06 (v0.2.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / retries 0
