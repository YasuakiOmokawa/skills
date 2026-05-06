# SQL Antipatterns Reference

Bill Karwin著『SQLアンチパターン』に基づく論理設計のアンチパターン集。

## 1. Jaywalking（ジェイウォーク / 信号無視）

### 症状

カンマ区切りで複数値を1つのカラムに格納。

```sql
-- ❌ アンチパターン
CREATE TABLE articles (
  id BIGINT PRIMARY KEY,
  title TEXT,
  tags TEXT  -- 'ruby,rails,web' のようにカンマ区切り
);
```

### 問題点

- 特定タグの検索が困難（LIKE '%tag%' は誤マッチの可能性）
- タグの追加・削除が文字列操作になる
- 参照整合性を保証できない
- 集計が困難

### 解決策

交差テーブル（中間テーブル）を作成:

```dbml
Table articles {
  id bigint [pk, increment]
  title text [not null]
}

Table tags {
  id bigint [pk, increment]
  name text [unique, not null]
}

Table article_tags {
  article_id bigint [ref: > articles.id, not null]
  tag_id bigint [ref: > tags.id, not null]

  indexes {
    (article_id, tag_id) [pk]
    tag_id
  }
}
```

---

## 2. Naive Trees（ナイーブツリー / 素朴な木）

### 症状

親IDのみで木構造を表現（隣接リスト）。

```sql
-- ❌ アンチパターン（単純な隣接リスト）
CREATE TABLE categories (
  id BIGINT PRIMARY KEY,
  name TEXT,
  parent_id BIGINT REFERENCES categories(id)
);
```

### 問題点

- 祖先・子孫の取得に再帰クエリが必要
- 深い階層でパフォーマンス劣化
- サブツリーの削除が複雑

### 解決策

用途に応じて選択:

**閉包テーブル**（推奨: 柔軟性が高い）:

```dbml
Table categories {
  id bigint [pk, increment]
  name text [not null]
}

Table category_paths {
  ancestor_id bigint [ref: > categories.id, not null]
  descendant_id bigint [ref: > categories.id, not null]
  depth int [not null]

  indexes {
    (ancestor_id, descendant_id) [pk]
    descendant_id
  }
}
```

**経路列挙**（読み取り重視の場合）:

```dbml
Table categories {
  id bigint [pk, increment]
  name text [not null]
  path text [not null]  // '/1/2/3/' のような形式

  indexes {
    path
  }
}
```

---

## 3. ID Required（IDリクワイアド / とりあえずID）

### 症状

すべてのテーブルに無意味な代理キー（サロゲートキー）を追加。

```sql
-- ❌ アンチパターン（自然キーで十分な場合）
CREATE TABLE country_languages (
  id BIGINT PRIMARY KEY,  -- 不要
  country_code CHAR(2),
  language_code CHAR(2)
);
```

### 問題点

- 重複データを防げない
- ディスク容量の無駄
- 自然な一意性を表現できない

### 解決策

自然キー or 複合主キーを検討:

```dbml
Table country_languages {
  country_code char(2) [not null]
  language_code char(2) [not null]

  indexes {
    (country_code, language_code) [pk]
  }
}
```

**ただし**: 以下の場合はサロゲートキーが適切:
- 自然キーが長い/変更される可能性がある
- 外部キーとして頻繁に参照される
- ORM/フレームワークがIDを前提としている

---

## 4. Keyless Entry（キーレスエントリー / 外部キー嫌い）

### 症状

外部キー制約を定義しない。

```sql
-- ❌ アンチパターン
CREATE TABLE orders (
  id BIGINT PRIMARY KEY,
  user_id BIGINT  -- FK制約なし
);
```

### 問題点

- 参照整合性が保証されない
- 孤児レコードが発生
- アプリケーション側でのチェックが必要

### 解決策

必ず外部キー制約を定義:

