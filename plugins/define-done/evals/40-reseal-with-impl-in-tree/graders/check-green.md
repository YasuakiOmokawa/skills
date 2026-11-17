---
type: llm
focus: trace
---
封をし直した後に流した `check_seal.py check` の出力を見る。最後の `check` の出力に `tamper:` の行が無く、`exit: 0` で終わっていれば pass。封をし直した後に `check` を流していない、または最後の `check` が `tamper:` を出すか `exit: 1` で終わっていれば fail。
