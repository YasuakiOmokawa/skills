---
type: llm
focus: {source: file, path: src/auth-route.ts}
---
src/auth-route.ts を評価する。route の解決結果が、「method に写像できた」枝と「対象 route でない / provider が未知」を区別できる枝を持つ判別子付き union (または同等の型) で返され、未知 provider の枝がその provider 名 (params の id) を保持していれば pass。戻り値が `SignInMethod | undefined` / `| null` のままで 2 つの意味を 1 つの値に畳んでいれば fail。
