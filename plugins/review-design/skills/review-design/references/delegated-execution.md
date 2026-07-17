# 委譲実行 (subagent として起動された場合)

Task ツールで委譲された場合、単独起動 (メイン会話でユーザーが直接起動) の動作に次を追加する。判定基準は「AskUserQuestion が利用可能ツールに無いか」で機械的に行う。

- **入力解決**: `Plan File Info:` と会話文脈は単独起動時のみ有効な経路であり、委譲時は試みない。起動プロンプト本文の明示指定のみを `$ARGUMENTS` として扱う。$ARGUMENTS からプランファイルパスも feature description も得られない場合のみ、「不足入力: レビュー対象のプランファイルまたは feature description」を最終メッセージで返し即座に終了する (返答を待たない)。パス文字列が渡されているが指す先のファイルが存在しない場合も同様に即時終了する (内容を捏造せず、その旨を返して完結する)。
- **Step 3 の Task 不可時**: reviewer dispatch (`Task`) が利用可能ツール一覧に無い場合、main agent が [reviewer-modes.md](reviewer-modes.md) の Parallel Review fallback に従い `agents/*.md` を自ら Read して適用する。
- **Design It Twice (deep-module-reviewer escalation)**: [deep-modules.md](deep-modules.md) の問題空間提示 (Step 1) は、対話承認者がいない (= AskUserQuestion が利用可能ツールに無い) 実行では提示のみで確認を待たず、即座に Step 2 (sub-agent 並列起動) へ進む。
- **`${CLAUDE_PLUGIN_ROOT}` の解決**: `agents/*.md` を `Read` で直接実行しており本文中に `${CLAUDE_PLUGIN_ROOT}` が生文字列で残る場合、いま読んでいる agent ファイルの 1 階層上 (`skills/review-design/`) を skill root とみなして解決する。nested `Task` へ埋め込むパスは解決後の絶対パスにする。
- **完了報告**: Step 6 の最終メッセージ・保存ファイルの規定は [final-report-format.md](final-report-format.md) のとおり (委譲・単独起動で同一)。
