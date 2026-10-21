---
type: llm
focus: {source: file, path: plans/confirm-on-post.md}
---
plans/confirm-on-post.md の Acceptance Criteria 節を評価する。次の 3 つの基準がそれぞれ 1 つ以上あれば pass。
1. 確認が済んでいない受信者の承認の POST が 303 で確認画面へ戻され、承認の状態が変わらない。
2. 確認が済んでいない受信者の同意の POST が 303 で確認画面へ戻され、同意の状態が変わらない。
3. 確認が済んでいる受信者の承認または同意が成功する。
1 つでも欠ければ fail。
