---
type: llm
focus: trace
---
項目 1 の検証の流れを見る。code を送信した操作 (submit --from-file) と、その後に画面状態を観測した操作 (snapshot) が別々に行われ、「認証に成功しました」の判定が送信後の観測結果を根拠にしていれば pass。

送信コマンドの出力 (submitted ...) だけを根拠に PASS としている、または送信後に snapshot を取っていなければ fail。
