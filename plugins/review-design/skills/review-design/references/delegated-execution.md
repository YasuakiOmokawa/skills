# 委譲実行 (subagent として起動された場合)

委譲が明示された場合、単独起動の動作に次を追加する。tool 名から委譲や対話可否を推測しない。

- **入力解決**: `Plan File Info:` と会話文脈は単独起動時のみ有効な経路であり、委譲時は試みない。起動プロンプト本文の明示指定のみを `$ARGUMENTS` として扱う。$ARGUMENTS からプランファイルパスも feature description も得られない場合のみ、「不足入力: レビュー対象のプランファイルまたは feature description」を最終メッセージで返し即座に終了する (返答を待たない)。パス文字列が渡されているが指す先のファイルが存在しない場合も同様に即時終了する (内容を捏造せず、その旨を返して完結する)。
- **Independent executor 不可時**: parallel reviewer capability が無い場合、main agent が [reviewer-modes.md](reviewer-modes.md) の fallback に従い `agents/*.md` を自ら読んで適用する。
- **Design It Twice**: [deep-modules-quickref.md](deep-modules-quickref.md) の比較を、対話不能な委譲実行でも確認待ちで止めず完遂する。
- **`${CLAUDE_PLUGIN_ROOT}` の解決**: `agents/*.md` を `Read` で直接実行しており本文中に `${CLAUDE_PLUGIN_ROOT}` が生文字列で残る場合、プレフィックス `${CLAUDE_PLUGIN_ROOT}/skills/review-design/` 全体を、いま読んでいる agent ファイルの 1 階層上 (skill root = `.../skills/review-design/`) に写像して解決する (`${CLAUDE_PLUGIN_ROOT}` 単体は plugin root = `skills/` の親ディレクトリを指す)。nested `Task` へ埋め込むパスは解決後の絶対パスにする。
- **完了報告**: Step 6 の最終メッセージ・保存ファイルの規定は [final-report-format.md](final-report-format.md) のとおり (委譲・単独起動で同一)。
