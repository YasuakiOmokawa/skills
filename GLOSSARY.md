# Repository context

## Layout

- Skill: `plugins/<name>/skills/<name>/SKILL.md`
- Outcome evaluation: `plugins/<name>/evals/outcomes.md`
- Eval case: `plugins/<name>/evals/<NN-slug>/prompt.md` と `graders/*.md`
- Chain eval case: 複数pluginを繋いだ流れを測るときは、case frontmatter の `plugins:` に対象pluginを列挙し、それらを含むrootを対象にして `--eval-dir <dir>` で走らせる
- Plugin manifest: `plugins/<name>/.claude-plugin/plugin.json`
- Marketplace manifest: `.claude-plugin/marketplace.json`

Skillとcommandはファイル配置からdiscoveryされる。agent定義は置かない。plugin manifestへdiscovery配列は書かない。

## Global configuration

非機密のマシン設定は `~/.claude/skills-config/` に置く。

- `create-design-doc/dd_template.md` と `dd_reference.md`: 任意。存在しなければ取得済み根拠へ縮退する

API key、access token、passwordはこの領域へ保存しない。

## Contracts

- Skill入力は自然文と利用可能なtask contextであり、skill固有argument schemaを持たない。
- `apply-findings` の明示的review-onlyと、`define-done` の依頼に「問い返し」とあるときの問い返し以外にnamed modeを持たない。
- Skillは別skillを暗黙起動せず、必要な後続作業を結果として返す。
- PoC、プロトタイプ、Design Docの受け渡しは、出力先直下の案件ディレクトリ（`<案件slug>/`）にある `poc.md` のパスで行う。`poc.md` の見出し（問い、星取表、結論、PR、申し送り、Prototype）と `design-doc.md` は後続skillが読むmachine contract。
- 固定見出し、ID、列、状態値は、skill外のconsumerが実際に読む場合だけmachine contractとする。
- 外部状態の変更と破壊的操作は、正確な対象と変更内容が依頼で承認された場合だけ行う。例外として、`build-poc` と `build-prototype` の起動は、検証用ブランチのpushと、元のブランチをbaseとするdraft PRの作成の承認を含む。`define-done` の起動は、受け入れテストと計画だけを含む封の commit を作る承認を含む (push は含まない)。PRのURLは後続skillが読む。依頼が外部状態の変更を禁じる場合は行わない。

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
- graderを足したら、既存のrunのtraceで、そのgraderが判定する段までrunが届いているかを確かめてから回す。Gateで止まるcaseに受け入れテストの段のgraderを置いても、何も測らない。
- skillの契約を変えたら、参照を辿って全graderを新しい契約に照らす。新旧比較で2 run以上落ちたgraderは、skillを直す前に、graderが今の契約に合っているかを確かめる。
- 変異の題材 (`scripts/eval/mutant/`) の採点用テストは全referenceで通り、手書きの変種を全部検出する。`scripts/test_mutant_score.py` が全題材でこれを検査する。chain caseの正解は `evals-chain/outcomes.md` に書く。

### 実行

```bash
cd plugins/<name>
claude plugin eval . --ablation with-without --judge-model sonnet --allow-tools "Write,Edit,Bash"
```

`--allow-tools` はSKILL.mdに `allowed-tools` frontmatterが無い場合の運用側付与で、全caseに効く。見る数字はΔ（withスコア引くwithoutスコア）。7 caseで1回およそ$21、85分。

### 新旧の比較

`scripts/eval/` の道具で、旧版 (main) と新版を `/tmp` の複製で並列に回し、grader 単位で比べる。

```bash
python3 scripts/eval/mkvariant.py plugins/<name> plugins/<name>/skills/<name>/SKILL.md /tmp/<name>-old
python3 scripts/eval/mkvariant.py plugins/<name> <新しい SKILL.md> /tmp/<name>-new
(cd /tmp/<name>-old && claude plugin eval . --ablation none --judge-model sonnet --allow-tools "Write,Edit,Bash" --no-publish --trust-plugin --json /tmp/<name>-old.json)
python3 scripts/eval/compare.py old=@plugins/<name> new=/tmp/<name>-new.json
python3 scripts/eval/rejudge.py /tmp/<name>-new.json <NN> plugins/<name>/evals/<NN-slug>/graders/<grader>.md
```

