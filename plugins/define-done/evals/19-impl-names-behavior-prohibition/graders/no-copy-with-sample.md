---
type: llm
focus: {source: file, path: repo/plans/rate-limit.md}
---
repo/plans/rate-limit.md の `## Acceptance Criteria` と `## Verification Plan` を評価する。上限値を `config/limits.json` の外に写さないことの基準があり、その検証が、上限値を写したコードの具体的な例 (例を書き足すファイルと中身) を一時的に入れると、リポジトリの試験や検査が落ちることを確かめる形になっていれば pass。複数の基準や項目にまたがって示していてもよい。検索で `60` などの文字列が 0 件であることを確かめるだけで、例を入れて落ちることを確かめないなら fail。その基準が無ければ fail。
