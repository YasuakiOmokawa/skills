# Detailed Workflow（複雑なケース用）

Quick Start (Q1-Q3) + Parallel Review で解決しない場合のみ実行する。

## 1. プロジェクト構造の把握

CLAUDE.md と `.claude/rules/` を読み込み、以下を抽出:
- レイヤー構成（services/, domain/, layers/ など）
- 命名規則（kebab-case, PascalCase など）
- 既存のパターン（Service, Repository, Handler など）

## 2. 配置場所の決定

| 観点 | 確認事項 |
|------|----------|
| ディレクトリ | 既存構造のどこに配置するか？ |
| ファイル名 | 命名規則に従っているか？ |
| モジュール | 既存モジュールに追加 or 新規作成？ |

**判断基準**: 類似機能のファイルを探し、同じパターンに従う。なければ CLAUDE.md に従う。

## 3. 依存関係の確認

| 原則 | 確認事項 |
|------|----------|
| 依存方向 | 依存性は内側（上位レベル）に向かっているか？ |
| 逆方向依存 | ドメイン層がフレームワーク/DB/UIに依存していないか？ |
| 依存逆転 | インターフェースで逆転すべき箇所はないか？ |

**典型的な違反パターン**:
```
# ❌ 違反: ドメイン層が外側に依存
domain/user.ts → import { db } from 'drizzle'

# ✅ 正しい: 依存逆転
domain/user.ts → UserRepository (interface)
services/user-service.ts → implements UserRepository
```

## 4. 類似実装の参照

同種のファイルを検索し、以下を確認:
- 実装パターン
- エラーハンドリングのパターン
- DI（依存性注入）の方式

## 5. アーキテクチャパターンの選択

| 状況 | 推奨パターン |
|------|-------------|
| 外部 API/DB を差し替えたい | Port/Adapter |
| ビジネスルールが複雑 | Entity/Value Object |
| 複数オブジェクトの整合性が必要 | Aggregate |
| 単純な CRUD | シンプルな Service |

## 6. 責務分割方針の決定

- 責務が一言で言えるか？ → 1ファイルで実装
- 「〜と〜」になる → レイヤーごとに分割
- 共通処理あり → ユーティリティに抽出

## 7. 設計判断の出力 + Parallel Review

設計判断をまとめた後、SKILL.md の Parallel Review Workflow (Step 3-4) を実行。
