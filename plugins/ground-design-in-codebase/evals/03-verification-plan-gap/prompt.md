---
max_turns: 8
timeout_seconds: 300
allowed_tools: [Skill, Read]
runs: 3
---
以下の設計を、既存コードとテストに照らして実装前にレビューして。

## 設計: findMember の戻り値を nullable にする

### 変更
- MemberRepository.findMember の戻り値を `Member` から `Member | null` に変える。見つからない場合は throw ではなく null を返す。
- 呼び出し側 (src/service.ts) で null を分岐する。
- src/repository.ts の findMember 直上に、null を返す理由と移行方針を説明するコメントブロック (3 行) を追加する。

### 検証計画
- `tsc --noEmit` が通ること。

## 既存コード

```ts
// src/repository.ts
export type Member = { id: string; role: "OWNER" | "ADMIN" | "MEMBER" };

export class MemberRepository {
  constructor(private rows: Member[]) {}

  // 見つからない id は呼び出し側のバグとみなし throw する
  findMember(id: string): Member {
    const m = this.rows.find((r) => r.id === id);
    if (!m) throw new Error(`member not found: ${id}`);
    return m;
  }
}
```

```ts
// src/service.ts
import { MemberRepository } from "./repository";
export function roleOf(repo: MemberRepository, id: string) {
  return repo.findMember(id).role;
}
```

```ts
// src/__tests__/repository.test.ts
import { describe, it, expect } from "vitest";
import { MemberRepository } from "../repository";

const repo = new MemberRepository([{ id: "u1", role: "OWNER" }]);

describe("findMember", () => {
  it("存在する id を返す", () => {
    const m = repo.findMember("u1");
    expect(m.role).toBe("OWNER");
  });
  it("存在しない id は throw", () => {
    expect(() => repo.findMember("zz")).toThrow(/not found/);
  });
});
```

```ts
// src/__tests__/comment-budget.test.ts
// src/ 配下のコメント行数は BUDGET と完全一致でなければならない (増減どちらも fail)。
import { it, expect } from "vitest";
import { countCommentLines } from "../../scripts/comment-budget";

const BUDGET = 12;
it("コメント予算は完全一致", () => {
  expect(countCommentLines("src")).toBe(BUDGET);
});
```
