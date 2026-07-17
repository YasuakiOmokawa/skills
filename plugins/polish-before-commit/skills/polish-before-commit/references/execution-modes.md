# 実行モード別の読み替え (polish-before-commit)

SKILL.md の通常フロー (単独起動・自ブランチ・ファイル編集可) に対する、低頻度モードの読み替えを集約する。該当モードに入ったときのみ本ファイルを読む。Orchestrated モードの記帳規則は [orchestrated-mode.md](orchestrated-mode.md) が正本。

## review-only モード (ファイル変更不可)

**review-only モード (ファイル変更不可)**: user が「ファイル変更はしない」「レビューのみ」「他者の PR」を指示した場合は編集せず、auto-fix Step (4/5/6/7) は候補提示に留め各 Step を `[<Step>: review-only により提案のみ]` と報告する (`<Step>` は各 Step のレポート文言表 bracket 内の実 label に厳密一致させる: `パターン一貫性` / `lint` / `dead mock` / `コメント改善`。variant 表を label の SSOT とし本文の言及とズレたら表を優先する)。**review-only overlay は Step 4/5/6/7 の tier 由来 skip・条件由来 skip の両方より優先する** (user 明示指示は最上位のため、たとえ Step 6 が条件不一致 (Ruby なし等) で通常なら条件バリアントを出す場面でも review-only 時は `[dead mock: review-only により提案のみ]` を出力する)。実行するのは Step 1 (規約収集) + Step 8 (最終レビュー) + Step 9 (集約)。対象が Ruby/TS/JS/Python 外 (Helm/YAML 等) の場合も Step 4/5/6/7 は言語スコープ外として skip し Step 8 中心で点検する (どちらも編集せず点検に倒す点は同じ)。明示指示が無い場合の一次検出は「## 委譲実行」節を参照。

## 他者 PR の点検時の Step 9 読み替え

**他者 PR の点検時の Step 9 読み替え**: 読むファイルも PR head ブランチ名で引き (`quality-review-handoff-<PR head ブランチ名>.md`)、申し送りの採用判定は「`branch:` == 点検対象 (PR head ブランチ名)」で行う (カレントブランチ基準にすると自ブランチ宛の無関係な申し送りを混入させる)。自ブランチ宛の申し送りは採用もクリアもしない — Step 9 の申し送りファイル削除 (`rm`) は自ブランチのフロー最終段でのみ実行する。終了文言は「コミットへ進めますか?」でなく「レビュー点検完了。指摘一覧を確認してください」とする (commit する対象が無いため)。

## 委譲実行 (subagent として起動された場合)

以下は、本 skill が `Task` で委譲された subagent として動く場合にのみ関係する読み替えである。判定はいずれも「利用可能ツール一覧」という観測可能な条件で行い、文字列一致による推測はしない。単独起動 (メイン会話でユーザーが直接起動) の現行動作はこれらの条件に当てはまらない限り変えない。

- **Orchestrated モード**: 発動条件・記帳先・記帳規則は SKILL.md の「Orchestrated モード」段落と [orchestrated-mode.md](orchestrated-mode.md) が正本 (本節では繰り返さない)。
- **review-only の一次検出**: `AskUserQuestion` が利用可能ツール一覧に無く、かつ実行モードの明示指定 (review-only / orchestrated 等) も起動プロンプトに無い場合に限り、`git log -1 --format='%an'` と `git config user.name` を比較する。不一致なら review-only を既定にする (ユーザーに確認できない状況で他者のブランチを誤って auto-fix する事故を防ぐため)。一致する場合、または `AskUserQuestion` が利用可能な単独起動では、現行どおり明示宣言が無い限り通常モードのまま進む。
- **Task / Skill 不可時の fallback**: `Task` が利用可能ツール一覧に無い場合のみ、Step 3 (パターン一貫性の並列処理) は並列化せず main thread で順次処理する。`Skill` が利用可能ツール一覧に無い場合のみ、Step 8 (最終レビュー) は同 Step 記載の fallback 手順に切り替える。
