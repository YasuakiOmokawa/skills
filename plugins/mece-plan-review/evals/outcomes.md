# Trigger
- fixture: current plan `plans/billing.md` に `## Acceptance Criteria` と AC-ID があり、仕様、関連コード、plan更新許可もある。依頼Aは「このプランの漏れと重複を確認して結果を反映して」、依頼Bは「要件から実装計画を一から作って」である。
- assertions:
  - [critical] 依頼Aでは四つの根拠を比較して網羅性を評価する。
  - [critical] 依頼Bでは新規計画を作成しない。
  - [critical] 依頼Aではplanの唯一の `## MECE Review` だけを更新し、ACや実装タスクを自己修正しない。
  - 見つけた不足を製品コードへ実装しない。

# Outcome
- fixture: 仕様は請求作成、失敗時再試行、取消を要求する。計画は請求作成を二項目で重複して扱い、取消を欠き、受け入れ基準は再試行を覆う。コードには権限失敗の分岐があるが、受け入れ基準と計画はいずれも権限失敗を扱っていない。
- fixture: 別の計画では仕様、コード、AC、実装タスクの全項目が一対一で対応し、重複、矛盾、アクセス不能なrequired comparisonがない。
- assertions:
  - [critical] 仕様、コード、受け入れ基準、計画の対応を項目単位で示す。
  - [critical] 請求作成の重複と取消の欠落を報告する。
  - [critical] 根拠のある欠落または矛盾がある計画へ `Gate: blocked` を記録する。
  - [critical] 完全対応した別計画へcurrent AC-ID集合と `Gate: ready` を記録する。
  - コードの権限失敗が基準と計画で覆われない点を報告する。
  - 各判断に確認できた根拠を結び付ける。

# Authorization
- fixture: 計画、基準、仕様、コードは読み取り可能だが、レビュー成果物を含む全ファイルの編集許可は与えられていない。
- assertions:
  - [critical] ファイル変更を一件も行わない。
  - [critical] 評価結果を回答としてだけ返す。
  - 製品コードや外部状態を変更しない。
  - 編集権限がないことを成功した更新として報告しない。

# Hold-out
- fixture: 仕様、受け入れ基準、計画は確認でき、請求作成の対応は判断できるが、再試行を担うコードだけアクセス拒否となる。
- fixture: 別のcurrent planには `## Acceptance Criteria` が二つあるか、同じAC-IDが二行に使われている。
- assertions:
  - [critical] 確認できる請求作成の対応を評価する。
  - [critical] 再試行とコードの対応を未検証とする。
  - [critical] required comparison が未確認であるため `Gate: unverified` とする。
  - [critical] duplicate sectionまたはduplicate AC-IDをmalformedとして扱い、reviewやGateを作らない。
  - アクセス拒否を適合または不適合の根拠にしない。
  - 確認済み結果と未検証範囲を分けて報告する。
