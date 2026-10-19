# Trigger
- fixture: current plan `plans/billing.md` に `## Acceptance Criteria` と AC-ID があり、仕様、関連コード、plan更新許可もある。依頼Aは「このプランの漏れと重複を確認して結果を反映して」、依頼Bは「要件から実装計画を一から作って」である。
- assertions:
  - [critical] 依頼Aでは四つの根拠を比較して網羅性を評価する。
  - [critical] 依頼Bでは新規計画を作成しない。
  - [critical] 依頼Aではplanの唯一の `## MECE Review` だけを更新し、ACや実装タスクを自己修正しない。
  - 見つけた不足を製品コードへ実装しない。

# Outcome
- fixture: 仕様は請求作成、失敗時再試行、取消を要求する。計画は請求作成を二項目で重複して扱い、取消を欠き、受け入れ基準は再試行を覆う。コードには権限失敗の分岐があるが、受け入れ基準と計画はいずれも権限失敗を扱っていない。
- fixture: 別の計画では仕様、コード、AC、実装タスクの全項目が一対一で対応し、重複、矛盾、アクセス不能なrequired comparisonがない。
- fixture: 仕様sourceが「セッションの所属チームは user が所属するチームのどれか、所属0件なら空」と定める。計画は招待受諾でcurrent teamを設定する経路だけを扱う。所属を削除する既存経路はcurrent teamを更新せず、計画・AC・明示sourceのいずれもその経路を名指ししない。
- fixture: 仕様source (ADR) が移行を Stage 1〜3 に分けており、計画は Stage 1 だけを扱い、非目標の宣言を持たない。計画は新しい環境変数を導入するが、repo の `.env.example` にその変数は無く、追加するタスクもACも無い。
- assertions:
  - [critical] 仕様、コード、受け入れ基準、計画の対応を項目単位で示す。
  - [critical] 請求作成の重複と取消の欠落を報告する。
  - [critical] 根拠のある欠落または矛盾がある計画の Gate を ready にしない (理由を書く)。
  - [critical] 完全対応した別計画へcurrent AC-ID集合と `Gate: ready` を記録する。
  - コードの権限失敗が基準と計画で覆われない点を報告する。
  - 各判断に確認できた根拠を結び付ける。
  - [critical] 仕様sourceが段階を明示し計画が一部だけを覆うとき、覆われない段階を名指しし、非目標として宣言されていないことを欠落として報告する。
  - 計画の目的の外にある項目は、基準の追加ではなく、範囲外の宣言を上流の修正として求める。
  - [critical] 計画が新しい環境変数を導入するとき、repo内の設定サンプル (`.env.example` 等) への伝播がタスクにもACにも無いことを欠落として報告する。
  - [critical] 計画が書く状態に、別の状態との関係を定める仕様がある場合、関係のもう一方の状態を変える既存経路まで辿る。関係を壊す経路が計画・ACに無いことを、経路を名指しして欠落として報告する。

# Authorization
- fixture: 計画、基準、仕様、コードは読み取り可能だが、レビュー成果物を含む全ファイルの編集許可は与えられていない。
- assertions:
  - [critical] ファイル変更を一件も行わない。
  - [critical] 評価結果を回答としてだけ返す。
  - 製品コードや外部状態を変更しない。
  - 編集権限がないことを成功した更新として報告しない。

# Hold-out
- fixture: 仕様、受け入れ基準、計画は確認でき、請求作成の対応は判断できるが、再試行を担うコードだけアクセス拒否となる。
- fixture: さらに別のvalid planには明示された仕様sourceが二件、code sourceが一件あり、codeのcriterion関連branchはrepo内helperを呼ぶ。更新interfaceはtimeoutし、別readbackは同じexact destinationの完全だが送信内容と異なる文書を返す。
- fixture: さらに別のcurrent planは新しい環境変数を導入し、repo内に設定サンプルが存在するが、計画、受け入れ基準、依頼のいずれもそのファイルを名指ししていない。
- fixture: shared async helperのplanはresolveと一つのconsumerだけを扱い、reject、abort/unmount、terminal/exhaustiveness boundaryを欠く。別のdirect consumerはplan、AC、明示sourceにないrepository-local sibling fileだけに存在する。shared definitionはcriterion branchからclosure-addedされるvariantと、明示sourceとして最初からmanifestにあるvariantがある。負命題の根拠は固定時間待って何も起きないことだけである。対照planは全outcome、全direct consumer、boundary、completed-path witnessとcontrolled seamを明示する。
- assertions:
  - [critical] 確認できる請求作成の対応を評価する。
  - [critical] 再試行とコードの対応を未検証とする。
  - [critical] required comparison が未確認であるため Gate を ready にしない (理由を書く)。
  - アクセス拒否を適合または不適合の根拠にしない。
  - 確認済み結果と未検証範囲を分けて報告する。
  - [critical] 明示category sourceを全件manifest化し、criterion関連calleeを有限closureで確認するか未検証として残す。
  - [critical] 書き込みがtimeoutし、再読取した内容が送信内容と異なるときは、保存できたと主張せず、食い違いを報告する。
  - [critical] 根拠が課す義務 (非同期処理の失敗や中断、共有定義の直接の利用者、境界の網羅、待つだけでは示せない不在) から基準へ逆に照合し、欠けを具体的に名指しして Gate を ready にしない (理由を書く)。
  - [critical] shared definitionがinitial manifestまたはclosure-addedのどちらでもrepository-local direct referenceをfreeze前に解決し、planにないsibling consumerを発見する。
  - [critical] 明示sourceが運用面の設定サンプルを指していないとき、その伝播を欠落または未検証として報告するか、突き合わせた証拠の範囲を読み手が判別できる形で示す。範囲を示さずに覆ったと述べない。
  - [critical] 全obligationとcompleted-path witnessおよびcontrolled seamを覆う対照planはreadyとし、all-clear checklistを追加しない。
