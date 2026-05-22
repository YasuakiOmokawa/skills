# Dead Mock 削除 (Ruby/RSpec)

**目的**: 実装側で `delegate :X` / `def X` を撤去した PR で、spec の対応 mock (`receive(:X)` / `receive_messages(X:)` / `instance_double(..., X:)` 等) が残置していないか検証し、残っていれば削除する。

**なぜ必要か**: 呼ばれなくなった mock は CI ではエラーにならない (RSpec は未使用 stub を error にしない)。lint でも検出されない。レビュー時に発見され差し戻しになる。

## スキップ条件と文言バリアント

| 条件 | スキップ文言 |
|---|---|
| 変更ファイルに `*.rb` が無い | `[dead mock: スキップ (Ruby/RSpec 対象外)]` |
| `spec/` ディレクトリが存在しない | `[dead mock: スキップ (Ruby/RSpec 対象外)]` |
| 検出手順 1 で削除された identifier が 0 件 (= delegate / def 撤去なし) | `[dead mock: スキップ (撤去なし)]` |
| 検出手順 1 で identifier が 1 件以上、かつ 検出手順 2 で残存 mock 0 件 | `[dead mock: 検出済み撤去なし]` (識別子 N 件確認、残存 0 件) |

検出手順 1 の出力で identifier 0 件と確定した時点で手順 2 を実行せず即スキップ報告して良い (rg 不要)。

## 検出手順

### 1. 削除された identifier を抽出 (impl 側のみ、`spec/` 自身は除外)

```bash
git diff origin/${BASE_BRANCH:-develop}...HEAD -- '*.rb' ':!spec/**' \
  | grep -E "^-\s*(#\s*)?(delegate\s+:|def\s+)" \
  | grep -vE "^---"
```

- `- delegate :foo, :bar, to: ...` → identifiers: `foo`, `bar`
- `- def foo` / `- def self.foo` → identifier: `foo`
- **コメント化による削除も対象**: `- # delegate :foo, ...` / `- # def foo` (PR で delegate / def をコメントアウト) も identifier 削除として扱う (上記 grep の `(#\s*)?` がこれを拾う)
- 同一 PR 内で同名メソッドが追加し直されている (`+ def foo`) なら除外する

### 2. spec/ で残存 mock を検出 (identifier ごとに)

```bash
rg --no-heading -n \
  -e "receive\(:${ID}\)" \
  -e "receive_messages\([^)]*\b${ID}:" \
  -e "instance_double\([^)]*\b${ID}:" \
  -e "double\([^)]*\b${ID}:" \
  -e "\.${ID}\b" \
  spec/
```

`allow_any_instance_of(...).to receive(:X)` 形式も `receive(:X)` パターンで拾える。

加えて **impl 側 `def X` を撤去した場合の spec 内 caller-only 残存呼出**も検出対象に含める (`expect(receiver.X)` / `receiver.X` の直呼出)。impl 側に定義がない以上、spec の caller-only 呼出は NoMethodError で必ず失敗するため、it block ごと削除候補として提示する。

### 3. 削除前にユーザーへ提示 (1 ヒットでも以下を必須)

- ヒットしたファイル/行
- 削除後の差分プレビュー
- **削除単位の分類** (auto / Manual Review):
  - `receive(:X)` の単独 stub で X が削除済 → **行ごと自動削除** (auto)
  - `receive_messages(a:, b:)` で **a, b すべてが削除済 identifier** → **行ごと自動削除** (auto, full removal)
  - `receive_messages(a:, b:)` で **一部 (例: a だけ) が削除済、他は実装に残存** → **Manual Review Items** に回す (auto しない)
  - **caller-only spec 残存** (`expect(receiver.X)` / `receiver.X` で X が削除済 def) → **it block ごと自動削除候補** (auto)。テスト意図が壊れていないか reviewer 確認を促す注記を付ける

### 4. 承認後の実行

承認後、該当 mock を削除 → 編集した spec ファイル**全件**を `bundle exec rspec <file1> <file2> ...` (複数指定可) で実行し 0 failures を確認。失敗した場合は変更を revert し報告。

## 注意

- caller 側で `obj.X` 呼出を撤去しただけ (実装は残存) の場合は対象外。`delegate` / `def` の **定義削除** に限る。
- 逆方向 (impl 側で `def X` を撤去後、spec の caller-only 呼出が残存) は **検出対象** (上記検出手順 2 で拾う)。it block ごと auto 削除候補に分類する。
- 部分削除 (`receive_messages(a:, b:)` のうち a だけ削除) は Manual Review。書換え候補 (例: `receive_messages(b:)` 化 / 行ごと削除 / テスト見直し) を併記してユーザーに選択させる。
