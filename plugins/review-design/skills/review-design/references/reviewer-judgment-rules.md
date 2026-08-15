# Reviewer 共通の判定規律 (全 reviewer 必読)

`agents/*.md` の 5 reviewer (anti-pattern-checker / ddd-reviewer / hexagonal-reviewer / clean-architecture-reviewer / deep-module-reviewer) が**共通で守る判定規律**の canonical。各 reviewer は起動時に本ファイルを Read し、以下 3 規律を自分の観点に適用する。

観点ごとの判定基準 (✅/⚠️/❌ をどの条件で付けるか) は各 reviewer 定義と早見表が SSOT であり、本ファイルには書かない。本ファイルが定めるのは「どういう態度で判定し、判定できないときどうし、何を出力するか」だけ。

## 規律 1: 証拠で判定する

各観点で反例と適合証拠を探す。適合を確認できれば✅、軽微な反例は⚠️、契約上の重大な反例は❌、判断材料がなければ Unknown とする。quickref の閾値を使い、既定ラベルから逆算しない。

## 規律 2: 証拠が取得できない項目は Unknown で棄権せよ

✅/⚠️/❌ をでっち上げず「Unknown (判定不能)」とし、「問題なしの項目」と同列に `<観点>: Unknown (理由)` の 1 行で出力して親エージェントに委ねる (例: `Shotgun Surgery: Unknown (対象概念名が plan から特定できず)`)。

判別:

| 状況 | 判定 |
|---|---|
| 反例検索 (greenfield では forward-looking 判定) を実行できて反例ゼロ | ✅ |
| 反例あり | ⚠️ or ❌ |
| 検索・判定そのものが成立しない (対象コード・対象概念を特定できない) | Unknown |

greenfield (コード不在) では提案された構造への forward-looking な制約として判定できる項目を Unknown にしない — Unknown は提案構造からも判定材料が得られない場合に限る。また greenfield では ✅ 項目にも判定根拠を 1 行付記する (反例 Grep ログが存在しないため、根拠の提示先が出力本文しかない)。

## 規律 3: 出力粒度

定義された全観点を `<観点>: <✅|⚠️|❌|Unknown> (<根拠または理由>)` の1行で列挙する。greenfield の✅も観点別に根拠を書く。⚠️/❌だけは次行へ影響と最小修正を足す。

最後に参照した絶対パスを列挙する。コード不在なら `参照コード: なし (greenfield)` とする。
