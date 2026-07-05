# Orchestrated モード (review-code-quality)

## 発動条件

ファイル存在からの推測では判定しない。呼び出し側（オーケストレータ。/deliver-from-spec 等）が「orchestrated モードで実行。escalation は `<path>` に記帳して続行せよ」のように明示指示した場合のみ発動する。指示の伝達経路は `Task` 起動プロンプトでも、メインコンテキストで本 skill の手順を実行する直前の明示宣言でもよい（判定するのは宣言の有無であり伝達経路ではない）。指示が無い単独起動では本ファイルを参照せず、SKILL.md 本文の現行動作（申し送りファイル `quality-review-handoff.md` のみへの記録）のまま進む。

## quality ledger 形式

トリガー文言中の `<path>` (escalation ledger のパス) はモード判定と escalation 記帳先の指定であり、quality ledger の記帳先は常に本ファイルの命名規則 `<プラン名>.quality-ledger.md` を使う (プラン名は指定された escalation ledger パスの basename から `.escalation-ledger` を除いて導出し、同じディレクトリに置く)。

ファイル名: `<プラン名>.quality-ledger.md`。1 行 = 1 項目、追記のみ（既存行は書き換えない。同一項目の状態を更新する再記帳では**同じ番号を使う** — 番号+出所の組で最後の行が現在状態になる「最新行が勝つ」規則。番号を変えると別項目扱いになり収束判定が古い行を残す）。

| 番号 | 出所 (review-code-quality/polish) | 深刻度 | 状態 (適用済み/escalated/保留) | 内容 |
|---|---|---|---|---|

- 「番号」は記帳前に ledger を Read し、既存の最終番号 +1 から採番する (ファイルが無ければ 1 から)。状態更新の再記帳は同じ番号を使う

Step 4 で確定した finding ごとに 1 行記帳する:
- auto-apply-safe で適用・検証 pass → 状態 `適用済み`
- auto-apply-safe で適用したが検証 fail → revert 後、状態 `escalated`（申し送りへ回った扱いのため）
- needs-judgment（cohesion / coupling / business-impact 全件、修正方針が一意でない readability 等） → 状態 `escalated`
- review-only / Edit・Bash 不可で申し送りに回した全件 → 状態 `escalated`

`保留` は本 skill からは記帳しない（`/polish-before-commit` が Manual Review Items の dead mock 部分削除等、判断待ちの項目を記帳する際に使う状態）。

## 深刻度クローズドセット基準 (review-design の fatal 判定と同型)

`references/business-impact.md` / `references/coupling.md` / `references/cohesion.md` / `references/readability.md` に既存の検出基準から、quality ledger 記帳時の深刻度を閉じた条件列挙で決める（判定の揺れ幅を絞るため、この列挙に無い理由での格上げ・格下げはしない）。

| 深刻度 | 該当条件 (いずれか 1 つで確定、上から優先) |
|---|---|
| **Critical** | business-impact: 永続化 chain 該当 (feature-flag revival / auth bypass 等)／business-impact: 認可 chain 該当／coupling: 内容結合 (`instance_variable_set` / `send(:private_method)` / モンキーパッチ)／coupling: 循環依存 (A→B→A) |
| **Major** | (Critical 非該当のとき) business-impact: 外部送信 chain 該当／business-impact: UI制御 chain 該当／coupling: 制御結合 (boolean 引数で内部動作分岐)／coupling: デメテルの法則違反／coupling: spec-coverage-gap／cohesion: 複数責務 (AND 説明 or public 5+ メソッド)／readability: 構造的問題閾値超過 (300行超 / 関数50行超 / ネスト3超 / 引数4超) |
| **Minor** | (上記いずれも非該当のとき) business-impact: 分類軸該当のみ／cohesion: 偶発的凝集 or 論理的凝集 (フラグ分岐)／readability: 曖昧な命名 / 否定形ブール値 / diff スコープ規律逸脱 |

business-impact の Read のみ (✅ Good) は quality ledger に記帳しない（是正対象ではないため）。

## 収束条件 (機械判定可能)

quality ledger の Critical/Major 行（最新行、「最新行が勝つ」規則を適用）が**全て `適用済み` または `escalated`** であれば、品質ループは完了とみなせる。Minor 行の `保留` は収束条件に算入しない (Minor は次 PR 以降でよいため)。

**検証済み Bash**（`/tmp` fixture で $4=深刻度・$5=状態 の列位置と、Critical/Major が両方 適用済み/escalated の場合に出力 0 件、片方が 保留 の場合に該当行が出力されることを確認済み）:

```bash
LEDGER="<plan>.quality-ledger.md"

if [ ! -s "$LEDGER" ]; then
  echo "quality ledger: 記帳なし (skip)"
else
  awk -F'|' '
    /^\| *[0-9]+ *\|/ {
      sev = $4; gsub(/^[ \t]+|[ \t]+$/, "", sev)
      st  = $5; gsub(/^[ \t]+|[ \t]+$/, "", st)
      key = $2 "::" $3
      row[key] = $0; rowsev[key] = sev; rowst[key] = st
    }
    END {
      unresolved = 0
      for (k in row) {
        if ((rowsev[k] == "Critical" || rowsev[k] == "Major") && rowst[k] != "適用済み" && rowst[k] != "escalated") {
          print row[k]
          unresolved++
        }
      }
      exit (unresolved > 0) ? 1 : 0
    }
  ' "$LEDGER"
  if [ $? -eq 0 ]; then
    echo "quality ledger: Critical/Major は全件 適用済み/escalated (収束)"
  else
    echo "quality ledger: 未収束 (上記の Critical/Major 残存行を解消してください)"
  fi
fi
```

## 記帳例

```
| 3 | review-code-quality | Major | 適用済み | app/models/user.rb の 62 行関数を分割 (readability 構造的問題閾値超過、検証 pass) |
| 4 | review-code-quality | Critical | escalated | UserService と TeamService の循環依存、責務分離が要判断 |
```
