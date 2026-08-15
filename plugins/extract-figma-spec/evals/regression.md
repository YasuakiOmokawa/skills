# regression eval

## A: explicit URL and output path, metadata unavailable

A delegated run receives Figma URL `https://www.figma.com/design/AbCdEf123/todo-app?node-id=1-234` and an existing plan path. No Figma metadata capability is available.

Checklist:
1. [critical] resolves the node as `1:234`, reports the missing capability, and stops without fabricated atoms;
2. [critical] leaves the existing plan unchanged, including no `## 正本抽出結果` section;
3. reports `正本抽出結果: 未生成` and asks the user to open the target file in the Figma desktop app;
4. does not retry a missing tool or write diagnostics to the output path.

## B: successful extraction without an output path

A delegated run receives node `1:234`, structured metadata, design context, variables, a screenshot, and implementation code. The metadata resolves eight applicable properties, including one explicit `none`, two implementation differences, and one unresolved style value after the required deeper lookup. No plan path is supplied.

Checklist:
1. [critical] creates continuous `FIG-01` onward atoms for every resolved applicable property and treats explicit `none` as a fact;
2. [critical] classifies every resolved atom as `一致`, `差分`, or `未実装` from structured/code evidence, not screenshot similarity;
3. keeps the unresolved style out of resolved rows and reports its source and reason separately;
4. returns the full canonical table in the final response with `未書き込み` and invents no path.

## C (holdout): ambiguous node selection

A delegated run receives only the concrete request keyword `priority tab`. Accessible pages contain `Priority Tab v0`, `Priority Tab v1`, `Components`, and `Cover`; both versioned pages contain plausible matching descendants. A plan path is supplied, but synchronous clarification is unavailable.

Checklist:
1. [critical] inspects enough metadata to identify both plausible candidates and does not use `v0` / `v1` as uniqueness evidence;
2. [critical] returns the candidate nodes and stops without choosing one or fabricating atoms;
3. leaves the plan unchanged and reports `正本抽出結果: 未生成` with the unresolved reason;
4. requests an explicit node selection in the final response.

## D (holdout): normal planning pipeline with a new analysis file

Extraction and comparison are complete for eight atoms. `FIG-03`, `FIG-06`, and `FIG-07` are differences. The work is not identified as a PoC, a plan path is supplied, and the analysis file does not yet exist.

Checklist:
1. [critical] creates the analysis file and persists the full canonical table before invoking `/define-acceptance-criteria`;
2. [critical] the downstream definition reads that table and transfers all three differences to generated acceptance criteria;
3. [critical] does not also add a plan reflection checklist after the acceptance criteria have actually been generated;
4. writes `## 正本抽出結果` with all eight resolved atom rows and a separate unresolved list;
5. reports the written absolute path and does not rewrite a QA ledger.
