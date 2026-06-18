# パターン一貫性チェック

## 概要

**AIが生成したコードで最も問題になるのは、パターンの不整合**。

パターン不整合には2種類ある:
1. **同一ファイル内の混在** - 1つのファイル内で異なるパターンが混在
2. **類似ファイル間の不整合** - 同じコンテキストのファイル間でパターンが異なる

パターンが混在すると:
- レビュアーの認知負荷が上がる
- 「他と合わせて」「方針がぶれてる」という指摘を受ける
- コードベースの一貫性が損なわれる

## チェック手法

### 1. 既存パターンの分析

対象ファイルと周辺ファイルから既存のパターンを抽出する。

```bash
# 同一ディレクトリ内の類似ファイルを確認
ls $(dirname $TARGET_FILE)

# 特定パターンの使用状況を確認
grep -E "パターンA|パターンB" $TARGET_FILE
grep -E "パターンA|パターンB" $(dirname $TARGET_FILE)/*.rb
```

### 2. 混在検出の観点

以下の観点でパターン混在を検出する:

#### 命名規則
```
# 混在例（NG）
def fetch_user    # fetch プレフィックス
def get_settings  # get プレフィックスが混在

# 統一例（OK）
def fetch_user
def fetch_settings
```

#### エラーハンドリング
```
# 混在例（NG）
do_something rescue nil           # インラインrescue
begin; do_other; rescue => e; end # ブロックrescue が混在

# 統一例（OK）- 既存パターンに合わせる
begin
  do_something
rescue => e
  handle_error(e)
end
```

#### データ構造
```
# 混在例（NG）
result1 = { success: true, data: [] }  # Hash
result2 = OpenStruct.new(success: true) # OpenStruct が混在

# 統一例（OK）
result1 = { success: true, data: [] }
result2 = { success: true, data: [] }
```

#### インポート/require
```
# 混在例（NG）
import { Button } from '@/components/Button'  # 絶対パス
import { Input } from '../../components/Input' # 相対パスが混在

# 統一例（OK）
import { Button } from '@/components/Button'
import { Input } from '@/components/Input'
```

### 3. 統一ルール

統一先の優先順 (auto-fix の統一先決定) と「明示的な指定」の定義は **SKILL.md Step 4 が SSOT**。本ファイルは統一ルール本体を持たず、混在の観点・言語別の典型例のみを担う。

### 4. チェックリスト

| カテゴリ | チェック観点 |
|---------|-------------|
| 命名 | メソッド名プレフィックス（fetch/find/get）の統一 |
| 命名 | イベントハンドラ名（handle/on）の統一 |
| 命名 | 変数名の命名規則（camelCase/snake_case）の統一 |
| 構造 | 結果オブジェクトの形式（Hash/Struct/Class）の統一 |
| 構造 | エラーハンドリングスタイルの統一 |
| 構造 | インポートパス形式（絶対/相対）の統一 |
| スタイル | nil ガード方式（&./try/if）の統一 |
| スタイル | 型定義方式（type/interface）の統一 |
| スタイル | 文字列リテラル（I18n/直書き）の統一 |

## 言語別の典型的なパターン混在

### Ruby

| パターン | 混在しやすい選択肢 |
|---------|------------------|
| 結果オブジェクト | OpenStruct / Struct / Hash |
| エラーハンドリング | inline rescue / block rescue / Sentry |
| メソッド命名 | fetch_ / find_ / get_ |
| nil ガード | &. / try / if present? |
| スコープ使用 | Model.scope / Model.where(直書き) |

### TypeScript/JavaScript

| パターン | 混在しやすい選択肢 |
|---------|------------------|
| データ取得 | fetch / axios / 独自wrapper |
| エラーハンドリング | .catch() / try-catch / カスタムハンドラ |
| 関数定義 | function / arrow function |
| 型定義 | type / interface |
| イベントハンドラ | handle* / on* |
| インポート | 絶対パス(@/) / 相対パス(../) |

### Python

| パターン | 混在しやすい選択肢 |
|---------|------------------|
| 型ヒント | 有り / 無し |
| 文字列 | f-string / .format() / % |
| インポート | 絶対 / 相対 |
| 例外処理 | 具体的な例外 / Exception |

## 検出コマンド例

```bash
# Ruby: メソッド命名プレフィックスの混在検出
grep -E "def (fetch_|find_|get_)" $FILE | cut -d: -f2 | sort | uniq -c

# TypeScript: インポートパスの混在検出
grep -E "from ['\"]" $FILE | grep -E "(from '@/|from '\.\./)" | sort | uniq -c

# 同一ファイル内の特定パターン出現回数
grep -c "パターンA" $FILE
grep -c "パターンB" $FILE
```

## 類似ファイル間のパターン整合性チェック

