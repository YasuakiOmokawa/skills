---
type: llm
focus: {source: file, path: plans/billing.md}
---
この設計書に書き込まれた MECE レビューについて、次を満たすなら pass。

- `createInvoice` が呼ぶ先にあるアクセス判定の失敗分岐が、受け入れ基準にも実装タスクにも覆われていないことを報告している。対象は `src/billing/access.ts` の `checkBillingAccess` が返す `{ allowed: false }` の 2 経路、すなわち利用停止 (`suspended`) と権限不足 (`no-permission`) である。

判定の要点。
- `access.ts`、`checkBillingAccess`、`suspended`、`no-permission` のいずれかで対象を特定できていればよい。2 経路の片方だけでも pass。
- 変更対象表が `src/billing/create.ts` と `src/billing/retry.ts` しか挙げていないのに対し、失敗分岐はそこから 2 段先の定義にある。呼び出し先を辿らずに「失敗時の扱いが未定義」と一般論で書いただけなら fail。
- レビュー中にこの分岐を覆う受け入れ基準を追加して解消した場合も、もともと覆われていなかったと分かる形で書かれていれば pass。
