---
type: llm
focus: {source: file, path: plans/mfa-policy.md}
---
この設計書に書き込まれた MECE レビューについて、次を満たすなら pass。

- `src/mfa/management/verify.ts` にも `MAX_ATTEMPTS = 5` のインライン定数があり、実装タスクにも受け入れ基準にもこのファイルが含まれていないことを、欠落・omission として報告している。

ファイル名 `verify.ts` を名指ししていることが必要。「他にも呼び出し元があるかもしれない」といった一般論だけでは fail。
レビュー中に verify.ts を覆う受け入れ基準やタスクを追加して解消した場合も、もともと計画から漏れていたと分かる形で書かれていれば pass。
