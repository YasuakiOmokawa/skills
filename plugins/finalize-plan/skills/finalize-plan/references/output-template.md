# Plan output contract

```markdown
---

## 実装準備

### 手動QA手順

**環境**: {BASE_URL}
**必要な権限種別**: <AC に必要な権限と用途>
**対象AC**: N項目（正常系X / 異常系Y / エッジケースZ / 不変条件U / 非影響W / MECE追加V）

[各操作に automation tool 名を併記した、人間がそのまま追える QA-ID 別手順]

正本カバレッジ: <skip / 差分 0 件 (...) / 補完 N 件 (再実行で差分 0 件)>

### 自動QA（テストコード仕様）

[RSpec / Vitest 仕様]
```

6カテゴリ名と0件を常に表示する。lite の auto 本文は次の一行だけにする。

```text
自動QA: lite tier のため対象外 (auto 0 件)
```

正本なしの canonical 行:

```text
正本カバレッジ: skip (構造化正本なし、または分析ファイル空)
```

他の canonical 行は `正本カバレッジ: 差分 0 件 (<counts>)` と `正本カバレッジ: 補完 N 件 (再実行で差分 0 件)`。

coverage 行は manual 末尾、auto 見出し直前に置く。fallback 備考は `## 実装準備` 直下に置く。