同一ファイル内だけでなく、**似たコンテキストを持つファイル間**でもパターンを統一する。

### 類似ファイルの特定

```bash
# 同じディレクトリ内の同種ファイル
ls $(dirname $TARGET_FILE)/*_controller.rb
ls $(dirname $TARGET_FILE)/*_service.rb

# 同じ命名パターンのファイル（1M context を活用し全件取得して傾向を把握）
find . -name "*_controller.rb" -type f
find . -name "*_service.rb" -type f

# 同じ親クラスを継承しているファイル
grep -l "< ApplicationController" app/controllers/*.rb
grep -l "< ApplicationService" app/services/*.rb
```

### ファイル間で統一すべきパターン

#### 認可・認証チェックの配置

```ruby
# ファイルA: before_action でチェック（NG: 混在）
class UsersController < ApplicationController
  before_action :authorize_user
  def show; end
end

# ファイルB: メソッド内でチェック（NG: 混在）
class TeamsController < ApplicationController
  def show
    authorize_team  # before_action ではなくメソッド内
  end
end

# 統一例（OK）- before_action に統一
class UsersController < ApplicationController
  before_action :authorize_user
  def show; end
end

class TeamsController < ApplicationController
  before_action :authorize_team
  def show; end
end
```

#### 文字列マッチング方式

```ruby
# ファイルA: 前方一致チェック（NG: 混在）
def valid_prefix?(str)
  str.start_with?("prefix_")
end

# ファイルB: 後方一致チェック（NG: 同じコンテキストで方式が異なる）
def valid_suffix?(str)
  str.end_with?("_suffix")
end

# ファイルC: 正規表現チェック（NG: さらに別方式が混在）
def valid_pattern?(str)
  str.match?(/^pattern_/)
end

# 統一例（OK）- 同じコンテキストなら同じ方式
def valid_prefix?(str)
  str.start_with?("prefix_")
end

def valid_suffix?(str)
  str.start_with?("suffix_")  # 前方一致に統一（コンテキストによる）
end
```

#### バリデーションの配置

```ruby
# ファイルA: モデルでバリデーション
class User < ApplicationRecord
  validates :email, presence: true
end

# ファイルB: サービスでバリデーション（NG: 配置場所が異なる）
class TeamService
  def create(params)
    raise "Name required" if params[:name].blank?  # サービス内でチェック
  end
end

# 統一例（OK）- モデルに統一
class Team < ApplicationRecord
  validates :name, presence: true
end
```

#### トランザクション境界の配置

```ruby
# ファイルA: Controller でトランザクション
class UsersController < ApplicationController
  def create
    ActiveRecord::Base.transaction do
      @user = User.create!(params)
    end
  end
end

# ファイルB: Service でトランザクション（NG: 配置場所が異なる）
class TeamService
  def create(params)
    ActiveRecord::Base.transaction do
      Team.create!(params)
    end
  end
end

# 統一例（OK）- Service に統一
class UserService
  def create(params)
    ActiveRecord::Base.transaction do
      User.create!(params)
    end
  end
end
```

#### React コンポーネントの状態管理

```tsx
// ファイルA: useState でローカル状態
function UserForm() {
  const [name, setName] = useState("")
  return <input value={name} onChange={e => setName(e.target.value)} />
}

// ファイルB: useReducer で状態管理（NG: 同じコンテキストで方式が異なる）
function TeamForm() {
  const [state, dispatch] = useReducer(reducer, initialState)
  return <input value={state.name} onChange={e => dispatch({ type: 'SET_NAME', payload: e.target.value })} />
}

// 統一例（OK）- 単純なフォームは useState に統一
function UserForm() {
  const [name, setName] = useState("")
  return <input value={name} onChange={e => setName(e.target.value)} />
}

function TeamForm() {
  const [name, setName] = useState("")
  return <input value={name} onChange={e => setName(e.target.value)} />
}
```

### ファイル間整合性のチェック手順

1. **類似ファイルを特定**
   ```bash
   # 対象ファイルと同じカテゴリのファイルを列挙
   ls $(dirname $TARGET_FILE)/*.rb
   ```

2. **パターンを抽出・比較**
   ```bash
   # 認可チェックの配置を比較
   grep -l "before_action.*authorize" app/controllers/*.rb
   grep -l "def.*authorize" app/controllers/*.rb

   # バリデーションの配置を比較
   grep -l "validates" app/models/*.rb
   grep -l "raise.*if.*blank" app/services/*.rb
   ```

3. **不整合を検出**
   - 同じコンテキストで異なるパターンが使われている場合を報告

4. **統一方針を決定**
   - 統一先の優先順は SKILL.md Step 4 が SSOT (規約 > 同一ファイル多数派 > 同一ディレクトリ多数派 > Manual Review)
