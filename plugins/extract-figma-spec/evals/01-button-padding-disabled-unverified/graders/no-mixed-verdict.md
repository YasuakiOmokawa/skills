---
type: llm
focus: {source: file, path: artifacts/figma-check.md}
---
判定の付け方を見る。どの行も 1 つの属性について、一致・不一致・未検証のいずれか 1 つの判定だけを持っていれば pass。

複数の属性を 1 行にまとめて 1 つの判定にした行 (「文字: 一部一致」「font-family / weight / line-height: 未確認」など)、または「一部一致」「△」のような混合の判定がある場合は fail。判定の言い換え (差分あり、✅、❌、❓) は fail としない。
