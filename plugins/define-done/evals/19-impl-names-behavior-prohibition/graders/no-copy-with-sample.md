---
type: llm
focus: {source: file, path: repo/plans/rate-limit.md}
---
repo/plans/rate-limit.md の `## Acceptance Criteria` と `## Verification Plan` を評価する。上限値を `config/limits.json` の外に写さないことの基準があり、その検証が次の 2 つを両方持てば pass。複数の項目にまたがって示していてもよい。
- 上限値を写したコードの具体的な例 (書き足すファイルと中身)。
- その例に当たる検索の文字列の pattern と、走査する範囲。

例を持たず、検索で `60` などが 0 件であることだけを確かめる形なら fail。その基準が無ければ fail。
