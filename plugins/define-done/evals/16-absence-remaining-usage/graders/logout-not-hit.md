---
type: llm
focus: {source: file, path: repo/plans/read-session.md}
---
repo/plans/read-session.md の `## Acceptance Criteria` と `## Verification Plan` を評価する。S-2 (`readSession` 以外が `getCookie` を直接使わない) に対応する基準の観測が、変更後も残る `src/logout.ts` の `deleteCookie` の import と呼び出しに当たらない形なら pass。

- `getCookie` を検索語にする、`src/read-session.ts` だけを許す形にする、などで `src/logout.ts` に当たらなければ pass。
- `cookie-kit` の import が `src/` に 0 件、のように `src/logout.ts` の `import { deleteCookie } from "cookie-kit"` に当たって必ず落ちる形なら fail。
- S-2 に対応する基準が無ければ fail。
