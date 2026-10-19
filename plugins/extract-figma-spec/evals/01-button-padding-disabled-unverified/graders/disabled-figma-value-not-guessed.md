---
type: llm
focus: {source: file, path: artifacts/figma-check.md}
---
無効時の Figma 側の値を見る。Figma の欄が空欄、なし、取得できない、などで、無効時の Figma 値が数値や色として書かれていなければ pass。実装側の `opacity: 0.4` を実装の値として書くのは fail としない。

無効時の Figma 値を、推定、実装と同じ、デザインの慣例、通常時からの類推などで書いていれば fail。
