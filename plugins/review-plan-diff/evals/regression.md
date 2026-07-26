# regression eval

収束記録: 2026-07-06 (v0.1.0 PR)。Iter1-3 の 3 実行で fresh executor が全 [critical] ○ / retries 0。

収束記録 (委譲実行摩擦): 2026-07-07。SKILL.md 経由で委譲実行した際の入力解決・`${CLAUDE_PLUGIN_ROOT}` 解決・`Task` fallback・重大度判定 (計画済みテスト未実装の Critical 検出) を対象に Iter1 (baseline) から Iter6 まで反復。Iter5→Iter6 の 2 ラウンド連続で新規不明点 0 件・精度 100% を維持して収束。hold-out シナリオ (`Task` 相当ツール不可時の自己判定 fallback) も 5/5 で通過し、過学習の兆候は無かった。

収束記録 (簡易プラン対応, G-RPD-1): 2026-07-07。「DD 該当タスクを転記した簡易プラン (AC・QA-ID マトリクス無し)」を対象範囲に加えた改修を、median (簡易プラン fast path) / edge (確定プラン regression) の 2 シナリオで 4 iteration 反復し規定打ち切り。QA-ID マトリクス不在・分析ファイル不在それ自体を乖離として報告する誤りは全 iteration で 0 件だった一方、Iter1 で「他の適合済み手順が構造上必要とする派生的な戻り値変更」を独立の仕様逸脱として誤検出する実バグを発見し `agents/plan-diff-reviewer.md` の Step 2 に除外規定を追記して解消 (Iter2-4 で再発無し)。edge シナリオでの回帰確認・hold-out (起点ブランチ未指定シナリオの再実行) も 100% 通過。

収束記録: 2026-07-11 (出力 enum の未定義ラベル削除)。agents/plan-diff-reviewer.md の出力 enum から未定義ラベル「スコープ越境」を削除し 4 択 (未実装/仕様逸脱/計画外差異/判定不能) に統一し、plugin.json の description も 3 種表記に同期した。既存 4 シナリオ (QA-ID 未実装 / 委譲 median / 委譲 edge / 簡易プラン fast path) を fresh executor で再実行し全 [critical] ○、判定カテゴリの選択に迷いなし / 新規不明点 0 で収束。

記録: 2026-07-18 (v0.7.0)。人間向けの出自説明 2 箇所 (description 末尾の「実案件 dogfood で…独立skill化したもの」、本文の旧オーケストレータからの移設経緯段落) を削除した。いずれも executor の判定に寄与しない開発史で、保存シナリオのどの checklist からも参照されていないことを grep で確認済み。fresh executor での再実行は同日セッションの subagent 上限到達により未実施 — 直前 (2026-07-17、v0.6.0 時点の同一ルール本文) に全 4 シナリオ × 2 ラウンド全 [critical] ○ を確認済みで、本変更はルール・手順・テンプレートに触れていない。次に本 skill を変更する PR で通常どおり再実行すること。

収束記録 (v0.7.0 再実行検証): 2026-07-18。直前の v0.7.0 記録が残した申し送り「fresh executor での再実行は subagent 上限到達により未実施 — 次に本 skill を変更する PR で通常どおり再実行すること」を本セッションで解消した。既存 4 シナリオ (QA-ID 未実装 / 委譲 median / 委譲 edge / 簡易プラン fast path) を fresh executor で再実行し全 [critical] ○ / Accuracy 100% / retries 0。SKILL.md・agents/plan-diff-reviewer.md への修正は無し (v0.6.0 と同一のルール本文で通過)。QA-ID 未実装シナリオの初回 executor が「シナリオが自分を plan-diff-reviewer と名指すが SKILL.md は plan-diff-reviewer を起動せよと指示する」枠組み上の一瞬の曖昧さを 1 件 unclear として言語化したが、これは eval の reviewer 視点フレーミングと『必ず SKILL.md を Read する』契約の衝突に由来する scaffolding 起因であり skill の欠陥ではない (executor は既存の委譲実行 fallback で正しく自己判定し全 [critical] ○)。同シナリオを fresh executor で 1 回追加再実行したところ unclear 0 件・全 [critical] ○ で再現せず、executor variance と確認したため skill 本文は変更していない。

