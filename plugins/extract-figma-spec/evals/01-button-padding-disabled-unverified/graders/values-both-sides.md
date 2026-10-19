---
type: llm
focus: {source: file, path: artifacts/figma-check.md}
weight: 0.5
---
一致または不一致と判定された各項目に、Figma の値と実装の値の両方が書かれていれば pass。判定された項目のどれかで片方の値が欠けていれば fail。

未検証の項目は、値が無いことが未検証の理由なので、値が欠けていても fail としない。
