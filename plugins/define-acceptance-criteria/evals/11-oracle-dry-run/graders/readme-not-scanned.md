---
type: llm
focus: {source: file, path: repo/plans/remove-legacy.md}
---
repo/plans/remove-legacy.md の `## Acceptance Criteria` 節だけを評価する。S-1 (`src/` に `legacySignIn` が残らない) に対応する criterion の観測が、S-3 が変更後も残すと定める `src/README.md` の移行メモに当たらない形 (README を除く、走査対象を `.ts` などのコードに限る、など) になっていれば pass。観測が `src/` 全体をそのまま検索し、README の言及で落ちる形なら fail。S-1 に対応する criterion が無ければ fail。