`mkvariant.py` は4番目以降の引数に渡した句を SKILL.md から1箇所ずつ消した版を作る (句を外した版の with run)。`compare.py` はカンマ区切りで複数の結果を1列に合算する (`--case` で再実行した分を足す)。`@plugins/<name>` は `last-run.json` が case ごとに記録した `startedAt` から `evals/results/<startedAt>/aggregate-result.json` を読む。新しい結果を `eval_coverage record` する前なら、旧版の記録になる。results は gitignore なので、記録を書いたマシンでだけ読める。`rejudge.py` は FAIL した run の evidence を同じ criterion で sonnet に3票判定し直す。llm judge が多条項の rubric を誤って FAIL にしたかを確かめるのに使う。

### 翻訳の質 (define-done)

define-done の受け入れテストは、runner の外で決定論的に採点する (runner には出力にコマンドを流す grader が無い)。題材ごとに `scripts/eval/mutant/<題材>/` に次を置き、eval の case の dir に `mutant.json` (`{"subject": "scripts/eval/mutant/<題材>", "test": "<受け入れテストの相対 path>"}`) を置く。

- `subject.json`: `{"target": "<テストが import する製品コードの path>", "references": [...]}`。`references` は省略すると `["reference.js"]`
- `reference.js` (と `references` に挙げた他の参照実装): 要求どおりの実装。2 つ目以降は、資料が決めていない振る舞い (状態コード、上限、境界ちょうど) だけを変える。テストはすべての参照実装で通るときだけ有効と数え、資料に無い値を期待するテストは、推測が 1 つ目と一致しても無効になる
- `stub.js`: 変更前のコード (受け入れテストが落ちるべき状態)
- `mutants.json`: 要求を破る手書きの変種。`find` と `replace`、離れた箇所を変えるなら `edits` の列で書き、各 `find` は参照実装にちょうど 1 回当たる。実バグの修正前を写した変種は id を `real-` で始める
- `test/hidden.test.js`: 自己検査用の隠しテスト

手書きの変種と隠しテストは、題材の資料が決めていることだけを破り、確かめる。隠しテストの名前と変種の `requirement` には、根拠の文 (`S-n`、要件の番号、用語集の項目) を書く。資料が二通りに読める点を片方の読みで破る変種を置くと、曖昧さを未決の判断として返す define-done が、推測して書いた素のモデルより低く出る。

```bash
python3 -I scripts/eval/mutant_score.py scripts/eval/mutant/<題材> scripts/eval/mutant/<題材> test/hidden.test.js
cd plugins/define-done && claude plugin eval . --case <case> --ablation with-without --keep-temp ... --json /tmp/<name>.json
python3 -m scripts.eval.score_results /tmp/<name>.json --record
```

1 行目は計測器の自己検査で、隠しテストがすべての参照実装で通り、手書きの変種を全部落とすことを確かめる。2 行目は `--keep-temp` を必ず付ける。3 行目は trace から受け入れテストを `<name>.json.restored/` に復元し、arm ごとの表を出し、`evals/mutant-record.json` に shipped の中身の hash ごとに記録する。sandbox を消すのは 3 行目の後にする。見る数は次のとおり。

- 全テストが有効な run: 資料に無い値や振る舞いを期待するテストを書かなかった run
- 要件適合度: 有効なテストで落とした手書きの変種 / 全変種
- バグ検出率: 有効なテストで落とした自動の変異 / 隠しテストが落とせる自動の変異。自動の変異は比較・論理・算術演算子の入れ替え、数値の ±1、真偽値の反転、`!` の除去、式の文の削除で作り、隠しテストも落とせないものは等価とみなす
- テストを書いた run: 書かなかった run は最終回答から Gate での停止とそれ以外を分ける

### コードの水準 (chain eval)

`evals-chain/<case>/` の case は frontmatter の `plugins:` に define-done を置き、repo root から `claude plugin eval . --eval-dir evals-chain --ablation with-without --keep-temp` で走らせる。依頼文は成果物 (受け入れテストの置き場所と、実装するファイル) を平文で書き、作業の最後に両方を `cat` で表示させる。エージェントは製品コードを heredoc や `python3 -` で書き換えるので、trace の Write/Edit からは最終状態を再現できない。`score_results` は最後の `cat` の出力を最終状態とし、`mutant.json` に `"code": true` があれば、製品コードに隠しテストを流して「隠しテストを全部通したコード」を数える。Gate で止まって製品コードが stub のままの run は未実装と数える。

### 改善ルーティン

