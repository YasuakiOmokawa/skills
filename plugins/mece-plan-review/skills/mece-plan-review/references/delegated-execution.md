# 委譲実行

委譲起動時の読み替え。単独起動の現行動作は変えない。判定は観測可能な capability と入力だけで行う。

- **入力解決の優先順位**: ① `$ARGUMENTS` → ② 起動プロンプト本文で明示されたプランファイルパス → ③ セッション文脈・システムプロンプトの `Plan File Info:` (単独起動時のみ有効)。①〜③のいずれでも解決できない場合、「不足入力: プランファイルパス」を最終メッセージで返し、返答を待たず終了する。
- **対話分岐の読み替え**: synchronous user-input capability がない場合、確認したかった内容と現状を最終メッセージに含めて終了する (呼び出し元が人間へ中継し、回答を添えて再起動する)。
- **独立 executor 不可時の fallback**: 必要な同時実行枠を1回取得し、capability 不在・capacity reject・hung のいずれかなら利用不能と確定する。追加 retry はせず、deep Step 1 を inline 実行 (standard 手順流用) へ切り替え、Step 2 は [synthesis-and-errors.md](synthesis-and-errors.md) のフォールバックに従う。
- **`${CLAUDE_PLUGIN_ROOT}` の解決**: 本文・agents / references 中に生文字列で残っている場合、SKILL.md が置かれているディレクトリを skill root とみなし `${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/` をそこへ読み替える。dispatch へ渡す全パス ([dispatch-prompts.md](dispatch-prompts.md) のテンプレート含む) は読み替え後の絶対パスにする。
- **完了報告**: Step 3 完了時の最終メッセージに、3-4 の 1 行サマリーに加えて (a) 分析ファイルの絶対パス、(b) MECE判定 (OK/要修正) と Critical 件数、を明記する。
