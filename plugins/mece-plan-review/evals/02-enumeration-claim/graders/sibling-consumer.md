---
type: llm
focus: {source: file, path: plans/mfa-policy.md}
---
この設計書に書き込まれた MECE レビューについて、次を満たすなら pass。

- `src/mfa/recovery/reset.ts` が MFA の試行回数上限と同じ値 5 を `RESET_ATTEMPT_CAP` という別名でインライン定義しており、仕様 S-1 の「一箇所だけ定義する」に対して、このファイルが実装タスクにも受け入れ基準にも含まれていないことを、欠落・omission として報告している。

判定の要点。
- ファイル名 `reset.ts`、パス `src/mfa/recovery/`、または定数名 `RESET_ATTEMPT_CAP` のいずれかで対象を特定できていればよい。
- 定数名が `MAX_ATTEMPTS` と異なるため、名前の一致だけでは見つからない。別名で同じ上限を持つ箇所として扱えていれば pass。
- 「他にも重複があるかもしれない」「リポジトリ全体を確認すべき」といった一般論だけでは fail。
- レビュー中に reset.ts を覆う受け入れ基準やタスクを追加して解消した場合も、もともと計画から漏れていたと分かる形で書かれていれば pass。
