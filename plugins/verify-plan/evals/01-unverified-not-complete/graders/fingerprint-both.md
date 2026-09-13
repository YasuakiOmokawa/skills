---
type: llm
weight: 0.5
---
検証開始時と終了時の 2 時点で fingerprint (plan、HEAD、working tree の状態を要約した値) を取り、両方の値または一致・不一致の比較結果を報告していれば pass。

1 時点しか報告していない、または fingerprint の言及が無ければ fail。
