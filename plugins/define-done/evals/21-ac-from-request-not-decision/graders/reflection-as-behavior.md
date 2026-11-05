---
type: llm
focus: {source: file, path: repo/plans/secret-rotation.md}
---
repo/plans/secret-rotation.md の受け入れ基準と、その検証の記述を評価する。「回した新しい値が staging に反映される」ことを観測する基準が、runbook に記述があることの基準とは別に 1 つ以上あれば pass。staging の実際の状態が要るので観測の前提が未解決 (未検証、要承認など) と書かれていてもよい。反映を runbook の記述の有無だけで扱っている、または反映を基準にしていなければ fail。
