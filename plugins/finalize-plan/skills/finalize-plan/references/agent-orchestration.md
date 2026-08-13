# Planner dispatch contract (standard / deep only)

lite には適用しない。standard / deep は QA-ID enumerate 後、次の2 Taskを同一メッセージで並列起動する。`${CLAUDE_PLUGIN_ROOT}` は SKILL.md の規則で絶対パスへ解決する。

```text
Read ${CLAUDE_PLUGIN_ROOT}/skills/finalize-plan/agents/manual-qa-planner.md.
Generate manual QA from PLAN_CONTENT, ENUMERATED_QA_AC, and MECE_CONTENT.

Read ${CLAUDE_PLUGIN_ROOT}/skills/finalize-plan/agents/auto-qa-planner.md.
Generate automated-test specifications from PLAN_CONTENT, ENUMERATED_QA_AC, and MECE_CONTENT.
```

Task 不可時は両 agent 定義を絶対パスで Read し、main agent が順次適用する。`## 実装準備` 直下へ次を挿入する。

```markdown
> **備考**: 本実行は Task ツール利用不可のため in-context 代替モードで実行 (2 agent 定義をメイン agent が逐次適用)。
```
