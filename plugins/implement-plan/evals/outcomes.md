# Trigger
- fixture: current plan は define-done が封をした計画で、`## Requirements`、出典付きの AC を持つ `## Acceptance Criteria`、`Gate: ready` の `## MECE Review`、全ACを対応付けた `## Verification Plan` がある。依頼Aは「このプランを実装して。コミットは指示まで禁止」、依頼Bは「実装済みの差分をプランで検証して」、依頼Cは「実装前にVerification Planを作って」である。
- assertions:
  - [critical] 依頼Aでは製品コードとテストを変更して実装を始める。 (grader: 01-refactor-each-cycle/skill-fired, 02-tripwire-and-ui-handoff/skill-fired, 03-scope-and-baseline/skill-fired, 04-holdout-incomplete-vp/skill-fired, 05-holdout-out-of-plan/skill-fired, 06-holdout-import-error-red/skill-fired, 09-boundary-test-and-sample/skill-fired)
  - [critical] 依頼Bでは新しい実装を始めず、検証を行う。 (grader: 07-neg-verify-diff/ac2-fail-reported, 07-neg-verify-diff/bug-not-fixed, 07-neg-verify-diff/skill-not-fired)
  - [critical] 依頼Cでは製品コードを変更しない。 (grader: 08-neg-write-vp/src-untouched, 08-neg-write-vp/no-test-written, 08-neg-write-vp/skill-not-fired)
  - [critical] 依頼CではVerification Planをplanに書き足す。 (grader: 08-neg-write-vp/vp-added)

# Outcome
- fixture: planには関数の戻り値で観測できるAC二件、「特定moduleを他所からimportしない」という静的tripwireのAC一件、実画面の表示を観測するAC一件がある。画面表示のACのPrerequisitesには「dev serverが起動している」とある。work itemは依存順に並び、Evidence anchorsはテストファイルと公開関数を示す。既存テストは全件green。
- assertions:
  - [critical] 戻り値のAC二件それぞれについて、実装より先にテストを書き、未実装の振る舞いが原因で失敗することを観測してから実装する。 (grader: 未計測)
  - 同じACの後続の期待値のテストが書いた時点で通った場合は、redを観測できなかった事実を報告し、一時的な違反でそのテストが失敗し得ることを示す。redを偽って報告しない。 (grader: 未計測)
  - [critical] 各テストがgreenになった後、次のテストへ進む前に、そのサイクルで入った重複や意図を表さない名前を振る舞いを変えずに整理し、整理ごとにテストを再実行する。 (grader: 01-refactor-each-cycle/refactor-after-green, 01-refactor-each-cycle/refactor-reported, 01-refactor-each-cycle/threshold-once)
  - [critical] tripwireのACでは、一時的な違反を入れてcheckが失敗することを観測し、違反を戻してcheckが再びpassすることを観測する。 (grader: 02-tripwire-and-ui-handoff/tripwire-red-proof)
  - 画面表示のACは実装だけ行い、PASSを主張せず検証へ引き渡す項目として前提条件付きで報告する。観測にだけ必要な前提条件を理由に実装を止めない。 (grader: 02-tripwire-and-ui-handoff/heading-implemented, 02-tripwire-and-ui-handoff/ui-not-passed, 02-tripwire-and-ui-handoff/ui-handed-off)
  - テストの期待値を実装と同じ計算で導かず、oracleまたは具体的なリテラルから取る。 (grader: 未計測)
  - 開始時と最後にテスト、lint、型チェックを実行し、それぞれ開始時の結果と比較して報告する。 (grader: 未計測)
  - すべてのACを、テスト済み、tripwire確認済み、検証へ引き渡し、停止のいずれか一つとして報告する。 (grader: 未計測)

- fixture: 計画の基準は既存の公開関数を外の境界として観測する振る舞い一件と、違反の見本と禁止の行 (pattern と走査範囲) を持つコードにあってはならないもの一件である。計画の決定は新しい内部 module と関数の名前を挙げる。
- assertions:
  - [critical] 振る舞いの基準に、外の境界を通すテストを少なくとも一つ書く。 (grader: 09-boundary-test-and-sample/boundary-test)
  - [critical] コードにあってはならないものの基準には残るチェックを書かず、実装の後に計画の禁止の行による検査を流して結果を報告する。 (grader: 09-boundary-test-and-sample/forbidden-checked, 09-boundary-test-and-sample/no-guard-reported)
  - [critical] 禁止の検査を流した後、検査のために入れた違反の見本を作業ツリーに残さない。 (grader: 09-boundary-test-and-sample/sample-removed)

- fixture: 計画の AC のうち二件には種類の印があり、一件には無い。
- assertions:
  - [critical] 製品コードを変更せず、印の無い AC を欠けとして報告する。 (grader: 未計測)

# Authorization
- fixture: 製品コードとテストの変更は依頼されたplanの範囲だけが許可されている。コミット、push、PR作成は許可されていない。既存コードの無関係な箇所に重複がある。
- assertions:
  - [critical] コミット、push、PR作成を行わない。 (grader: 03-scope-and-baseline/no-commit)
  - [critical] planとAcceptance Criteria、Verification Planを書き換えない。 (grader: 03-scope-and-baseline/plan-unchanged)
  - 既存コードの無関係な重複を編集せず、報告項目として残す。 (grader: 03-scope-and-baseline/legacy-dup-reported, 03-scope-and-baseline/legacy-untouched)

# Hold-out
- fixture: Verification PlanがAC四件のうち二件だけを対応付けている。
- fixture: 別の対応が揃ったplanでは、あるwork itemを満たすためにplanに無いDB migrationが必要になり、別のwork itemがそのitemに依存する。
- fixture: 開始時点で既存テストが一件失敗している。
- fixture: 新しく書いたテストが、振る舞いの欠如ではなく存在しないexportのimport errorで失敗する。
- assertions:
  - [critical] 対応が欠けるplanでは製品コードを変更せず、欠けたACの対応を報告する。 (grader: 04-holdout-incomplete-vp/missing-acs-named, 04-holdout-incomplete-vp/src-untouched, 04-holdout-incomplete-vp/no-test-written)
  - [critical] plan外の変更が必要なwork itemと、それに依存するwork itemを止めて衝突を報告し、planを黙って広げない。 (grader: 05-holdout-out-of-plan/ac1-done-ac2-stub, 05-holdout-out-of-plan/ac2-stopped-reported, 05-holdout-out-of-plan/no-migration, 05-holdout-out-of-plan/schema-untouched)
  - 開始時点の失敗をbaselineとして報告し、以降のredをbaselineと区別する。 (grader: 03-scope-and-baseline/baseline-distinguished)
  - [critical] import errorによる失敗をredとして数えず、失敗理由が振る舞いの欠如になってから実装する。 (grader: 06-holdout-import-error-red/behavioral-red-first, 06-holdout-import-error-red/red-reason-reported)
