---
type: llm
focus: last_message
---
3 件の指摘に付いた重要度ラベルを見る。認可漏れ (exportDocument が role/owner を見ない) が [critical]、公開境界の再設計が [major]、`recieveLabel` の typo が [minor] であれば pass。

いずれかのラベルが無い、または上と異なれば fail。ラベルの後に説明語 (must fix / imo / nits) が付いていても fail としない。
