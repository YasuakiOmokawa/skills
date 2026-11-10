---
type: regex
target: {source: file, path: repo/src/shipment.test.ts}
match: contains
flags: s
---
status: "preparing", trackingNumber: null, deliveredAt: null \}.*status: "shipped", trackingNumber: "ab12", deliveredAt: null \}.*status: "delivered", trackingNumber: "ab12", deliveredAt: "2026-04-03" \}
