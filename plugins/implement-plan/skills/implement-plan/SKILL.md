---
name: implement-plan
description: Verification Planが全受け入れ基準を対応付けている準備済みの計画を実装する。テストで観測できる各基準を、計画の依存順にred、green、refactorで進める。
---

## 手順

1. 計画の `## Acceptance Criteria`、`- Gate:` が `ready` の `## MECE Review`、全 AC の `### AC-NNN` を持つ `## Verification Plan` を特定する。対応が欠ける AC があればコードを編集する前に止めて欠けを報告し、対応は実装でなく計画から得る。
2. 最初に test suite、lint、type check を一度実行して baseline を記録し、既に red のものは報告して以降の red と区別する。
3. 計画の作業項目を依存順に進め、テストで観測できる基準はテスト一つにつき red → green → refactor のサイクルを回す。refactor が済んでから次のテストを始める。
   - red: `Evidence anchors` の seam に、公開インターフェースを通したテストを一つ書き、期待値は oracle か計算済みのリテラルから取る。import・型・セットアップの失敗は red に数えず、無い公開インターフェースは振る舞いを持たない最小のスタブで補い、振る舞いが無いための失敗を確かめる。書いた時点で通ったテストは red 未観測と報告し、手順4の一時的な違反で落ちうることを示す。
   - green: 通すための最小の変更にとどめ、まだテストの無い期待値を先取りしない。到達しうるテストを実行する。
   - refactor: 全 green のまま、このサイクルで入った重複と意図を表さない名前を、振る舞いの変更と分けられる形で一つずつ直し、そのたびにテストを実行する。差分に重複が無く新しい名前がすべて意図を述べていれば、refactor は済む。既存コードの smell は直さず記録する。
4. 不変条件、不在、静的な tripwire の基準は、チェックを書き、一時的な違反を入れて落ちること、戻して通ることを観測する。
5. 実画面や外部状態が要る基準は、実装して到達するテストを実行し、PASS とは言わず前提条件とともに検証へ引き渡す。観測にだけ要る前提条件は実装を止めない。
6. 計画外の変更が要る項目と、oracle がコードと矛盾する項目は、依存する項目ごと止めて衝突を報告する。計画、AC、Verification Plan は書き換えず、commit、push、PR 作成は依頼が許可したときだけ行う。
7. 最後に test suite 全体、lint、type check を実行し、baseline と比べて報告する。

## 完了

全 AC を tested、tripwire proved、handed to verification、stopped のちょうど一つに割り当て、どの作業項目にも紐づかない AC は stopped にする。基準ごとに、追加したテストまたはチェック、観測した red とその理由、green、適用した refactor を報告する。記録した既存の smell も報告する。基準の受け入れは検証の結果であり、実装はここで終わる。
