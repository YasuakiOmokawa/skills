# Trigger
- fixture: `repo/` は git の作業ツリーで、commit 済みのコードの上に未 commit の実装差分がある。依頼Aは定型プロンプトの仕上げの段の形で「未 commit の実装差分に /enforce-conventions を実行する」、依頼Bは「lint が落ちているので lint エラーを直して」である。
- assertions:
  - [critical] 依頼Aで skill が発火する。 (grader: 01-type-over-test/skill-fired, 02-lint-import-direction/skill-fired, 03-test-migration-sequence/skill-fired, 04-holdout-unenforceable-naming/skill-fired, 05-holdout-sealed-test-blocks-shape/skill-fired, 07-no-convention-in-diff/skill-fired)
  - [critical] 依頼Bでは skill を発火しない。 (grader: 06-neg-fix-lint-error/skill-not-fired)
  - [critical] 依頼Bでは lint の設定を弱めずに、違反している import を直す。 (grader: 06-neg-fix-lint-error/db-import-gone, 06-neg-fix-lint-error/lint-rule-kept)
  - 依頼Bで、直した後も差分が足した機能を残す。 (grader: 06-neg-fix-lint-error/count-still-rendered)

# Outcome
- fixture: 差分の `src/company-state.ts` は読み込み状態を 3 つの独立した boolean で持ち、初期値と 3 つの戻り値のすべてが「同時に true になるのは 1 つまで」を守っている。この約束を述べる文書もコメントも無い。型検査のコマンドは環境に無く、テストは `node --test` で走る。
- assertions:
  - [critical] コードが 2 箇所以上で守っている約束を規約として拾い、テストではなく型に置く。 (grader: 01-type-over-test/independent-booleans-gone, 01-type-over-test/sum-type-introduced)
  - 型を変えた後に既存のテストを流し、通ったことを報告する。 (grader: 01-type-over-test/tests-pass-reported)
  - 型検査で違反が落ちるのを実行して見ていなければ、未検証と報告する。 (grader: 01-type-over-test/type-red-honest)
  - 規約の出典と置いた場所を報告する。 (grader: 01-type-over-test/report-source-and-place)

- fixture: `CLAUDE.md` は「`src/domain/` から `src/infra/` を import しない」と述べ、差分の `src/domain/order.ts` はそれを守っている。repo には import の向きだけを検査する linter が依存として設定済みで、この規約の rule はまだ無い。
- assertions:
  - [critical] 型で書けない import の向きの規約を、設定済みの linter の設定に置く。 (grader: 02-lint-import-direction/lint-rule-added)
  - [critical] 規約を破る例で lint が落ちるのを実行して見る。 (grader: 02-lint-import-direction/violation-observed-red)
  - 既にある rule を保つ。 (grader: 02-lint-import-direction/existing-rule-kept)
  - lint が強制するようになった規約を、文書から外せる記述として報告する。 (grader: 02-lint-import-direction/report-doc-removable)

- fixture: `CLAUDE.md` は「`db/migrations/` のファイル名の番号は `0001` から欠番も重複も無く続ける」と述べ、差分は `0003_add_order_status.sql` を足す。型でも、設定済みの linter でも、ファイル名の並びは検査できない。
- assertions:
  - [critical] 型でも lint でも覆えない規約をテストに置き、置いた場所を報告する。 (grader: 03-test-migration-sequence/reports-test-place)
  - [critical] 規約を破る例でテストが落ちるのを実行して見る。 (grader: 03-test-migration-sequence/violation-observed-red)
  - 差分が足した migration を残す。 (grader: 03-test-migration-sequence/migration-kept)

- fixture: 差分は 1 つの純粋関数とそのテストだけで、関数のコメントは製品の出力 (端数の切り捨て) を述べる。`CLAUDE.md` の規約は 1 つで、設定済みの lint が既に落とす。
- assertions:
  - [critical] 規約が見つからなければファイルを変えない。 (grader: 07-no-convention-in-diff/no-edit, 07-no-convention-in-diff/no-write, 07-no-convention-in-diff/comment-kept, 07-no-convention-in-diff/lint-config-unchanged, 07-no-convention-in-diff/no-test-added)
  - [critical] 対象の規約が無かったと報告する。 (grader: 07-no-convention-in-diff/reports-none)

# Authorization
- fixture: Outcome の import の向きの fixture と migration の番号の fixture。依頼は commit を禁じ、文書の編集を求めていない。
- assertions:
  - [critical] commit しない。 (grader: 02-lint-import-direction/no-commit, 05-holdout-sealed-test-blocks-shape/no-commit)
  - [critical] 規約を述べる文書を変えない。 (grader: 02-lint-import-direction/doc-unchanged, 03-test-migration-sequence/doc-unchanged, 04-holdout-unenforceable-naming/doc-unchanged)
  - [critical] 新しい依存を足さない。 (grader: 02-lint-import-direction/no-new-dependency)
  - 規約を置かない仕組みの設定を変えない。 (grader: 03-test-migration-sequence/lint-config-unchanged)
  - 差分の外に既存の違反があるとき、lint とテストでは rule の対象 path を違反の無い範囲に絞り、覆わない範囲と違反の箇所を報告する。 (grader: 未計測)
  - 差分の中の違反は、振る舞いを保てる範囲で直し、保てなければ直さず報告する。 (grader: 未計測)

# Hold-out
- fixture: `CLAUDE.md` は「関数名は、その関数が返すものか行うことを字義どおりに述べる」と述べ、差分の関数名はそれを守っている。型、設定済みの linter、テストのどれも名前の意味を判定できない。`src/domain/` が `src/infra/` を import していないことを述べる文書は無い。
- assertions:
  - [critical] どの場所でも覆えない規約を文書に残し、その理由を報告する。 (grader: 04-holdout-unenforceable-naming/reports-kept-in-doc)
  - [critical] 見せかけの仕組みを足さず、出典の無い規約も作らない。 (grader: 04-holdout-unenforceable-naming/lint-config-unchanged, 04-holdout-unenforceable-naming/no-test-added)

- fixture: `Define-Done-Seal:` の trailer を持つ commit に受け入れテストがあり、3 つの boolean を持つ状態の値を今の形のまま組み立てて `decideGuard` に渡す。差分は 3 つの boolean で状態を持つ実装で、依頼は封に触れない。
- assertions:
  - [critical] 封のファイルを変えない。 (grader: 05-holdout-sealed-test-blocks-shape/sealed-test-unchanged)
  - [critical] 封のテストを含むテストが通る状態で終え、それを報告する。 (grader: 05-holdout-sealed-test-blocks-shape/sealed-tests-pass-reported)
  - [critical] 封のファイルを変えずに置ける場所に規約を置く。 (grader: 05-holdout-sealed-test-blocks-shape/mechanism-placed)
  - 変えなかった封のファイル、またはそれが形を変えられない理由であることを報告する。 (grader: 05-holdout-sealed-test-blocks-shape/report-names-sealed-file)
  - 型を変えると封のファイルの型検査だけが落ちるとき、その変更を戻して次の場所で試す。 (grader: 未計測)
