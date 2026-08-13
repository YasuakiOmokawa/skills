# QA-ID contract

各 AC `- [ ]` を一度だけ分類・連番化する。

| Category | Prefix |
|---|---|
| 正常系 | `QA-H-NN` |
| 異常系 | `QA-E-NN` |
| エッジケース | `QA-D-NN` |
| 不変条件 | `QA-I-NN` |
| 非影響確認 | `QA-R-NN` |
| `[MECE追加]` / `[MECE追加 変更]` | `QA-M-NN` |

MECE タグは見出し分類より優先し、base 5 categories と別に総数へ加算する。0件は ID を発行せず、理由文から AC を捏造しない。planner はこの結果を再分類しない。

全項目を分類不能なら user に `/define-acceptance-criteria` 再実行または手動ラベル付けを確認する。一部だけ不明なら `QA-X-NN` とし、planner に推測適用と Self-report 明記を指示する。質問不可時は SKILL.md の委譲規則を使う。
