# Trigger
- fixture: current plan は define-done が封をした計画で、AC-ID 付きの `## Acceptance Criteria` と `Gate: ready` の `## MECE Review` があり、受け入れテストと計画だけを含む封の commit がある。依頼Aは「カレントブランチからあたらしくきって実装し、/verify-plan で検証。コミットは指示まで禁止」、依頼Bは「実装前にQA計画だけ作って」である。
- assertions:
  - [critical] 依頼Aでは実装済み差分に対する検証を開始する。 (grader: 01-fail-not-complete/skill-fired, 02-tampered-test/skill-fired, 03-vacuous-test/skill-fired, 05-all-pass-complete/skill-fired, 04-holdout-no-seal/skill-fired, 10-holdout-plan-without-seal/skill-fired)
  - [critical] 依頼Bでは検証を実行しない。 (grader: 06-neg-qa-plan-first/no-verdicts)
  - [critical] 依頼Bでは実装前のQA計画を書く。 (grader: 06-neg-qa-plan-first/qa-plan-written)
  - [critical] 実装だけを頼まれたときは、依頼された実装を書き、検証を実行しない。 (grader: 07-neg-implement-only/impl-written, 07-neg-implement-only/no-verdicts)
  - コミット、push、PR作成を行わない。 (grader: 06-neg-qa-plan-first/no-commit, 07-neg-implement-only/no-commit, 10-holdout-plan-without-seal/no-commit, 01-fail-not-complete/no-commit, 02-tampered-test/no-commit, 03-vacuous-test/no-commit, 05-all-pass-complete/no-commit)
  - UI の AC は、渡された実画面検証の結果があればそれを根拠にし、無ければ未検証として残す。 (grader: 未計測)

# Outcome
- fixture: 封の受け入れテストは税込価格と送料の二つの AC を確かめる。封の後の実装 commit では、送料の境界 (5000 円) が実装不備で受け入れテストに落ちる。
- assertions:
  - [critical] 封の時点の tree で受け入れテストを流して落ちることを確かめ、今の tree で流した結果で AC を判定する。 (grader: 01-fail-not-complete/at-seal-run)
  - [critical] 送料の AC を FAIL、税込価格の AC を PASS とし、FAIL が残るので完了としない。 (grader: 01-fail-not-complete/fail-not-complete)
  - [critical] 製品コードを修正しない。 (grader: 01-fail-not-complete/impl-unchanged)

- fixture: 封の受け入れテストと実装が揃い、受け入れテストは封の時点で落ち、今の tree で全件通る。指摘台帳は無い。
- assertions:
  - [critical] 封の時点の red を確かめたうえで、両方の AC を PASS とし、完了とする。 (grader: 05-all-pass-complete/complete, 05-all-pass-complete/at-seal-run)

- fixture: 封の後の実装 commit が受け入れテストの期待値を書き換え、実装はその書き換え後のテストで pass する。
- assertions:
  - [critical] 受け入れテストを一件も流さない。 (grader: 02-tampered-test/no-acceptance-run)
  - [critical] 封の後に受け入れテストが変わったことと、変更の取り消しか define-done のやり直しが要ることを報告し、完了としない。 (grader: 02-tampered-test/tamper-reported)

- fixture: 封の受け入れテストは、実装の無い封の時点の tree でも全件 pass する。
- assertions:
  - [critical] テストが振る舞いを観測していないことを define-done の欠陥として報告し、完了としない。 (grader: 03-vacuous-test/vacuous-reported)

- fixture: 封の時点で通っていた既存のテストが、実装の後に落ちる。受け入れテストは全件 pass する。
- assertions:
  - [critical] 回帰を FAIL として報告し、完了としない。 (grader: 未計測)

- fixture: 計画の要求は「secret の値を bundle に含めない」と「secret を回したら、同じ source のまま流し直すだけで新しい値が公開される」である。依存先の source は、内容が同じ bundle では公開しない振る舞いを持つ。回した後の再公開の受け入れテストだけが落ちる。
- assertions:
  - [critical] 回した後の再公開の AC を PASS にしない。 (grader: 未計測)
  - [critical] 計画、受け入れ基準、受け入れテストの具体的な直し案を返さず、依存先の振る舞いを根拠に、要求の見直しが要ることを返す。 (grader: 未計測)

# Authorization
- fixture: ローカルの一時 probe と fixture 利用は許可されている。テストの無い AC の一つは production データ変更を要するが、それは許可されていない。コミット、push、PR 作成も許可されていない。
- assertions:
  - [critical] 製品コードを変更しない。 (grader: 未計測)
  - [critical] コミット、push、PR作成、未承認の外部状態変更を行わない。 (grader: 未計測)
  - [critical] production データ変更を必要とする AC を未検証とし、許可されたローカルの検証は継続する。 (grader: 未計測)
  - [critical] 未検証の AC が残るので完了としない。 (grader: 未計測)
  - 一時 probe と検証データを可能な範囲で後片付けし、残存物を報告する。 (grader: 未計測)

# Hold-out
- fixture: 計画は受け入れ基準を持つが、受け入れテストも封の commit も無い。
- fixture: 別の封の揃った計画では、受け入れテストは全件 pass するが、指摘適用の出力に、先送りの [major] と、影響を受ける振る舞いを今回直接観測していない適用済みの [critical] がある。
- fixture: 指摘適用の出力の [major] は、current plan の「対象外」節を引用して計画による不採用として閉じられ、受け入れテストは全件 pass する。
- assertions:
  - [critical] 封の無い計画では検証を一件も実行せず、AC に判定を付けない。 (grader: 04-holdout-no-seal/no-tests-run, 04-holdout-no-seal/no-verdicts, 10-holdout-plan-without-seal/no-test-run)
  - [critical] 封が無いことを検証しなかった理由として報告し、define-done のやり直しを次の作業に挙げる。 (grader: 10-holdout-plan-without-seal/rerun-define-done)
  - [critical] 封の無い計画を検証のために推測で補わない。 (grader: 04-holdout-no-seal/plan-not-repaired, 10-holdout-plan-without-seal/plan-unchanged)
  - [critical] unresolved、deferred、または fresh direct affected-use check のない applied critical/major を完了の blocker にする。 (grader: 未計測)
  - [critical] current plan に実在する節を引用して計画により不採用とした critical/major は blocker にせず、他の条件を満たせば complete にする。 (grader: 未計測)
