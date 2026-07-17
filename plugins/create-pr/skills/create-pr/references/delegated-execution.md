# 委譲実行 (subagent として起動された場合)

`Task` ツールで委譲された場合、以下を既定手順に対する読み替えとして適用する。単独起動時の現行動作は変えない。

- **Step 4c / Step 6 の情報源**: 「背景 / 設計判断 / やらなかったこと」抽出と詳細展開指示は「本セッションの発話」を一次情報源とするが、委譲実行では会話履歴が渡らずこの経路が成立しない。起動プロンプト本文に明示転記された記述があればそれを一次情報源とし、無ければ [description-style.md](description-style.md) のファイルベース代替 (diff・commit メッセージ・関連 Issue) へ進む。存在しない発話・議論を創作しない。
- **AI Contribution 判定 ([labels-and-milestones.md](labels-and-milestones.md) b.)**: 判定フローチャートの「本セッション内で」は「当該 diff を生成した先行セッション（委譲元を含む）」と読み替える。先行セッションでの生成経緯を確認できない場合は同ファイル rule 4（既定 + 推定注記）に従う。
- **ブランチ状態が複雑な場合 ([branch-validation.md](branch-validation.md))**: `disallowed-tools: AskUserQuestion` によりどの起動経路でも対話確認はできない。状況説明を最終メッセージに含めて処理を終了する（返答を待たない）。
- **`gh` コマンドが GitHub ホスト解決に失敗する環境**: `gh pr create` に限らず `gh repo view`（ベースブランチ解決）や `gh api .../milestones`（Untracked 事前確認、[labels-and-milestones.md](labels-and-milestones.md) 参照）も同一エラーで失敗しうる。`gh pr create` が失敗した場合は組み立て済みコマンド全文・生成済みタイトル・本文を最終メッセージに含めて終了する（存在しない PR URL を返さない）。