1. 仕様変更を `outcomes.md` のassertionとして先に書く。
2. SKILL.mdを触る前にsuiteを回し、caseごとのΔをベースラインにする。suiteは実行ごとにディスク上のpluginを読むため、実行中にSKILL.mdを編集しない。
3. SKILL.mdを編集するagentには `outcomes.md` とeval結果（スコア、落ちたgrader名、trace抜粋）だけ渡す。`prompt.md` と `graders/` は渡さない。
4. 編集後にsuiteを回しcaseごとのΔを比較する。1つでも下がれば回帰。負例のwithスコア低下はover-trigger。
5. 新しい振る舞いを足したときだけ、対応するcaseを1つ追加する。

SKILL.mdの本文は `## 目的` / `## 原理` / `## 契約` / `## 禁止` / `## 完了条件` の5節に限る (`scripts/validate_skills.py` が検査する)。新旧の版は `--ablation none` のwith runをgrader単位で比べ、graderを次の5種に分けて合否を決める。

- 契約・禁止・完了条件: 新版が旧版より下がれば不合格。
- 原理: スキルの原理を観測するgrader。新版は旧版以上を保つ。既存graderで足りなければ足す。
- 癖対策: 素のモデルの癖を抑える句だけが支えるgrader。参考値とし、下がった分は受け入れた損失としてPRに列挙する。

n=3では2 run以上の差だけを有意とする。without armで素のモデルが通っていても、スキルの他の句と組み合わさると要る句がある。

曖昧さの発見は編集のたびに `empirical-prompt-tuning`、回帰検出はPR前のsuiteが担う。

### assertion と grader の対応

`outcomes.md` の `- assertions:` の下の各行は、行末に `(grader: <case>/<grader>[, ...])` を持つ。測る grader が無い assertion は `(grader: 未計測)` と書く。各 grader はちょうど 1 つの assertion から参照される (1 grader 1 論点)。`scripts/validate_skills.py` が双方向に照合し、参照先の無い grader、assertion の無い grader、2 つの assertion から参照される grader を落とす。skill の契約を変えたら、参照を辿って全 grader を新しい契約に照らす。

### 網羅の記録

plugin の `skills/` か `commands/` を変えた PR は、`plugins/<name>/evals/last-run.json` に、変えた後の中身で全 case を回した記録を持つ。記録は `python3 -m scripts.eval_coverage record plugins/<name> <result.json>...` で書く (同じ中身の記録には case を足していける)。回さないと決めたら `python3 -m scripts.eval_coverage waive plugins/<name> "<理由>"` で理由を残す。CI の `eval_coverage check` は、中身の hash が記録と違うか、回していない case があり理由も無ければ落とす。

### runnerのクセ

