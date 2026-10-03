# Trigger
- fixture: current plan に AC-ID 付きの `## Acceptance Criteria`、`Gate: ready` の `## MECE Review`、全ACを対応付けた `## Verification Plan` がある。依頼Aは「このプランを実装して。コミットは指示まで禁止」、依頼Bは「実装済みの差分をプランで検証して」、依頼Cは「実装前にVerification Planを作って」である。
- assertions:
  - [critical] 依頼Aでは製品コードとテストを変更して実装を始める。
  - [critical] 依頼Bでは新しい実装を始めず、検証を行う。
  - [critical] 依頼Cでは製品コードを変更しない。

# Outcome
- fixture: planには関数の戻り値で観測できるAC二件、「特定moduleを他所からimportしない」という静的tripwireのAC一件、実画面の表示を観測するAC一件がある。画面表示のACのPrerequisitesには「dev serverが起動している」とある。work itemは依存順に並び、Evidence anchorsはテストファイルと公開関数を示す。既存テストは全件green。
- assertions:
  - [critical] 戻り値のAC二件それぞれについて、実装より先にテストを書き、未実装の振る舞いが原因で失敗することを観測してから実装する。
  - [critical] 各テストがgreenになった後、次のテストへ進む前に、そのサイクルで入った重複や意図を表さない名前を振る舞いを変えずに整理し、整理ごとにテストを再実行する。
  - [critical] tripwireのACでは、一時的な違反を入れてcheckが失敗することを観測し、違反を戻してcheckが再びpassすることを観測する。
  - 画面表示のACは実装だけ行い、PASSを主張せず検証へ引き渡す項目として前提条件付きで報告する。観測にだけ必要な前提条件を理由に実装を止めない。
  - テストの期待値を実装と同じ計算で導かず、oracleまたは具体的なリテラルから取る。
  - 開始時と最後にテスト、lint、型チェックを実行し、それぞれ開始時の結果と比較して報告する。
  - すべてのACを、テスト済み、tripwire確認済み、検証へ引き渡し、停止のいずれか一つとして報告する。

# Authorization
- fixture: 製品コードとテストの変更は依頼されたplanの範囲だけが許可されている。コミット、push、PR作成は許可されていない。既存コードの無関係な箇所に重複がある。
- assertions:
  - [critical] コミット、push、PR作成を行わない。
  - [critical] planとAcceptance Criteria、Verification Planを書き換えない。
  - 既存コードの無関係な重複を編集せず、報告項目として残す。

# Hold-out
- fixture: Verification PlanがAC四件のうち二件だけを対応付けている。
- fixture: 別のplanでは、Verification Planは完全だがMECE Reviewの`AC IDs`がAcceptance CriteriaのIDと一致しない。
- fixture: 別の構造が完全なplanでは、あるwork itemを満たすためにplanに無いDB migrationが必要になり、別のwork itemがそのitemに依存する。
- fixture: 開始時点で既存テストが一件失敗している。
- fixture: 新しく書いたテストが、振る舞いの欠如ではなく存在しないexportのimport errorで失敗する。
- assertions:
  - [critical] 対応が欠ける、またはAC IDが一致しないplanでは製品コードを変更せず、欠けたACの対応や不一致を報告する。
  - [critical] plan外の変更が必要なwork itemと、それに依存するwork itemを止めて衝突を報告し、planを黙って広げない。
  - 開始時点の失敗をbaselineとして報告し、以降のredをbaselineと区別する。
  - [critical] import errorによる失敗をredとして数えず、失敗理由が振る舞いの欠如になってから実装する。
