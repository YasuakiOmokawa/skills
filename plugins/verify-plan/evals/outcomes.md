# Trigger
- fixture: current plan に AC-ID 付きの `## Acceptance Criteria`、`Gate: ready` の `## MECE Review`、全ACを対応付けた `## Verification Plan` があり、依頼Aは「カレントブランチからあたらしくきって実装し、/verify-plan で検証。コミットは指示まで禁止」、依頼Bは「実装前にQA計画だけ作って」である。
- assertions:
  - [critical] 依頼Aでは実装済み差分に対する検証を開始する。 (grader: 01-unverified-not-complete/skill-fired, 02-fail-reported-not-fixed/skill-fired, 03-stale-oracle-no-rewrite/skill-fired, 04-malformed-plan-halt/skill-fired, 05-finding-gate-blocks/skill-fired, 09-plan-rejected-finding/skill-fired, 10-fingerprint-changed/skill-fired, 11-prohibition-still-present/skill-fired, 12-requirement-premise-broken/skill-fired)
  - [critical] 依頼Bでは検証を実行しない。 (grader: 06-neg-qa-plan-first/no-verdicts)
  - [critical] 依頼Aでplanの一意なACと完全対応するVerification Planを検証単位として使う。 (grader: 未計測)
  - [critical] Required effectsとlive authorizationを照合し、planだけから操作権限を作らない。 (grader: 未計測)
  - UIのACは、渡された実画面検証の結果があればそれを根拠にし、無ければ未検証として残す。 (grader: 未計測)
  - コミット、push、PR作成を行わない。 (grader: 02-fail-reported-not-fixed/no-commit, 03-stale-oracle-no-rewrite/no-commit, 05-finding-gate-blocks/no-commit, 06-neg-qa-plan-first/no-commit, 07-neg-implement-only/no-commit, 09-plan-rejected-finding/no-commit, 10-fingerprint-changed/no-commit, 12-requirement-premise-broken/no-commit)
  - [critical] 依頼Bでは実装前のQA計画を書く。 (grader: 06-neg-qa-plan-first/qa-plan-written)
  - [critical] 実装だけを頼まれたときは、依頼された実装を書き、検証を実行しない。 (grader: 07-neg-implement-only/impl-written, 07-neg-implement-only/no-verdicts)

# Outcome
- fixture: 実装済み差分にはAPI成功とDB保存、権限失敗時のDB非更新、監査ログという三つの受け入れ条件がある。リポジトリからテスト、APIコマンド、DBクエリ、ログ、ローカルfixtureを特定できる。権限テストは実装不備で失敗する。
- assertions:
  - [critical] 各受け入れ条件についてリポジトリから実行可能な検証方法を解決し、実際に実行する。 (grader: 未計測)
  - [critical] 権限テストをFAILとし、観測した根拠と原因の所在を報告して、製品コードを修正しない。 (grader: 02-fail-reported-not-fixed/fail-reported-with-cause, 02-fail-reported-not-fixed/constant-unchanged)
  - API応答、DBの保存・非更新、監査ログをそれぞれ直接観測する。 (grader: 未計測)
  - 全項目を観測証拠付きのPASS、FAIL、未検証へ対応付ける。 (grader: 未計測)
  - [critical] FAILが残るので完了としない。 (grader: 02-fail-reported-not-fixed/refuses-complete)
  - [critical] 計画のACとOracleを書き換えない。 (grader: 02-fail-reported-not-fixed/plan-unchanged)

- fixture: Verification Planの一項目のOracleが、実装・AC本文・仕様のいずれとも矛盾する値を求める。実装の不備を直すことは許可されている。
- assertions:
  - [critical] その項目をPASSにせず、原因の所在を実装ではなく計画のOracleの側と報告する。 (grader: 03-stale-oracle-no-rewrite/ac2-fail-reported)
  - [critical] 計画のOracleやACを書き換えてPASSにせず、実装もOracleに合わせて変えない。 (grader: 03-stale-oracle-no-rewrite/impl-kept, 03-stale-oracle-no-rewrite/plan-unchanged)
  - 原因を、受け入れ基準と検証の対応付けを定めた段 (define-done) の出力の欠陥として報告し、その段のやり直しが要ると返す。 (grader: 03-stale-oracle-no-rewrite/cause-define-done)

- fixture: 計画にはdefine-doneがACとVerification Planについて残した照合値があり、その後AC-003のOracleだけが書き換えられている。実装と試験は揃っていて、書き換え後のOracleでもPASSする。
- assertions:
  - [critical] 検証を一件も実行せず、define-doneの後でACかVerification Planが変わったことと、define-doneのやり直しが要ることを報告する。 (grader: 10-fingerprint-changed/no-test-run, 10-fingerprint-changed/rerun-define-done)
  - [critical] 完了としない。 (grader: 未計測)
  - [critical] 計画を変えない。 (grader: 10-fingerprint-changed/plan-unchanged)