- pilotは `--runs 1 --no-publish`。`aggregate-result.json` の `suite.plugins` に対象pluginが載り `problem` が無いことを確認する。載っていなければwith armがplugin無しで走っており、pilotは無意味。
- `--case` を複数回渡しても最後の1つしか効かない。`0[23]-*` のようなbracket globは0件になる。複数caseはループで1つずつ回す。
- `report.html` と `aggregate-result.json` はjudgeの理由文を保存しない。判定を検証するには `--keep-temp` が残すsandboxの `out/trace.jsonl` の最終assistant textを読む。
- llm graderのjudgeはthinking無効・一語 (PASS/FAIL) 回答・temperature 1の3票多数決で、理由文は生成すらされない。judgeに見せた本文は `aggregate-result.json` の `graders[].evidence` に残るので、判定を検証するにはそれを同じprompt (`You are grading the output of a coding agent against a criterion.` / `Criterion:` / `Agent output (file <path>):` / `Respond with exactly one word: PASS or FAIL.`) でsonnetに投げ直す。
- 上の性質から、多条項で例外規定の多いrubricは正解にも3票FAILを付け、whitelist照合 (「この一覧に無い名前を挙げていればfail」) は票が割れる。rubricは1 graderにつき1論点で短く書き、実在性の照合はfixtureに無いパスを `not_contains` で検出するregexにする。
- `focus: trace` のllm graderに渡るevidenceは、メッセージが24件を超えると先頭12件と末尾12件だけに間引かれ、traceの途中のメッセージが落ちる (80KBのtraceでassistant 37件中11件しか残らない)。途中で起きた手順 (refactorの編集、一時違反によるred) は正解でも3票FAILになり、逆に最終報告から推測したPASSも出る。手順の有無は `type: regex`、`target: trace`、`flags: s` で全traceを照合する。tool_useの順序は `"name":"(?:Write|Edit)","input":\{[^{}]*?"file_path":"[^"]*<path>"` を区切りにしたtempered regexで書く。テスト失敗は `"type":"tool_result","content":"` の内側に限る。agentのgrepコマンド文字列 (`not ok`、`✖`) にも一致するため。
- traceのJSONでは改行が `\n` の2文字になる。改行直後のコマンドの前では `\b` が効かないので、コマンドの区切りは `(?:\\n|;|&&|\|\||\||\(|\{)` のように明示する。Bashの1回の呼び出しで書き込みと読み直しを済ませる手順も、Write/Edit の後の別の呼び出しと同じく照合できるregexにする。
- `--ablation none` では `tool_used: Skill` のgraderも採点に入るので、with-without のscoreと比べられない。版どうしの比較はgrader単位の合否で行う。skill-not-firedの負例でも同じgraderが3/3から1/3までぶれるので、3 runの2 run差はノイズとみなす。
- sandboxでは素の `git init` が `.git/config` と `.git/hooks` への書き込み拒否で失敗し、以後のgitは親の `home/.git` に落ちる。gitのfixtureは `git init -q --template= --separate-git-dir=../repo.gitdir -b main .` で作り、remoteは `git init -q --bare --template= ../remote.git` にpushする。graderは `repo.gitdir/logs/HEAD` (reflog) や `remote.git/refs/heads/<b>` を `{source: file, path}` で読める。
- `--keep-temp` のsandboxで `home/` と `tmp/` はmode 000で封印され、chmodは許可されない。書き込まれたファイルの内容は `out/trace.jsonl` のWrite/Edit入力から復元する。
- `eval_coverage record` と `score_results --record` は、`skills/` と `commands/` の中身の hash を `git ls-files` の一覧から計算する。新しく足したファイルが未追跡のまま記録すると、そのファイルが hash から抜け、CI の `eval_coverage check` が別の中身の記録として落とす。記録は `git add` の後に書く。
- `score_results` は結果の `suite.root` を plugin の場所として読み、`git ls-files` で hash を取る。`/tmp` の複製 (git の外) で回した結果は記録できないので、`suite.root` と `suite.plugins[].path` を repo の plugin の path に書き換えた写しを渡す。
- `target: trace` の regex は、Bash の heredoc で書いた本文の中の文字列にも当たる。コマンドの実行を照合する regex は `"command":"(?![^"]*<<)` で heredoc を含むコマンドを除く。
- 負例caseでもagentがBashにturnを使うため、10 turn程度は与える。

## Language

### 完了の定義 (define-done)

**受け入れ基準 (AC)**:
計画が完了したと言える条件。外から観測できる振る舞い (`[振る舞い]`) と、コードにあってはならないもの (`[禁止]`) の 2 種類だけで書く。
_Avoid_: 完了条件 (SKILL.md の節名と紛れる)

**要求**:
依頼・issue・仕様が求めていることを、原文の引用付きで 1 件ずつ挙げたもの。計画の決定からは引かない。
_Avoid_: 要件

**既存の保証**:
変更前の repo に既にある試験・guard (製品コードの中で入力を拒む検査を含む)・不変条件の文書。要求と並んで AC の出典になれる。

**出典**:
AC が何に基づくかを示すもの。要求か既存の保証のどちらかに限る。
_Avoid_: 根拠 (Ground Review の根拠と紛れる)、出どころ

**決定**:
計画が選んだ手順・値・仕組み。変わりうるので AC の出典にはならず、どの要求に仕えるかだけを持つ。
_Avoid_: 設計判断

**受け入れテスト**:
define-done が各 AC から翻訳した、実行できるテスト。テスト名は AC-ID で始まる。テストがそのまま oracle であり、散文の oracle は書かない。
_Avoid_: 検証の対応付け、Verification Plan (v14 までの散文の oracle)

**封**:
受け入れテストと計画だけを含み、trailer `Define-Done-Seal:` と `Define-Done-Test-Command:` を持つ commit。その後に封をしたファイルを変えれば、`check_seal.py check` が必ず差分として検出する。完了は `check_seal.py verify` が、封が破られておらず、受け入れテストが封の時点で落ち、今の tree で通ることを exit 0 で返したときである。define-done のやり直しは新しい封の commit を積む。古くなった AC を書き直すだけの commit は trailer `Define-Done-Supersedes: <置き換える AC-ID>` で封じる。この commit は改ざんの検査では封に数え、`verify` が流す封には選ばない。
_Avoid_: fingerprint (v14 までの、計画の中に書いた hash)

**保護するパス**:
封の commit に入ったファイルの集合。実装は変えない。
