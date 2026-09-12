---
max_turns: 8
timeout_seconds: 300
allowed_tools: [Skill, Read]
runs: 3
---
次の設計を実装前にレビューして。保存は不要、回答で返して。

## 設計

### 変更 1: SessionStore からトークンキャッシュを分離する
- 現在 SessionStore が持つ `cacheToken` / `getCachedToken` を新クラス TokenCache に移す。
- SessionStore は `save` / `load` だけを持つ。

### 変更 2: 鍵ローテーション手順を SessionStore に追加する
- 暗号鍵 (KEK) を 90 日ごとに更新する `rotateKey()` を SessionStore に追加する。
- 手順の詳細は docs/spec/key-rotation.md に従う。

## 参照可能な証拠

注意: docs/spec/key-rotation.md はこのリクエストでは参照できない (アクセス権がない)。それ以外は以下のとおり。

```md
# docs/spec/session.md
- SS-1: セッション本体とトークンキャッシュは独立に失効できなければならない。
- SS-2: セッション保存は暗号化する。鍵管理は docs/spec/key-rotation.md を参照。
```

```ts
// src/session-store.ts
export class SessionStore {
  constructor(private redis: RedisLike, private kek: Buffer) {}

  async save(id: string, s: Session) {
    await this.redis.set(`sess:${id}`, encrypt(this.kek, JSON.stringify(s)));
  }
  async load(id: string): Promise<Session | null> {
    const v = await this.redis.get(`sess:${id}`);
    return v ? JSON.parse(decrypt(this.kek, v)) : null;
  }

  // トークンキャッシュ。セッション本体とは別 key 空間で、互いを参照しない。
  async cacheToken(hash: string, userId: string) {
    await this.redis.set(`tok:${hash}`, userId, { ttl: 300 });
  }
  async getCachedToken(hash: string): Promise<string | null> {
    return this.redis.get(`tok:${hash}`);
  }
}
```

```ts
// src/__tests__/session-store.test.ts
it("token cache は session の失効に影響されない", async () => {
  await store.cacheToken("h", "u1");
  await redis.del("sess:u1");
  expect(await store.getCachedToken("h")).toBe("u1");
});
```
