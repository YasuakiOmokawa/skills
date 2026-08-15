# 会話履歴を持たない委譲実行

委譲実行では以下を既定手順へ適用する。単独起動時の現行動作は変えない。

- **Step 4c / Step 6 の情報源**: 起動プロンプト本文 → diff → commit メッセージ → verified related Issue の順。存在しない発話・議論を創作しない。
- **AI Contribution 判定**: 当該 diff を生成した先行処理（委譲元を含む）の authorship も数える。確認不能なら PR 本文へ推測を書かず、完了報告で不確実性を示す。
- **ブランチ状態が複雑な場合 ([branch-validation.md](branch-validation.md))**: 状況説明を最終メッセージに含めて処理を終了する（返答を待たない）。
- **`gh` コマンドが GitHub ホスト解決に失敗する環境**: `gh pr create` に限らず `gh repo view`（ベースブランチ解決）や `gh api .../milestones`（Untracked 事前確認、[labels-and-milestones.md](labels-and-milestones.md) 参照）も同一エラーで失敗しうる。`gh pr create` が失敗した場合は組み立て済みコマンド全文・生成済みタイトル・本文を最終メッセージに含めて終了する（存在しない PR URL を返さない）。
