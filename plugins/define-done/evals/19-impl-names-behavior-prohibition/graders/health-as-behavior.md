---
type: llm
focus: {source: file, path: repo/plans/rate-limit.md}
---
repo/plans/rate-limit.md の `## Acceptance Criteria` と `## Verification Plan` を評価する。`/health` に関する基準が、`/health` の応答 (status 200 と body `ok`) が変わらないことを、`handle` を呼ぶか既存の試験を実行して観測する形なら pass。基準か観測が `src/health.js` のファイルが変わらないこと (git diff が空、ファイルを編集しない、など) を求めているなら fail。`/health` に関する基準が無ければ fail。
