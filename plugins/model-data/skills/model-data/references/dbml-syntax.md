# DBML Syntax Reference

## Overview

DBML (Database Markup Language) はデータベーススキーマを定義するための DSL。
dbdiagram.io で視覚化可能。

## Table Definition

```dbml
Table table_name {
  column_name data_type [constraints]
}
```

### Data Types

| DBML | PostgreSQL |
|------|------------|
| `int` | integer |
| `bigint` | bigint |
| `text` | text |
| `varchar(n)` | character varying(n) |
| `boolean` | boolean |
| `timestamp` | timestamp |
| `date` | date |
| `json` | json |
| `jsonb` | jsonb |

### Constraints

| 構文 | 意味 |
|------|------|
| `[pk]` | 主キー |
| `[pk, increment]` | 自動増分主キー |
| `[unique]` | ユニーク制約 |
| `[not null]` | NOT NULL |
| `[null]` | NULL許可（明示） |
| `[default: value]` | デフォルト値 |
| `[default: `now()`]` | SQL式（バッククォート） |
| `[note: 'text']` | コメント |

### Example

```dbml
Table users {
  id bigint [pk, increment]
  email text [unique, not null]
  name text [not null]
  is_active boolean [default: true]
  created_at timestamp [default: `now()`]
  updated_at timestamp

  Note: 'ユーザーマスタテーブル'
}
```

## References (Foreign Keys)

### Inline Reference

```dbml
Table orders {
  id bigint [pk, increment]
  user_id bigint [ref: > users.id, not null]
}
```

### Explicit Reference

```dbml
Ref: orders.user_id > users.id
```

### Cardinality

| 構文 | 意味 |
|------|------|
| `>` | many-to-one |
| `<` | one-to-many |
| `-` | one-to-one |
| `<>` | many-to-many |

### Cascade Actions

```dbml
Ref: orders.user_id > users.id [delete: cascade, update: no action]
```

| Action | 意味 |
|--------|------|
| `cascade` | 親削除時に子も削除 |
| `restrict` | 子がある場合は削除拒否 |
| `set null` | 親削除時にNULLに設定 |
| `set default` | 親削除時にデフォルト値に設定 |
| `no action` | 何もしない（デフォルト） |

## Indexes

```dbml
Table users {
  id bigint [pk]
  email text
  name text

  indexes {
    email [unique]
    name
    (email, name) [unique, name: 'users_email_name_idx']
  }
}
```

### Index Options

| オプション | 意味 |
|-----------|------|
| `[unique]` | ユニークインデックス |
| `[name: 'idx_name']` | インデックス名を指定 |
| `[type: btree]` | インデックスタイプ |
| `[type: hash]` | ハッシュインデックス |

## Enum

```dbml
Enum user_role {
  admin
  member
  guest
}

Table users {
  id bigint [pk]
  role user_role [not null, default: 'member']
}
```

## Table Groups

```dbml
TableGroup auth {
  users
  sessions
  accounts
}

TableGroup products {
  products
  categories
}
```

## Notes

### Table Note

```dbml
Table users {
  id bigint [pk]
  Note: 'ユーザー情報を管理'
}
```

### Column Note

```dbml
Table users {
  email text [note: 'ログインに使用するメールアドレス']
}
```

### Standalone Note

```dbml
Note project_note {
  'このスキーマはマルチテナント対応'
}
```

## Best Practices

### 命名規約

- テーブル名: 複数形、snake_case（`users`, `order_items`）
- カラム名: snake_case（`user_id`, `created_at`）
- インデックス名: `{table}_{column}_idx`
- 外部キー名: `{table}_{referenced_table}_fk`

### 必須カラム（推奨）

```dbml
Table example {
  id bigint [pk, increment]  // or text [pk] for UUID
  created_at timestamp [default: `now()`, not null]
  updated_at timestamp
}
```

### 外部キーインデックス

FK列には必ずインデックスを作成（PostgreSQLは自動作成しない）:

```dbml
Table orders {
  user_id bigint [ref: > users.id, not null]

  indexes {
    user_id [name: 'orders_user_id_idx']
  }
}
```
