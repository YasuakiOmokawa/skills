---
type: llm
focus: {source: file, path: src/removal-guard.ts}
---
src/removal-guard.ts を評価する。removal-policy 側の signature 変更に合わせて呼び出しが更新され、`canRemoveTarget` 相当の呼び出しが位置 boolean を渡さずに (名前付き引数、union 値、または関数分割で) 意図を読める形になっていれば pass。`canRemoveTarget(actor.role, isSelf, target.role)` のような位置 boolean の呼び出しが残っていれば fail。
