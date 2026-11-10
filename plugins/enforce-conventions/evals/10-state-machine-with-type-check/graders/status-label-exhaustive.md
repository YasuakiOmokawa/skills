---
type: llm
focus: {source: file, path: repo/src/shipment.ts}
---
repo/src/shipment.ts の statusLabel だけを評価する。status の値を名指しせずに受ける枝 (if の列の後に続く無条件の return、default の枝、else の枝) が、文字列のラベルを返していれば fail。そういう枝が無ければ pass。3 つの status をすべて case か if で名指ししている switch や if の列は pass。never 型を受けるだけの枝は、名指しせずに受ける枝に数えない。
