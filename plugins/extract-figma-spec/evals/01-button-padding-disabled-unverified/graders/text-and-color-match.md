---
type: llm
focus: {source: file, path: artifacts/figma-check.md}
---
次の 2 項目を見る。

1. 文字サイズ (font-size。Figma 14、実装 14) が一致と判定されている。
2. 背景色 (ボタンの色。Figma #246BFD、実装 #246BFD) が一致と判定されている。

2 項目とも一致なら pass。どちらかが不一致、未検証、または項目が無ければ fail。文字色、ラベル文言、フォントの種類など他の項目が未検証でも、要約が「一部一致」となっていても、fail としない。
