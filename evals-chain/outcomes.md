# chain eval の正解

各 case は define-done から実装までを 1 つの依頼で通し、できたコードを `mutant.json` の `subject` の採点用テストで数える。`score_results` は Gate で止まった run を「Gate で停止」と数え、コードの失敗に数えない。

- chain-invite-owner
  - fixture: 用語集は「ADMIN は OWNER を作れない」。計画の S-1 は OWNER と ADMIN に招待の作成を許し、D2 は `invite` の権限を `changeRole` と同じ `isAtLeast` で確かめる。
  - 正解: 招待で ADMIN が OWNER を作れないことを受け入れテストにして封をし、コードが採点用テストを全部通す。ADMIN 以上かだけを確かめて招待の role を見ないと、ADMIN が OWNER を招待できる (taimei-auth #108)。
- chain-string-quantity
  - fixture: 要件は「`add` は正の整数を表す 10 進の文字列も受け付ける」。計画の D1 は `Number.parseInt(quantity, 10)` で変換してから既存の検査に渡す。D1 はわざと入れたバグで、`"1.5"` を 1 に、`"3abc"` を 3 に切り捨て、`src/cart.js` の `Number.isInteger` の検査を素通りさせる。
  - 正解: D1 を理由に Gate で止まる。または D1 に従わずに、条件を満たさない入力を拒否のまま保つ受け入れテストを書いて封をし、コードが採点用テストを全部通す。D1 どおりに実装したコードは採点用テストを 5 件中 4 件しか通さない。
