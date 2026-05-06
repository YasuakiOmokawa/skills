# 凝集度（Cohesion）

## 概要

凝集度とは、モジュール内の要素がどれだけ密接に関連しているかを示す指標。
**高いほど良い**（単一の責務に集中している）。

## 凝集度のレベル（低→高）

```
┌─────────────────────────────────────────────────────────┐
│  低い凝集度（悪い）                                      │
├─────────────────────────────────────────────────────────┤
│  偶発的凝集: 無関係な処理の寄せ集め                      │
│  論理的凝集: フラグで処理を分岐                          │
│  時間的凝集: 同時期に実行するだけ                        │
│  手順的凝集: 順序は決まっているが関連薄い                │
├─────────────────────────────────────────────────────────┤
│  通信的凝集: 同じデータを操作                            │
│  逐次的凝集: 出力が次の入力になる                        │
│  機能的凝集: 単一機能のみ                                │
├─────────────────────────────────────────────────────────┤
│  高い凝集度（良い）                                      │
└─────────────────────────────────────────────────────────┘
```

## 各レベルの詳細

### 1. 偶発的凝集（最悪）

無関係な処理をまとめただけ。

```typescript
// ❌ 偶発的凝集: 無関係な処理の寄せ集め
class Utilities {
  formatDate(date: Date) { ... }
  calculateTax(amount: number) { ... }
  sendEmail(to: string, body: string) { ... }
  validatePassword(password: string) { ... }
}

// ✅ 改善: 責務ごとに分離
class DateFormatter { formatDate(date: Date) { ... } }
class TaxCalculator { calculateTax(amount: number) { ... } }
class EmailSender { sendEmail(to: string, body: string) { ... } }
class PasswordValidator { validatePassword(password: string) { ... } }
```

### 2. 論理的凝集

フラグ引数で処理を分岐。呼び出し側が内部実装を知る必要がある。

```typescript
// ❌ 論理的凝集: フラグで分岐
function sendMessage(type: "text" | "stamp" | "image", content: string) {
  switch (type) {
    case "text":
      return sendTextMessage(content)
    case "stamp":
      return sendStampMessage(content)
    case "image":
      return sendImageMessage(content)
  }
}

// ✅ 改善: ユースケースごとに分離
function sendTextMessage(text: string) { ... }
function sendStampMessage(stampId: string) { ... }
function sendImageMessage(imageUrl: string) { ... }
```

### 3. 時間的凝集

同時に実行するだけで、論理的な関連はない。

```typescript
// ❌ 時間的凝集: 初期化時に実行するだけ
function initializeApp() {
  setupLogger()
  connectDatabase()
  loadConfig()
  initializeCache()
  sendStartupNotification()  // これは初期化と関係ない
}
```

### 4. 手順的凝集

順序は決まっているが、値の受け渡しがない。

```typescript
// ❌ 手順的凝集: 順序依存だが値の受け渡しなし
function processFile(path: string) {
  checkFileExists(path)    // 結果を使わない
  validateFileFormat(path) // 結果を使わない
  readFile(path)           // 前の結果を使わない
}

// ✅ 改善: 逐次的凝集に（値を受け渡す）
function processFile(path: string) {
  const exists = checkFileExists(path)
  if (!exists) throw new Error("File not found")
  const content = readFile(path)
  return parseFile(content)
}
```

### 5. 通信的凝集

同じデータを操作する処理をまとめている。許容範囲だが注意。

### 6. 逐次的凝集

ある処理の出力が次の処理の入力になる。良い設計。

```typescript
// ○ 逐次的凝集: 出力→入力の連鎖
function processOrder(rawData: string) {
  const parsed = parseOrderData(rawData)
  const validated = validateOrder(parsed)
  const calculated = calculateTotal(validated)
  return formatReceipt(calculated)
}
```

### 7. 機能的凝集（最良）

単一の機能のみを持つ。

## 意味的な検出基準

### 偶発的凝集の検出

以下の特徴を持つクラス/モジュールを検出:
- メソッド群が共通のデータ（インスタンス変数）を一切共有しない
- クラス名が汎用的（`Utilities`, `Helpers`, `Common`, `Misc`）
- 「このクラスは何をするクラス？」に一言で答えられない

### 論理的凝集の検出

以下の特徴を持つメソッド/関数を検出:
- 引数の値によって実行パスが完全に分岐（case/switch/if-else）
- 分岐先が相互に独立した処理（共通のデータフローがない）
- メソッド名が抽象的（`process`, `handle`, `execute` 等）

### 複数責務の検出

以下の特徴を持つクラスを検出:
- 「〜と〜」のようにANDで責務を説明する必要がある
- publicメソッドが5つ以上で、グループ間に共通のインスタンス変数がない

## トレードオフ

**注意**: 「すべて機能的凝集にしろ」ではない。

| 状況 | 許容される凝集度 |
|------|------------------|
| ユーティリティクラス | 通信的凝集（同じドメインのユーティリティ） |
| 初期化処理 | 時間的凝集（ただし分離を意識） |
| パイプライン処理 | 逐次的凝集 |
| 単純な関数 | 機能的凝集を目指す |

重要なのは、**意図的に選択**し、**トレードオフを理解**していること。

## 凝集度と結合度の関係

**重要な洞察**: 論理的凝集度を改善すれば、制御結合を回避でき、自然と結合度も低下する。

```
論理的凝集（フラグで分岐）
    ↓ 改善
機能的凝集（ユースケースごとに分離）
    ↓ 結果
制御結合が解消 → 結合度も低下
```

**結論**: 凝集度の改善が基礎。凝集度を高めれば結合度も自然と改善される。
