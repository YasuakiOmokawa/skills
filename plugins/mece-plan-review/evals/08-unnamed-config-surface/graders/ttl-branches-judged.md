---
type: llm
focus: {source: file, path: plans/cache-ttl.md}
---
この設計書に書き込まれた MECE レビューについて、次を満たすなら pass。

- AC-001 / AC-002 / AC-003 のそれぞれについて、`src/cache/ttl.ts` の `resolveTtlSeconds` または `src/cache/index.ts` を根拠に、対応の有無を項目単位で判定している。

判定の形式は問わない。対応表でも本文でもよい。根拠としてファイル名または行番号が示されていればよい。
AC-002 が列挙する 4 つの入力のうち一部だけに触れていても、既定値へ倒れる分岐として一括で判定していれば pass。
