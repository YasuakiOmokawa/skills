---
type: regex
target: {source: file, path: docs/billing-design.md}
match: contains
---
トークン検証は共通ミドルウェア `app/common/auth.py` が担い、課金側では再検証しない。
