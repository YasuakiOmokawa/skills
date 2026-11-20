---
type: llm
focus: trace
---
凍結し直した後に流した `check_seal.py check` の出力を見る。最後の `check` の出力に `tamper:` の行が無く、`acs:` の行が AC-003 を含まず、`exit: 0` で終わっていれば pass。凍結し直した後に `check` を流していない、最後の `check` が `tamper:` を出す、`acs:` の行が AC-003 を含む、`exit: 1` で終わる、のどれかなら fail。
