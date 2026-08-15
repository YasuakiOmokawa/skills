# 委譲実行 (qa-ui)

委譲実行の読み替えを定める。単独起動の現行動作は変えない。発動条件は同期的な返答を待てないことであり、subagent という名前だけでは判定しない。

## Resolve inputs

ベース URL は起動プロンプト本文 → 単独起動時のセッション → `SKILL.md` のプラン記載値で解決し、無ければ `不足入力: ベース URL` と終了する。プランパスは明示指定または単独起動時のセッションから解決し、無くても停止せず `SKILL.md` の no-QA-ID source fallback へ進む。

## Split manual handoff

`SKILL.md` の `Manual default` は、同期的な返答を待てない委譲実行では次のとおり分割する:

1. 委譲実行では手順書全文を最終メッセージとして返し、その時点で終了する（待たない）。
2. 呼び出し元は人間から回答を得たうえで本 skill を再起動する。台帳（`<プラン名>.qa-ledger.md`）を追記専用の状態正本とし、再起動時は current source generation 内の各 `(QA-ID, 手段)` 最新行から再開する。
3. 最終メッセージには手順書全文に加え、上記 1〜2（人間の回答を得たうえで台帳から再開する旨）を明記する。

この契約は Orchestrated モードでも変わらない。初回の手動依頼は escalation ledger の対象外とする（[orchestrated-mode.md](orchestrated-mode.md)）。

## automation モードで独立 evaluator が使えない場合

独立 evaluator が使えなくても browser automation capability があれば、main agent が `agents/ui-evaluator.md` を読み inline で同じ検証を行う。browser capability 自体が無い場合、台帳があれば対象 QA-ID を `検証不能(真の制約)` として記帳し、なければ同じ状態を報告する。他の対象の処理は止めない。
