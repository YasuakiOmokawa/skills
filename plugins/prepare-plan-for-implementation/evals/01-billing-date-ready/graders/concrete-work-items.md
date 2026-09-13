---
type: llm
focus: {source: file, path: plans/billing-date.md}
---
この設計書に書かれた実装のための作業項目 (`## Verification Plan` 以外の部分) について、次をすべて満たすなら pass。

- 作業項目が個別に列挙され、各項目に (a) 変更対象のファイルまたは対象 (`migrations/002_add_billing_day.sql`、`src/billing/date.ts`、`src/billing/customer.ts`、`src/billing/date.test.ts` のいずれか、または外部依存への引き継ぎ)、(b) 先行する項目または「先行なし」、(c) 対応する AC ID、(d) 検証方法、の 4 つが書かれている。
- 実行順序が依存関係に従っている。少なくとも、`customers.billing_day` 列を追加する項目が、`registerCustomer` で `billing_day` を保存する項目より前にある。
- `runBillingCycle` に関わる AC-004 の確認が、リポジトリ外の前提を伴う引き継ぎまたは未解決事項として明示されている。

次は fail としない。
- 作業項目の粒度が設計書の T-1〜T-4 と異なること。
- テスト追加を実装より前に置くこと (TDD)。

「網羅している」「対応済み」といった主張だけで具体的な項目が無い場合、または項目に変更対象が書かれていない場合は fail。