記録 (Opus 5 / Fable 5 向けチューニング): 2026-07-25。下記 3 シナリオ (A median / B edge / C hold-out) へ再編し 9 ラウンド・fresh executor 19 体で反復。**旧 4 シナリオの [critical] 要件はすべて新 3 シナリオへ引き継がれている** (末尾の対応表を参照)。全 19 実行で精度 100% / 全 [critical] ○、retries は round 1 の 1 件 (nested 起動の `name` パラメータ拒否) 以降ゼロ。hold-out C は round 8 で初投入し 100% (低下 0 点、過学習なし)、Step 2 を触った round 9 で再実行しても 100%。「新規不明点 0 が 2 ラウンド連続」は厳密には未達 (fresh executor は毎回文言観察を返す) だが、round 4〜7 の指摘が「前ラウンドで自分が足した禁止句のスコープ質問」に移行した時点で過剰規定と判断し、iter 8 で禁止句を撤去する削除パスを実施。round 9 は新規パターン 0 件 (全指摘が台帳の既存クラス) で打ち切った。実害あり欠陥として修正したのは (1) 可用性分岐がツール固有名 `Task` 依存で `Agent` 環境だと Generator-Evaluator 分離を捨てて自己判定 fallback へ落ちる、(2) 起動ツールが既定 background で Step 4 に渡す出力が消える、(3) nested 起動に `name` を付けると拒否される、(4) `${CLAUDE_PLUGIN_ROOT}` の読み替えが `skills/review-plan-diff/` 二重化を許す、(5) 「乖離なしの根拠明示」要求に対応する出力枠が無く全 executor が独自節を自作、(6) 重大度表の「(副作用が限定的なもの)」限定子に補集合が無く重大度が裁量落ち、(7) 起点ブランチのラベル判定が「起点ブランチ」完全一致前提で `ベースブランチ` 等の実務表記を拾えない、の 7 点。

## シナリオ A (median): 確定プラン + 全入力明示の委譲実行

fixture: git リポジトリ (base `main` / HEAD `feature/priority`、`src/tasks.ts` + `test/tasks.test.ts` の TypeScript todo アプリ)。プラン類はリポジトリ外の `plans/` に置く (プラン自体が diff に混入しないため) — `plan-priority-final.md` (実装手順 1〜5 + QA-ID カバレッジマトリクス + ブランチ戦略節)、`plan-priority-final.analysis.md` (AC-1〜AC-3)、`plan-priority-final.preflight.md` (「起点ブランチ | main」)。

プランの実装手順 5 は「優先度の異なる複数のタスクを追加し、`listTasks` の出力順が優先度の高い順になることを検証する回帰テストを `test/tasks.test.ts` に追加する」と明記。QA-ID マトリクスは QA-N-01 (auto)・QA-E-01 (auto)・QA-N-02 (manual、備考「対応する自動テストが未実装のため manual 扱いへ変更」)。

diff の仕込み: 実装手順 1〜4 (Priority 型 / priority フィールド / 既定値 normal / 優先度順 sort) と QA-N-01・QA-E-01 のテストは実装済み。**1 実装漏れ** = 実装手順 5 の並び順回帰テストが無い (プロダクションコードの sort は実装済み)。**1 計画外差異** = プラン全体に記載の無い公開関数 `clearCompleted()` の追加。

確定プランファイルパス・起点ブランチ (`main`)・対象リポジトリの絶対パスをいずれも起動プロンプト本文で明示し、委譲実行 (`AskUserQuestion` が利用可能ツール一覧に無い前提) として実行する。

### Requirements checklist

1. [critical] 実装手順 5 の回帰テスト (優先度順ソートの検証) が diff に無いことを未実装・Critical として検出する。QA-ID カバレッジマトリクスが QA-N-02 を manual 扱いへ付け替えていても Critical を格下げしない
2. [critical] その指摘の diff 根拠として「diff 中に優先度順ソートを検証するテストケースが存在しない」ことを示す (プロダクションコード側のソート実装済みを理由に判定を済ませない)
3. [critical] プラン記載の無い `clearCompleted` の追加を計画外差異として乖離一覧に報告する (実装漏れの検出だけで打ち切らない)
4. [critical] `plan-diff-reviewer` を nested 起動する際、`${CLAUDE_PLUGIN_ROOT}` を生文字列のまま埋め込まず実際の絶対パスへ解決して渡す (サブエージェント起動ツールが使えず自己判定 fallback に入る場合は、`agents/plan-diff-reviewer.md` を絶対パスへ解決して Read したことを報告に示す)
5. 起点ブランチ `main` との diff を実際に取得して突き合わせる。分析ファイル `plan-priority-final.analysis.md` の存在も確認し AC との突き合わせに使う
6. 実装済みの実装手順 1〜4 (`Priority` 型 / `priority` フィールド / 既定値 normal / ソート順) を誤って未実装・仕様逸脱として報告しない
7. 「## プラン突き合わせ結果」相当のフォーマットで総合判定「Critical あり」と乖離一覧の表を提示する