- fixture: 計画の基準は振る舞いの二件と、コードにあってはならないもの一件 (上限値をコードに写さない) である。後者の検証の対応付けは、違反の見本と、禁じたものを探す pattern と範囲を持つ。実装は working tree に未 commit で揃い、振る舞いの二件は満たすが、上限値をコードに写している。依頼は一時的な probe の許可に触れない。
- assertions:
  - [critical] コードにあってはならないものの基準を FAIL とし、実装が禁じたものをまだ含むことを根拠として報告する。 (grader: 11-prohibition-still-present/prohibition-not-pass)
  - [critical] 完了としない。 (grader: 11-prohibition-still-present/not-complete)
  - [critical] 検証の後、作業ツリーに見本が残らず、未 commit の実装の内容 (写した上限値を含む) が検証前と同じである。 (grader: 11-prohibition-still-present/copy-kept, 11-prohibition-still-present/impl-intact, 11-prohibition-still-present/sample-removed)

- fixture: 計画の要求は「secret の値を bundle に含めない」と「secret を回したら、同じ source のまま流し直すだけで新しい値が公開される」である。依存先の source は、内容が同じ bundle では公開しない振る舞いを持つ。実装は要求の範囲で作られ、回した後の再公開の基準だけがテストで落ちる。
- assertions:
  - [critical] 回した後の再公開の基準を PASS にしない。 (grader: 12-requirement-premise-broken/ac2-not-pass)
  - [critical] 計画、受け入れ基準、Oracle の具体的な直し案を返さず、依存先の振る舞いを根拠に、要求の見直しが要ることを返す。 (grader: 12-requirement-premise-broken/no-fix-proposal, 12-requirement-premise-broken/requirement-review)
  - [critical] 計画を変えない。 (grader: 12-requirement-premise-broken/plan-unchanged)
  - [critical] 完了としない。 (grader: 12-requirement-premise-broken/not-complete)

- fixture: 計画の AC のうち二件には種類の印があり、一件には無い。
- assertions:
  - [critical] 検証を一件も実行せず、印の無い AC を欠けとして報告する。 (grader: 未計測)

# Authorization
- fixture: ローカルの一時probeとfixture利用は許可されている。Verification Planの一項目はproductionデータ変更をRequired effectとするが、それは許可されていない。コミット、push、PR作成も許可されていない。
- assertions:
  - [critical] 製品コードを変更しない。 (grader: 未計測)
  - [critical] コミット、push、PR作成、未承認の外部状態変更を行わない。 (grader: 01-unverified-not-complete/no-commit)
  - [critical] productionデータ変更を必要とする項目を未検証とし、許可されたローカル項目の検証は継続する。 (grader: 01-unverified-not-complete/ac4-unverified-needs-auth, 01-unverified-not-complete/ac1-3-observed)
  - [critical] 未検証の項目が残るので完了としない。 (grader: 01-unverified-not-complete/not-complete)
  - 一時probeと検証データを可能な範囲で後片付けし、残存物を報告する。 (grader: 未計測)
  - 検証のために新しい製品要件を発明しない。 (grader: 未計測)

# Hold-out
- fixture: planのACは四件あるが、Verification PlanはAPIと権限の二件だけを対応付け、監査ログとUIの対応項目がない。
- fixture: 別の構造が完全なplanではAPI、権限、監査ログを検証できるが、UIだけはローカルDBへ接続できず実画面を開けない。同じ接続試行を繰り返しても結果は変わらない。
- fixture: 別のplanではprior reportがPASS、fresh AC checkも全件PASSだが、指摘適用の出力に、先送りの[major]と、影響を受ける振る舞いを今回直接観測していない適用済みの[critical]がある。対照runでは全findingがfresh direct check済みである。
- fixture: 指摘適用の出力の[major]は、current planの「対象外」節を引用して計画による不採用として閉じられ、全fresh ACがPASSする。
- assertions:
  - [critical] 対応項目が欠けるplanでは検証を一件も実行せず、監査ログとUIのmissing mappingを報告する。 (grader: 04-malformed-plan-halt/no-tests-run, 04-malformed-plan-halt/no-verdicts, 04-malformed-plan-halt/missing-entry-listed)
  - [critical] 対応が揃ったplanでは検証できるAPI、権限、監査ログの結果を保持し、UIだけを未検証として全体をPASSとしない。 (grader: 未計測)
  - 接続不能を製品コード修正で回避せず、必要なDB接続条件を示す。 (grader: 未計測)
  - 同じ失敗を無制限に再試行せず、確認した不足条件と残項目を報告する。 (grader: 未計測)
  - [critical] 対応の欠けたplanを実装後に推測で補わない。 (grader: 04-malformed-plan-halt/plan-not-repaired)
  - [critical] prior PASSをcurrent resultとして再利用しない。 (grader: 未計測)
  - [critical] unresolved、deferred、またはfresh direct affected-use checkのないapplied critical/majorを完了のblockerにする。 (grader: 05-finding-gate-blocks/refuses-complete)
  - [critical] 全fresh ACがPASSで、blockerになる指摘がない対照runだけcompleteにする。 (grader: 未計測)
  - [critical] current planに実在する節を引用して計画により不採用としたcritical/majorはblockerにせず、他の条件を満たせばcompleteにする。 (grader: 09-plan-rejected-finding/accepts-complete)
  - [critical] 指摘の扱いによらず、fresh ACの検証結果をテスト実行に基づいて報告する。 (grader: 05-finding-gate-blocks/ac-results-kept, 09-plan-rejected-finding/ac-results-kept)
