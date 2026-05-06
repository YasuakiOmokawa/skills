# コード可読性（Readability）

## 5原則

| 原則 | 説明 |
|------|------|
| ボーイスカウト・ルール | 見つけたときより少しきれいにして去る |
| YAGNI | 必要な時にのみ実装（将来機能の90%は使用されない） |
| KISS | シンプルさを重視（美しいコード ≠ 可読性の高いコード） |
| 単一責任原則 | クラスは変更理由を1つだけ持つべき |
| 過度な最適化の回避 | 97%の最適化は悪の根源（Knuth） |

## ネーミング原則

### 良い名前の3要素

1. **正確性**: 実際の動作を正確に表現
2. **記述的**: 名前だけで意図がわかる
3. **曖昧性排除**: 複数の解釈ができない

### 要素別の命名規則

| 要素 | 形式 | 例 |
|------|------|-----|
| 型・値 | 名詞 | `imageView`, `HashSet`, `userCount` |
| 手続き | 命令形 | `findMessage`, `compareTo`, `calculateTotal` |
| ブール値 | 疑問形 | `isVisible`, `contains`, `hasPermission` |
| 変換器 | 前置詞付き | `toInt`, `fromMemberId`, `asString` |

### 重要なルール

#### 本質的な単語を最後に

```typescript
// ✅ 良い: 本質が最後
MessageEventHandler  // Handler が本質
UserRepository       // Repository が本質

// ❌ 悪い: 本質が最初
HandlerMessageEvent
RepositoryUser
```

#### 「何（What）」を説明

```typescript
// ✅ 良い: 何をするかが明確
storeReceivedMessage()
calculateTotalPrice()

// ❌ 悪い: いつ呼ばれるかしかわからない
onMessageReceived()
handleClick()
```

#### 曖昧な単語を避ける

```typescript
// ❌ 悪い: 曖昧
let flag = true
let data = fetchData()
let check = validate()

// ✅ 良い: 具体的
let isInitializing = true
let userProfile = fetchUserProfile()
let isEmailValid = validateEmail()
```

#### ブール値は肯定形

```typescript
// ✅ 良い: 肯定形
isEnabled, isVisible, hasPermission

// ❌ 悪い: 否定形（二重否定で混乱）
isDisabled    // if (!isDisabled) → 二重否定
isNotVisible  // if (!isNotVisible) → 二重否定
```

### よく使われる動詞

| 動詞 | 用途 | 例 |
|------|------|-----|
| `get` | プロパティ取得 | `getName()` |
| `find` | 検索（見つからない可能性あり） | `findUserById()` |
| `fetch` | 外部から取得 | `fetchOrders()` |
| `create` | 新規作成 | `createUser()` |
| `update` | 更新 | `updateProfile()` |
| `delete` | 削除 | `deleteOrder()` |
| `validate` | 検証 | `validateInput()` |
| `calculate` | 計算 | `calculateTotal()` |
| `format` | 整形 | `formatDate()` |
| `parse` | 解析 | `parseJson()` |

## コメント指針

### コメントが必要な場合

1. **意図の伝達**: コードだけでは伝わらない「なぜ」
2. **間違い防止**: 注意事項の記述
3. **複雑なアルゴリズム**: ロジックの概要説明

### コメント判定フロー

```
名前とシグネチャだけで明確か？
    │
    ├── YES → コメント不要
    │
    └── NO → コメントを記述（Why を説明）
```

### 良いコメントの例

```typescript
// ✅ 良い: Why を説明
// 在庫数は競合更新が頻繁なため、楽観ロックではなく悲観ロックを採用
function reserveStock(): void { ... }

// ✅ 良い: 判断根拠を具体的に記載
// 月間100件以下のため、N+1を許容（最適化は月間1000件超えてから）
function listItems() { ... }

// ✅ 良い: 技術的負債の理由を明記
// FIXME: 外部APIの仕様変更待ち。v2 APIがリリースされたらリトライロジックを削除
function callExternalApi() { ... }
```

### 悪いコメントの例

```typescript
// ❌ 悪い: What を説明（コードを読めばわかる）
// ユーザー名を返す
function getUserName() { return this.name }

// ❌ 悪い: 空の JSDoc
/**
 * @param {string} name
 * @returns {User}
 */
function createUser(name: string): User { ... }

// ❌ 悪い: 古くなった情報
// TODO: 後で直す（2年前のコメント）
function legacyFunction() { ... }
```

### FIXME/TODO の書き方

```typescript
// ✅ 良い: 妥協理由と理想の実装を明記
// FIXME: 外部API制約で同期処理。v3 APIで非同期対応後、Effect.forkに移行

// ✅ 良い: 期限と担当を明記
// TODO(yamada, 2024-Q2): パフォーマンス改善。現状100ms、目標30ms

// ❌ 悪い: 理由がない
// TODO: リファクタする
```

## 意味的な検出基準

### 曖昧な命名の検出

以下の名前をコード内で検出:
- `flag`, `data`, `check`, `info`, `temp`, `result`, `handle`
- メソッド名が「いつ呼ばれるか」のみ表現（`onXxx`, `handleXxx`）

### 否定形ブール値の検出

以下のパターンを検出:
- `is_not_`, `isNot`, `!is_`, `isDisabled`, `isHidden` 等の否定形

### 構造的問題の検出

以下の閾値を超えるコードを検出:
- ファイル行数 > 300行
- メソッド行数 > 50行
- ネスト深さ > 3レベル
- 引数の数 > 4個

## 言語別の追加ルール

### TypeScript

```typescript
// 型名は PascalCase
type UserProfile = { ... }

// 定数は SCREAMING_SNAKE_CASE
const MAX_RETRY_COUNT = 3
```

### Ruby

```ruby
# メソッド名は snake_case
def calculate_total_price; end

# 述語メソッドは ? で終わる
def valid?; end

# 破壊的メソッドは ! で終わる
def normalize!; end
```
