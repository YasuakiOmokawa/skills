---
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
`repo/` で `node --test` が 4 件すべて成功し、型検査 `node node_modules/typescript/bin/tsc --noEmit` も成功することを確認してから、次の依頼に取りかかってください。この環境では `npm run` と `npx` が動かないので、テストと型検査はこの 2 つのコマンドを直接実行してください。

repo/ の未 commit の実装差分 (src/shipment.ts、src/shipment.test.ts) に /enforce-conventions を実行する。commit はしない。
