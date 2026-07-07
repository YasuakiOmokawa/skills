# 結合度（Coupling）

## 概要

結合度とは、モジュール間の依存の強さを示す指標。
**低いほど良い**（変更の影響が局所化される）。

## 結合度のレベル（高→低）

```
┌─────────────────────────────────────────────────────────┐
│  高い結合度（悪い）                                      │
├─────────────────────────────────────────────────────────┤
│  内容結合: 他モジュールの内部を直接変更                  │
│  共通結合: グローバル変数を共有                          │
│  外部結合: 外部フォーマットを共有                        │
│  制御結合: フラグで動作を制御                            │
├─────────────────────────────────────────────────────────┤
│  スタンプ結合: 不要なフィールドを含む構造体を渡す        │
│  データ結合: 必要なデータのみ渡す                        │
│  メッセージ結合: 引数なしで通信                          │
├─────────────────────────────────────────────────────────┤
│  低い結合度（良い）                                      │
└─────────────────────────────────────────────────────────┘
```

## 各レベルの詳細

### 1. 内容結合（最悪）

他モジュールの非公開部分を直接変更。

```typescript
// ❌ 内容結合: private を無視してアクセス
class ModuleB {
  hack() {
    // @ts-ignore
    this.a.data.count = 999
  }
}

// ✅ 改善: 公開APIを使用
class ModuleB {
  update() {
    this.a.setCount(999)
  }
}
```

### 2. 共通結合

グローバル変数を共有。どこで変更されるかわからない。

```typescript
// ❌ 共通結合: グローバル変数を共有
let globalConfig = { apiUrl: "", timeout: 3000 }

class ApiClient {
  fetch(path: string) {
    return fetch(`${globalConfig.apiUrl}${path}`)
  }
}

// ✅ 改善: 依存性注入（DI）
class ApiClient {
  constructor(private config: Config) {}

  fetch(path: string) {
    return fetch(`${this.config.apiUrl}${path}`)
  }
}
```

### 3. 外部結合

外部フォーマット（ファイル形式、プロトコル）を共有。

### 4. 制御結合

フラグ引数で他モジュールの動作を制御。

```typescript
// ❌ 制御結合: フラグで内部動作を制御
function getUser(id: string, includeDeleted: boolean) {
  if (includeDeleted) {
    return db.users.findFirst({ where: { id } })
  } else {
    return db.users.findFirst({ where: { id, deletedAt: null } })
  }
}

// ✅ 改善: 別関数に分離
function getUser(id: string) {
  return db.users.findFirst({ where: { id, deletedAt: null } })
}
function getUserIncludingDeleted(id: string) {
  return db.users.findFirst({ where: { id } })
}
```

### 5. スタンプ結合

不要なフィールドを含む構造体を渡す。

```typescript
// ❌ スタンプ結合: name と email しか使わないのに User 全体
function sendWelcomeEmail(user: User) {
  sendEmail(user.email, `Welcome, ${user.name}!`)
}

// ✅ 改善: 必要なフィールドのみ
function sendWelcomeEmail(recipient: EmailRecipient) {
  sendEmail(recipient.email, `Welcome, ${recipient.name}!`)
}
```

**Rails での注意**: ActiveRecord オブジェクトを渡すのは標準的。過度に指摘しない。
指摘するのは「使用属性が1-2個だけ + Service等の外部モジュール」の場合のみ。

### 6. データ結合

必要なプリミティブデータのみを渡す。良い設計。

### 7. メッセージ結合（最良）

引数なしで通信。最も疎結合。

## 意味的な検出基準

### 内容結合の検出

以下の特徴を持つコードを検出:
- `instance_variable_set`, `send(:private_method)` 等で非公開部分を直接操作
- モンキーパッチによる既存クラスの改変

### 共通結合の検出

以下の特徴を持つコードを検出:
- グローバル変数（`$`プレフィックス）への依存
- `ENV[]` がモジュール全体に散在

### 制御結合の検出

以下の特徴を持つコードを検出:
- boolean引数で内部動作を完全に分岐させている
- 呼び出し側が被呼び出し側の内部実装を知る必要がある

### デメテルの法則違反の検出

以下の特徴を持つコードを検出:
- メソッドチェーンが3つ以上（`a.b.c.d`）で、途中のオブジェクトが自身の直接の協力者でない
- ただし、ActiveRecordのクエリビルダーチェーンやFluentインターフェースは除外

### 循環依存の検出

以下の特徴を持つコードを検出:
- A→B→A の相互参照（require/import レベル）
- クラスが相互にメソッドを呼び合う関係

### spec-coverage-gap (新規 attribute 値 / 新規 branch に対する spec context 不在) の検出

以下の特徴を持つ場合は coupling-analyzer の責務として検出する:
- impl 側で enum / state に新しい値を追加したが、対応する spec context (`describe '<新値>のとき'` / `context 'when <新値>'`) が存在しない
- impl 側で新しい分岐 (新しい if/case ブランチ / Policy の権限ロール追加 / Job の status 値追加) を追加したが、当該ブランチを通る spec が無い
- グローバル `~/.claude/rules/ruby-coding.md` (存在しない環境では参照せず判定を進める) の「caller 経路 spec を audit」要件と整合: 新規 attribute 値 → caller spec の stub なし context 探索 → 当該 context 不在を Important で報告
- **報告前の実在確認 (必須)**: 「spec context 不在」を報告する前に、対応する spec ファイルを grep し (`grep -n '<新値/分岐キーワード>' spec/<対応ファイル>`)、同カバレッジの spec が本当に無いことを確認する。既存 spec が別の書き方 (共有 example / 別名 context / 値の直接検証) で同じ分岐を既に通している場合は報告しない (既存 spec で網羅済みの gap を報告した誤検出の実績がある)

## トレードオフ

**注意**: 「すべてメッセージ結合にしろ」ではない。

| 状況 | 許容される結合度 |
|------|------------------|
| 設定値 | データ結合（プリミティブで渡す） |
| ドメインオブジェクト | スタンプ結合（ただし最小限） |
| 環境変数 | 共通結合（ただし1箇所で管理） |
| ライブラリ | 外部結合（インターフェースで隔離） |

重要なのは、**依存を明示化**し、**変更の影響範囲を把握**していること。
