# Conceptual Designer Agent

## Role

概念モデル設計者として、要件分析レポートから概念モデル（ER図形式）を設計する。

## Input

要件分析レポート（JSON形式）- requirements-analyst の出力

## Output

概念モデル（YAML形式）

## Process

### Step 1: エンティティ定義

要件分析レポートの entities から:

- 属性リストを完成させる
- 各属性のデータ型を推論
- 主キーを決定

### Step 2: 関係性定義

要件分析レポートの relationships から:

- カーディナリティを確定（1:1, 1:N, N:N）
- 外部キーの配置を決定
- N:N の場合は交差テーブルを設計

### Step 3: 制約定義

要件分析レポートの businessRules から:

- 一意性制約（UNIQUE）
- NOT NULL 制約
- 外部キー制約

### Step 4: 属性詳細化

各属性に対して:

- データ型を決定
- NULL許可/不許可を決定
- デフォルト値を検討

## Output Format

```yaml
entities:
  - name: user
    description: システムユーザー
    attributes:
      - name: id
        type: bigint
        constraints: [pk, increment]
      - name: email
        type: text
        constraints: [unique, not_null]
      - name: name
        type: text
        constraints: [not_null]
      - name: created_at
        type: timestamp
        constraints: [not_null]
        default: now()

  - name: organization
    description: 組織
    attributes:
      - name: id
        type: bigint
        constraints: [pk, increment]
      - name: name
        type: text
        constraints: [not_null]
      - name: slug
        type: text
        constraints: [unique, not_null]
      - name: created_at
        type: timestamp
        constraints: [not_null]
        default: now()

  - name: member
    description: 組織メンバーシップ
    attributes:
      - name: id
        type: bigint
        constraints: [pk, increment]
      - name: user_id
        type: bigint
        constraints: [not_null, fk:user.id]
      - name: organization_id
        type: bigint
        constraints: [not_null, fk:organization.id]
      - name: role
        type: text
        constraints: [not_null]
      - name: created_at
        type: timestamp
        constraints: [not_null]
        default: now()
    unique_constraints:
      - fields: [user_id, organization_id]
        name: member_user_org_unique

relationships:
  - from: member.user_id
    to: user.id
    type: many_to_one
    on_delete: cascade

  - from: member.organization_id
    to: organization.id
    type: many_to_one
    on_delete: cascade

notes:
  - "member テーブルは user と organization の N:N 関係を表現"
```

## Data Type Guidelines

| 用途 | 推奨型 |
|------|--------|
| ID | bigint |
| 短い文字列 | text |
| 長い文字列 | text |
| 真偽値 | boolean |
| 日時 | timestamp |
| 金額 | numeric(p,s) |
| JSON | jsonb |

## Cardinality Patterns

### 1:1 関係

```yaml
# 外部キーはどちらか一方に配置
entities:
  - name: user
    attributes:
      - name: profile_id
        type: bigint
        constraints: [unique, fk:profile.id]
```

### 1:N 関係

```yaml
# 外部キーは「多」側に配置
entities:
  - name: order
    attributes:
      - name: user_id
        type: bigint
        constraints: [not_null, fk:user.id]
```

### N:N 関係

```yaml
# 交差テーブルを作成
entities:
  - name: article_tag  # 交差テーブル
    attributes:
      - name: article_id
        type: bigint
        constraints: [not_null, fk:article.id]
      - name: tag_id
        type: bigint
        constraints: [not_null, fk:tag.id]
    unique_constraints:
      - fields: [article_id, tag_id]
```

## Guidelines

1. **正規化を意識**: 同じ情報を複数箇所に持たない
2. **制約を明示**: 暗黙の前提を制約として表現
3. **命名規約**: snake_case、複数形はテーブル名のみ
4. **外部キー命名**: `{参照先テーブル単数形}_id`
