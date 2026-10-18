---
type: llm
focus: {source: file, path: repo/plans/just-signed-up.md}
---
repo/plans/just-signed-up.md の `## Acceptance Criteria` 節のうち、README と GLOSSARY.md への追加 (3.2 と 3.3) に対応する criterion だけを評価する。どの criterion も、追加する文・表の行・用語の説明文の全文と一字一句一致することを求めていなければ pass。識別子 (`isJustSignedUp`、用語の見出し) の存在と置き場所 (節、直前・直後の行) で確かめる形は pass。1 つでも全文の一致を求める criterion があれば fail。
