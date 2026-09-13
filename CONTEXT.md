# Repository context

## Layout

- Skill: `plugins/<name>/skills/<name>/SKILL.md`
- Outcome evaluation: `plugins/<name>/evals/outcomes.md`
- Eval case: `plugins/<name>/evals/<NN-slug>/prompt.md` と `graders/*.md`
- Chain eval case: `evals-chain/<slug>/`。複数pluginを繋いだ流れを測る。case frontmatter の `plugins:` に対象pluginを列挙し、repository rootを対象にして `--eval-dir evals-chain` で走らせる
- Plugin manifest: `plugins/<name>/.claude-plugin/plugin.json`
- Marketplace manifest: `.claude-plugin/marketplace.json`

Skillとcommandはファイル配置からdiscoveryされる。agent定義は置かない。plugin manifestへdiscovery配列は書かない。

## Global configuration

非機密のマシン設定は `~/.claude/skills-config/` に置く。

- `jira.md`: personal Jira plugins
- `create-design-doc/dd_template.md` と `dd_reference.md`: 任意。存在しなければ取得済み根拠へ縮退する
- `vision.md`: career pluginに必須

API key、access token、passwordはこの領域へ保存しない。

## Contracts

- Skill入力は自然文と利用可能なtask contextであり、skill固有argument schemaを持たない。
- `apply-findings` の明示的review-only以外にnamed modeを持たない。
- Skillは別skillを暗黙起動せず、必要な後続作業を結果として返す。
- PoC、プロトタイプ、Design Docの受け渡しは、出力先直下の案件ディレクトリ（`<案件slug>/`）にある `poc.md` のパスで行う。`poc.md` の見出し（問い、星取表、結論、PR、申し送り、Prototype）と `design-doc.md` は後続skillが読むmachine contract。
- 固定見出し、ID、列、状態値は、skill外のconsumerが実際に読む場合だけmachine contractとする。
- 外部状態の変更と破壊的操作は、正確な対象と変更内容が依頼で承認された場合だけ行う。

## Evaluation

`outcomes.md` は `Trigger`、`Outcome`、`Authorization`、`Hold-out` の4節を持つ。構造は `scripts/validate_skills.py`、振る舞いはfresh executorとblind judgeで検証する。

`outcomes.md` が仕様、`evals/<NN-slug>/` が計測器。計測器は `claude plugin eval` が実行し、pluginを有効にしたarmと無効にしたarmを比較する。

### 計測器の作り方

- 入力は実トラフィックから取る。`~/.claude/projects/<repo>/*.jsonl` のskill呼び出し直前のuser promptを読む。SKILL.mdの例文を入力にしない。
- 実プロンプトは複数skillを連ねたpipeline形である。後続skillはサンドボックスに無いため、対象skillまでで切った部分集合を入力にする。
- fixtureは各 `prompt.md` 冒頭のbash heredocで作業ディレクトリに生成する。絶対パスと `~/` は使わない。
- caseは `outcomes.md` のassertionに対応させる。対応の無い振る舞いをcaseにしたら、先に `outcomes.md` へassertionを足す。
- graderは `outcomes.md` を見て書く。SKILL.mdの語彙を写すと過適合する。仕様の書式リテラルを使うなら `weight: 0.5` の二次判定に留め、一次はoutcome graderにする。
- 「欠落の無いplan」を意図したfixtureは本当に欠落を無くす。非同期は `await` ごとにreject経路を数える。仕込み損ねると、正しく指摘したarmをgraderが罰する。
- llm rubricは「1観測 = 1 criterion」で分割された出力をfailにしないよう、複数criterionにまたがる充足を明示的に可とする。
- suiteにskillが発火してはならない負例を1件以上残す。`tool_used` だけのcaseは作らない。

### 実行

```bash
cd plugins/<name>
claude plugin eval . --ablation with-without --judge-model sonnet --allow-tools "Write,Edit,Bash"
```

`--allow-tools` はSKILL.mdに `allowed-tools` frontmatterが無い場合の運用側付与で、全caseに効く。見る数字はΔ（withスコア引くwithoutスコア）。7 caseで1回およそ$21、85分。

### 改善ルーティン

1. 仕様変更を `outcomes.md` のassertionとして先に書く。
2. SKILL.mdを触る前にsuiteを回し、caseごとのΔをベースラインにする。suiteは実行ごとにディスク上のpluginを読むため、実行中にSKILL.mdを編集しない。
3. SKILL.mdを編集するagentには `outcomes.md` とeval結果（スコア、落ちたgrader名、trace抜粋）だけ渡す。`prompt.md` と `graders/` は渡さない。
4. 編集後にsuiteを回しcaseごとのΔを比較する。1つでも下がれば回帰。負例のwithスコア低下はover-trigger。
5. 新しい振る舞いを足したときだけ、対応するcaseを1つ追加する。

曖昧さの発見は編集のたびに `empirical-prompt-tuning`、回帰検出はPR前のsuiteが担う。

### runnerのクセ

- pilotは `--runs 1 --no-publish`。`aggregate-result.json` の `suite.plugins` に対象pluginが載り `problem` が無いことを確認する。載っていなければwith armがplugin無しで走っており、pilotは無意味。
- `--case` を複数回渡しても最後の1つしか効かない。`0[23]-*` のようなbracket globは0件になる。複数caseはループで1つずつ回す。
- `report.html` と `aggregate-result.json` はjudgeの理由文を保存しない。判定を検証するには `--keep-temp` が残すsandboxの `out/trace.jsonl` の最終assistant textを読む。
- llm graderのjudgeはthinking無効・一語 (PASS/FAIL) 回答・temperature 1の3票多数決で、理由文は生成すらされない。judgeに見せた本文は `aggregate-result.json` の `graders[].evidence` に残るので、判定を検証するにはそれを同じprompt (`You are grading the output of a coding agent against a criterion.` / `Criterion:` / `Agent output (file <path>):` / `Respond with exactly one word: PASS or FAIL.`) でsonnetに投げ直す。
- 上の性質から、多条項で例外規定の多いrubricは正解にも3票FAILを付け、whitelist照合 (「この一覧に無い名前を挙げていればfail」) は票が割れる。rubricは1 graderにつき1論点で短く書き、実在性の照合はfixtureに無いパスを `not_contains` で検出するregexにする。
- `--keep-temp` のsandboxで `home/` と `tmp/` はmode 000で封印され、chmodは許可されない。書き込まれたファイルの内容は `out/trace.jsonl` のWrite/Edit入力から復元する。
- 負例caseでもagentがBashにturnを使うため、10 turn程度は与える。