```dbml
Table orders {
  id bigint [pk, increment]
  user_id bigint [ref: > users.id, not null]

  indexes {
    user_id [name: 'orders_user_id_idx']
  }
}
```

---

## 5. EAV（Entity-Attribute-Value）

### 症状

汎用的なkey-valueテーブルで属性を管理。

```sql
-- ❌ アンチパターン
CREATE TABLE attributes (
  entity_id BIGINT,
  attr_name TEXT,
  attr_value TEXT
);
```

### 問題点

- データ型を強制できない
- 必須属性を保証できない
- クエリが複雑になる（PIVOT必要）
- パフォーマンス劣化

### 解決策

具体的なテーブル/カラムに分解:

```dbml
// 代わりに具体的なテーブルを定義
Table products {
  id bigint [pk, increment]
  name text [not null]
  price decimal [not null]
  weight decimal
  color text
}

// サブタイプがある場合は継承パターン
Table electronics {
  product_id bigint [pk, ref: > products.id]
  voltage int
  warranty_months int
}
```

---

## 6. Polymorphic Associations（ポリモーフィック関連）

### 症状

1つの外部キーが複数のテーブルを参照。

```sql
-- ❌ アンチパターン
CREATE TABLE comments (
  id BIGINT PRIMARY KEY,
  commentable_type TEXT,  -- 'Article' or 'Video'
  commentable_id BIGINT   -- articles.id or videos.id
);
```

### 問題点

- 外部キー制約を定義できない
- 参照整合性が保証されない
- JOIN が複雑になる

### 解決策

**交差テーブル方式**:

```dbml
Table comments {
  id bigint [pk, increment]
  body text [not null]
}

Table article_comments {
  article_id bigint [ref: > articles.id, not null]
  comment_id bigint [ref: > comments.id, not null]

  indexes {
    (article_id, comment_id) [pk]
  }
}

Table video_comments {
  video_id bigint [ref: > videos.id, not null]
  comment_id bigint [ref: > comments.id, not null]

  indexes {
    (video_id, comment_id) [pk]
  }
}
```

**共通親テーブル方式**:

```dbml
Table commentables {
  id bigint [pk, increment]
  type text [not null]
}

Table articles {
  commentable_id bigint [pk, ref: > commentables.id]
  title text [not null]
}

Table videos {
  commentable_id bigint [pk, ref: > commentables.id]
  url text [not null]
}

Table comments {
  id bigint [pk, increment]
  commentable_id bigint [ref: > commentables.id, not null]
  body text [not null]
}
```

---

## 7. Multicolumn Attributes（マルチカラムアトリビュート / 複数列属性）

### 症状

同種の値を複数カラムで表現。

```sql
-- ❌ アンチパターン
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  phone1 TEXT,
  phone2 TEXT,
  phone3 TEXT
);
```

### 問題点

- 列数に上限がある
- NULLが多発
- 検索が複雑（OR条件の列挙）
- 追加時にスキーマ変更が必要

### 解決策

従属テーブルに分離:

```dbml
Table users {
  id bigint [pk, increment]
  name text [not null]
}

Table user_phones {
  id bigint [pk, increment]
  user_id bigint [ref: > users.id, not null]
  phone text [not null]
  label text  // 'home', 'work', 'mobile'

  indexes {
    user_id [name: 'user_phones_user_id_idx']
  }
}
```

---

## Quick Reference

| パターン | 症状 | 解決策 |
|---------|------|--------|
| Jaywalking | カンマ区切りリスト | 交差テーブル |
| Naive Trees | 親IDのみの木構造 | 閉包テーブル/経路列挙 |
| ID Required | 無意味なサロゲートキー | 自然キー/複合主キー |
| Keyless Entry | FK制約なし | FK制約を必ず定義 |
| EAV | 汎用key-valueテーブル | 具体的なテーブル |
| Polymorphic | 1 FK → 複数テーブル | 交差テーブル/共通親 |
| Multicolumn | col1, col2, col3... | 従属テーブル |
