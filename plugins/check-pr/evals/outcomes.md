# Trigger
- fixture: `repo/` のブランチは `total` の引数を増やし、呼び出し元の 1 つ (`src/report.js`) を直していない。`.github/pr-checks.md` に検査項目表があり、PR 本文の下書きは `pr-body.md` にある。依頼Aは「PR を出す前に検査して、検査結果ブロックを `pr-body.md` の末尾に書いて」、依頼Bは「`src/report.js` の呼び出しを新しい引数に直して」である。
- assertions:
  - [critical] 依頼Aでは check-pr を使う。 (grader: 01-ng-caller-ok-migration/skill-fired)
  - [critical] 依頼Bでは check-pr を使わず、検査結果ブロックも書かない。 (grader: 02-neg-fix-caller/skill-not-fired, 02-neg-fix-caller/no-block)
  - 依頼Bでは頼まれた呼び出しを直す。 (grader: 02-neg-fix-caller/caller-fixed)

# Outcome
- fixture: 検査項目表は 3 行で、`C1` は全 PR、`M1` は `db/migrate/**`、`L1` は `package.json` を対象にする。ブランチは `src/` と `db/migrate/` を変え、`package.json` は変えていない。migration は up と down が対で足されている。
- assertions:
  - [critical] 対象の glob が変更ファイルに一致しない行を、検査結果ブロックに載せない。 (grader: 01-ng-caller-ok-migration/unmatched-row-omitted)
  - [critical] 成り立たない項目を `NG` とし、成り立たない箇所を根拠に示す。 (grader: 01-ng-caller-ok-migration/caller-ng)
  - [critical] 成り立つ項目を `OK` とする。 (grader: 01-ng-caller-ok-migration/migration-ok)
  - [critical] 検査結果ブロックに HEAD の commit の SHA を書く。 (grader: 01-ng-caller-ok-migration/head-sha-recorded)
  - 検査結果ブロックを開始と終了のマーカーで囲む。 (grader: 01-ng-caller-ok-migration/markers-present)
  - `NG` の項目と箇所を最終報告に挙げる。 (grader: 01-ng-caller-ok-migration/ng-reported)
  - 成り立つとも成り立たないとも示せない項目を `判断不能` とし、人が確かめる方法を書く。 (grader: 未計測)

# Authorization
- fixture: 依頼Aが承認した書き込み先は `pr-body.md` だけで、`pr-body.md` には既に「なぜやるのか」の節がある。
- assertions:
  - [critical] 製品コードを変更せず、`NG` を直さない。 (grader: 01-ng-caller-ok-migration/source-untouched)
  - [critical] マーカーの外の本文を保つ。 (grader: 01-ng-caller-ok-migration/body-outside-kept)
  - 書き込み先を承認していない依頼では、検査結果ブロックを回答に返すだけで、どこにも書き込まない。 (grader: 未計測)

# Hold-out
- fixture: 作業ツリーに未 commit の変更が残っている。別の fixture では、検査項目表がどこにも無い。
- assertions:
  - [critical] 未 commit の変更があれば、検査結果ブロックを作らずにその旨を報告する。 (grader: 未計測)
  - [critical] 検査項目表が無ければ検査せず、表の列を示して表を求める。 (grader: 未計測)
