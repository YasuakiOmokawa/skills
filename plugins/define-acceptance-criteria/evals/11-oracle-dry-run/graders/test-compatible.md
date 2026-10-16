---
type: llm
focus: {source: file, path: repo/plans/remove-legacy.md}
---
repo/plans/remove-legacy.md の `## Acceptance Criteria` 節だけを評価する。S-1 (`src/` に `legacySignIn` が残らない) の criterion と、S-2 (`legacySignIn` を export しないことを test で確かめる) の criterion が、同時に成立し得るなら pass。たとえば S-1 の観測が test file (`__tests__` など) を走査対象から外している、または S-2 の test が `legacySignIn` の文字列を書かずに確かめると定めている、などで両立していれば pass。S-1 の観測が S-2 の test file に書かれる `legacySignIn` の文字列に当たって必ず落ちる形なら fail。複数の criterion にまたがって両立を示していてもよい。
