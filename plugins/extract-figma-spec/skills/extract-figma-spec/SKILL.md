---
name: extract-figma-spec
description: Use when supplied or retrievable Figma evidence must be decomposed into atomic checks and compared with an identified implementation for specified frames, states, or components in a design-difference table.
---

# Workflow

1. 依頼と利用可能な文脈から、対象フレーム、状態、部品、Figmaの根拠、実装の観測元、指定された比較成果物を特定する。
2. 提供された応答、書き出し、画面根拠、および実装の画像やコードから取得できる値を実際に観測する。
3. 複数の属性を含む項目を独立に観測できる単位へ分け、一項目につき一つの判定にする。
4. 各項目にFigmaの観測値、実装の観測値、双方の根拠、一致・不一致・未検証のいずれかを対応付ける。
5. 一方の根拠が欠ける項目や権限不足で取得できない項目だけを未検証とし、不足理由を示す。比較可能な残りの項目は判定を続ける。
6. 書き込みを指定された比較成果物に限定し、具体的な変更が別途承認されていないFigmaと実装は変更しない。
7. 保存後に成果物を読み直し、各原子項目とその判定が存在することを確認する。別途承認された変更を行った場合は、その反映も返却値または再取得した実状態から確認する。書き込み拒否があれば失敗として報告し、変更済みと扱わない。
8. 比較の正本となる判定表、アクセス不能または不足している証拠、失敗、未検証事項を返す。
