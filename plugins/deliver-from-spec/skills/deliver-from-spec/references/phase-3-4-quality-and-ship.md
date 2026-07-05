# Phase 3: 品質ループ + QA / Phase 4: 出荷ゲート〜監査パック

起動方法の通則 (2 経路パス解決・メインコンテキスト実行・Orchestrated モード宣言) は SKILL.md 本文を参照。検証済み Bash (出荷ゲート・監査パック集計) は SKILL.md 本文の該当節に直接記載する (本ファイルでは重複させない)。

## Phase 3: 品質ループ + QA

3 skill を順に Orchestrated モードで起動する。いずれも起動直前に発動フレーズ（「orchestrated モードで実行。escalation は `<plan>.escalation-ledger.md` に記帳して続行せよ」）を宣言する。

1. `/review-code-quality` — quality ledger (`<plan>.quality-ledger.md`) へ記帳しながら実行
2. `/polish-before-commit` — 同じ quality ledger を引き継ぎ、Manual Review Items を escalation ledger へ記帳しながら実行
3. `/qa-ui` — qa-ledger (`<plan>.qa-ledger.md`) を審判し、Critical FAIL を escalation ledger へ記帳しながら実行 (認証つき案件はログイン 1 タッチが同期タッチとして残る。preflight のログイン手段欄を参照してユーザーに依頼する。自動ログインは行わない)

### 完了条件

- quality ledger 収束: Critical/Major 行が全て `適用済み` または `escalated` (review-code-quality の既存収束判定バッチをそのまま使う)
- qa-ledger Step 6 完了判定 exit 0 (qa-ui 既存の完了判定バッチをそのまま使う。escalated Critical が残る場合は「部分完了」までしか名乗らないが、Phase 3 自体は次へ進める — Critical の最終可否判断は Phase 4 の出荷ゲートに一本化する)

### 再突入

品質ループが収束しない場合、該当 skill (review-code-quality または polish-before-commit) を再実行する。フェーズ再突入は 1 回まで。qa-ui のラウンド上限は qa-ui 自身の既存規則 (ラウンド3 + root cause 例外1) をそのまま使う (deliver-from-spec 側で別途上限を設けない)。

## Phase 4: 出荷ゲート → create-pr → 監査パック

1. 出荷ゲート bash (SKILL.md 本文) を実行する
2. Critical 0 件なら `/create-pr` を起動する (base branch は起点ブランチ、PR 本文生成は create-pr 既存の手順に従う)
3. 監査パック bash (SKILL.md 本文) を実行し、`<plan>.audit-pack.md` を生成する
4. 監査パックのパスを最終報告としてユーザーに提示する（最終監査の同期タッチ）

### Critical が残っている場合

`/create-pr` を起動せず機械停止する。監査パックだけは生成し (現状の escalation 内容を可視化するため)、ユーザーに提示する。ユーザーが Critical 項目を解消したと判断した場合、次のいずれかで先へ進める:
- Phase 2/2.5/3 のいずれかへ再突入し実際に修正する（フェーズ再突入は 1 回まで。既に 1 回使っている場合はこれ以上の機械再開をせず、ユーザー自身の `/create-pr` 起動に委ねる）
- ユーザーが直接 `/create-pr` を起動する（本 skill のゲートを介さない、ユーザー自身の判断による上書き）

escalation ledger は追記専用で解決済みマークの仕組みを持たないため、一度記帳された Critical 行は台帳上に残り続ける。出荷ゲートの再判定を機械的に「解除」する機構は薄い版のスコープに含めない (薄い版はゲートの機械停止までが責務であり、解除は人間判断に委ねる)。