## シナリオ B (edge): 簡易プラン (QA-ID マトリクス・分析ファイル無し) の fast path

fixture: git リポジトリ (base `develop` / HEAD `feature/pagination`)。プランは `plan-pagination-dd.md` のみ (分析ファイル・preflight・QA-ID マトリクスとも無し)。「やること」として 5 項目のみを記載: (1) `listTasks` に limit/offset を追加 (2) limit 既定 20・上限 100 (3) offset 負値でエラー (4) 戻り値に `totalCount` を追加 (5) `listTasks` のテストにページネーション挙動の検証ケースを追加。

diff の仕込み: 項目 1〜4 は実装済み (戻り値は `Task[]` → `{ items, totalCount }` へ変わり、既存テスト 2 件が `.items` へ追随)。**1 実装漏れ** = 項目 5 の新規テストケースが 0 件。**1 計画外差異** = プラン記載の無い `Priority` 型追加・`Task.priority` 必須化・`addTask` でのデフォルト優先度付与。

### Requirements checklist

1. [critical] QA-ID カバレッジマトリクス不在・分析ファイル (`.analysis.md`) 不在それ自体を乖離・判定不能として報告しない
2. [critical] やること項目 5 (ページネーション挙動のテスト追加) の未実装を Critical として検出する
3. [critical] プラン記載の無い `addTask` へのデフォルト優先度付与 (`priority: 'normal'` / `Priority` 型追加) を計画外差異として報告する
4. やること項目 1〜4 (実装済み) を誤って未実装・仕様逸脱として報告しない。特に項目 4 の戻り値形状変更 (配列 → `{ items, totalCount }`) と既存テストの追随修正を、項目 1 のページネーション導入に伴う構造上必要な派生的変更として扱い独立の仕様逸脱に計上しない
5. 総合判定「Critical あり」と乖離一覧の表を含める
6. 各指摘にプラン根拠 (やること番号) と diff 根拠 (ファイルパス:行範囲) を引用する

## シナリオ C (hold-out): 起点ブランチ未指定 + preflight.md 欠落

fixture: シナリオ A と同じリポジトリ・プラン・分析ファイルから `plan-priority-final.preflight.md` を削除。起動プロンプトには確定プランファイルパスと対象リポジトリの絶対パスのみを書き、起点ブランチを含めない。プラン本文の「ブランチ戦略」節には `作業ブランチ: feature/priority (実装を継続する現ブランチ)` の記載があるが、これは diff の比較元を指すラベルではない。

### Requirements checklist

1. [critical] 起点ブランチをプラン本文・preflight.md のいずれからも確定できない場合、「不足入力: 起点ブランチ」相当の内容を最終メッセージに含めてその場で終了する (返答を待って停止・ハングしない)
2. [critical] `<プラン名>.preflight.md` の存在を実際に確認したうえで不足と判断する。プラン本文「ブランチ戦略」節の作業ブランチ `feature/priority` を、比較元を指すラベルが無いにもかかわらず起点ブランチとして誤採用しない
3. 不足入力の報告に具体的な項目名 (起点ブランチ) を明示する (曖昧な「情報不足」で終わらない)
4. 起点ブランチ以外の入力解決 (プランパス確定・分析ファイルの有無確認) は通常どおり進める
5. 起点ブランチ未確定のまま サブエージェント起動ツールで `plan-diff-reviewer` を起動しない (diff 取得・レビュー起動を試みる前に停止する)

## 旧 4 シナリオの [critical] 要件との対応

| 旧シナリオ | 旧 [critical] 要件 | 現行の担保 |
|---|---|---|
| QA-ID カバレッジマトリクスに計画されたテストが diff に無い | 計画済み auto テストの不在を Critical 検出 / テストの不在を独立に diff 根拠で示す (プロダクションコード実装済みで済ませない) | A-1 / A-2 |
| SKILL.md 委譲実行 — 確定プランパス・起点ブランチとも明示 (median) | 実装手順のテスト未実装を Critical (QA-ID マトリクスの manual 付け替えでも免除しない) / `${CLAUDE_PLUGIN_ROOT}` を絶対パスへ解決して渡す | A-1 / A-4 |
| SKILL.md 委譲実行 — 起点ブランチ未指定・preflight.md 欠落 (edge) | 「不足入力: 起点ブランチ」で即終了 (ハングしない) / preflight を実確認し作業ブランチを誤採用しない | C-1 / C-2 |
| 簡易プラン (DD タスク転記) の fast path | QA-ID マトリクス不在・分析ファイル不在それ自体を乖離報告しない / テスト未追加を Critical 検出 | B-1 / B-2 |
