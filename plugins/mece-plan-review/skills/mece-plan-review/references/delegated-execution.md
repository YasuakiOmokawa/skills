# 委譲実行 (subagent として起動された場合)

Task で委譲起動された場合の読み替え。単独起動 (メイン会話でユーザーが直接起動) の現行動作は変えない。判定基準はすべて観測可能な条件 (利用可能ツール一覧) であり、実行文脈の推測では判定しない。

- **入力解決の優先順位**: ① `$ARGUMENTS` → ② 起動プロンプト本文で明示されたプランファイルパス (Task 委譲時はこれが `$ARGUMENTS` 相当) → ③ セッション文脈・システムプロンプトの `Plan File Info:` (単独起動時のみ有効)。①〜③のいずれでも解決できない場合、「不足入力: プランファイルパス」を最終メッセージで返し、返答を待たず終了する。
- **AskUserQuestion 分岐の読み替え**: AskUserQuestion が利用可能ツール一覧に無い場合 (= subagent 実行)、確認したかった内容と現状を最終メッセージに含めて終了する (呼び出し元が人間へ中継し、回答を添えて再起動する)。対話承認者がいるかの判定基準は AskUserQuestion の利用可否そのもの。
- **Task 不可時の fallback**: Task (Agent) ツールが利用可能ツール一覧に無い場合のみ、deep の Step 1 も本文記載の inline 実行 (standard inline 手順流用) に切り替える。Step 2 (Fresh Red Team) は [synthesis-and-errors.md](synthesis-and-errors.md) の「Red Team subagent 失敗」節のフォールバックに従う。
- **`${CLAUDE_PLUGIN_ROOT}` の解決**: 本文・agents / references 中に生文字列で残っている場合、SKILL.md が置かれているディレクトリを skill root とみなし `${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/` をそこへ読み替える。nested Task へ埋め込む全パス ([dispatch-prompts.md](dispatch-prompts.md) のテンプレート含む) は読み替え後の絶対パスにする。
- **完了報告**: Step 3 完了時の最終メッセージに、3-4 の 1 行サマリーに加えて (a) 分析ファイルの絶対パス、(b) MECE判定 (OK/要修正) と Critical 件数、を明記する。
