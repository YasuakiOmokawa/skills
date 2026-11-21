# Changelog

All notable changes to omokawa-skills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v21.0.0 - 2026-11-21

### Changed

- **`define-done` 6.0.0 (破壊的変更: 凍結の commit をやめる):** 受け入れテストを凍結の commit で守る仕組みと、専用の入口 (土台、`harness/`) を通して書かせる規則を削除した。受け入れテストは repo の既存のテスト (手本) と見分けがつかない形で書く。置き場所、ファイル名の形、ランナーとその設定、補助、外の境界の通り方を手本から取り、既存のテストのファイルと補助のファイルに足してよい。commit は作らない。理由は `docs/adr/0002-acceptance-tests-follow-existing-tests.md` に書いた。
- **`check_seal.py` を `check_done.py` に置き換えた:** command は `check`、`report`、`spike-open`、`spike-close` の 4 つ。`seal`、`reseal`、`verify`、改ざんを見る旧い `check` は無い。実装の完了は repo の test command が通ることで判定する。
- **`check_done.py check` が確かめること:** 計画の整合 (これまでの `seal` と同じ)、渡したファイルの置き場所が HEAD にあること、HEAD にあるファイルへの変更が行の追加だけであること (import と require の行は数えない)、足した行に AC-ID が無いこと、今の tree で `[規則]` が落ち `[非影響]` が通ること、試作の実装で全部通ること。種類は計画の印から読み、同じファイルの既存のテストは数えない。
- **`check` の入力:** `rule` と `non_impact` を `files` 1 つにまとめた。`rewrites` (要求が振る舞いを変えるので書き直した既存のテスト)、`new_dirs` (repo の規則か依頼の名指しが求めた新しいディレクトリ)、`implemented` (実装がすでに HEAD にある規則の基準) を足した。3 つとも理由を添え、`report` が最終回答に並べる。
- **ローカルの起動の範囲を広げた:** repo の test command と開発の手順がローカルで起動するものは、アプリのサーバも含めて起動してよい。接続と送信はローカルの中に限る。
- **受け入れテストのファイル名:** repo の機能の語で付け、issue の番号や計画の名前を入れない。

- **無くなった検査:** 凍結したファイルの改ざんの検出、受け入れテストが土台とランナーだけを import する検査、同じ AC-ID で本文の変わった基準を拒む照合 (v20.9.0)、種類ごとのファイル分け。受け入れテストを後から弱めても検出しない。
- **文の規則だけになったもの:** 実装の選択を固定する既存の試験 (内部の message を語彙にする部品のテストなど) を手本にしないことと、外の境界を通る既存のテストが無い AC を未検証で返すことは、機械の検査が無い。eval の case も無い。
- **移行:** 前の版の凍結の commit と `acceptance/` のテストは、普通の commit と普通のテストとして残る。新しい版は凍結を読まない。
- **eval:** `check_done.py` の unit test は 84 件 (旧 141 件から、凍結の command の 71 件を除き、新しい検査の 14 件を足した)。case は 41 (凍結の機構だけを測る 36、37、40 を削除し、48 `follow-existing-tests` と 49 `no-test-location` を足した)。全 41 case を with arm で 3 run ずつ回した。名前の変わらない grader で、旧版から 2 run 以上下がったものは無い (1 run の差は 4 個が下がり 2 個が上がった)。24 の `existing-interface-used` は 1/3 から 3/3 に上がった。名前を変えた grader (`seal-by-script` → `check-by-script`、`seal-commit` → `check-passed` など) と新しい case の grader は、35 の `rewrite-declared` を除いてすべて 3/3 だった。
- **eval (計測器の直し):** 35 の `rewrite-declared` は 1/3 だったが、3 run とも `rewrites` を渡して既存のテストを書き直していた。grader がファイル名の literal を求めていて、shell の変数で渡した 2 run を落としていたので、grader を直して 35 だけ回し直し、`rewrite-declared` と `rule-rewrite-reported` はどちらも 3/3 だった。35 の fixture は、既存のテストが空のカートを試していて要求が変える振る舞いに当たらなかったので、カートにある商品を試す形に直した。47 の `check-green` は trace を読む llm grader が正しい run を落としたので regex に改めた。
- **eval (翻訳の質):** 変異の題材 8 つは旧版と同じ水準だった。23、24、26、27、29 は 3 run とも全テストが有効で、手書きの変種と自動の変異をすべて落とした。25 はテストを書いた run が 2/3 から 3/3 に増え、資料に無い期待を 1 件書いた run が 0 から 2 に増えた (過去 14 回の記録では 0 が 7 回、1 が 4 回、2 が 3 回で、揺れの範囲にある)。30 は全テストが有効な run が 2/3 のままで、無効なテストを持つ 1 run が手書きの変種 8 個中 2 個と自動の変異 48 個中 4 個を逃した。28 は旧版と同じく 3 run とも Gate で止まった。
- **eval (chain):** `chain-invite-owner` は with arm の 3 run とも全テストが有効で (旧版 2/3)、コードは 3 run とも採点用テストを全部通した。`chain-string-quantity` は旧版と同じく 3 run とも D1 を理由に Gate で止まった (`score_results` は最終回答の言い回しの違いで 1 run を Gate の停止に数えない)。
- **eval (新しい補助):** テストを書いた 61 run の trace で、agent が新しい補助のファイルか `harness/` を作った run は 0 だった (Write、Edit、heredoc の書き込み先で数えた)。48 は試走を含む 4 run とも、既存の `test/cart.test.js` か `test/support.js` に足した。
- **eval (測っていないもの):** 手本の無い AC を未検証に回すこと、repo の規則が求める新しいディレクトリ、`implemented`、ファイル名に issue の番号を入れないことは、`outcomes.md` に assertion を足したが grader が無い (`rewrites`・`new_dirs`・`implemented` の根拠は unit test)。Ruby と、サーバを起動する e2e を手本にする repo では回していない。
- **ルーティンから外れた点:** skill の文は、grader と fixture を読んだ本人が書いた (改善ルーティンの 3 番は、編集する agent に `prompt.md` と `graders/` を渡さないと決めている)。

## v20.9.0 - 2026-11-20

### Changed

- **`check_seal.py reseal` (凍結の後に基準を減らせる):** 計画の `## Acceptance Criteria` から消えた基準は、`reseal` がテストの対応を外し、`dropped: AC-NNN` を出す。これまでは前の凍結の対応を必ず引き継ぐので「テストを対応させた AC-NNN が計画に無い」で拒まれ、基準を減らせなかった。taimei-auth の #504 で、利用者が凍結の後に要求を 2 度変え、`check_seal.py` の source を読んで、文書に無い `"resealed": true` を付けた `seal` に全部の対応を渡し直して回避したため。
- **`check_seal.py seal` と `reseal` (拒む計画が増える):** 凍結の commit に、計画の path (`Define-Done-Plan`)、基準ごとの本文の hash (`Define-Done-Criteria`)、要求ごとの文の hash (`Define-Done-Requirements`) を記録する。同じ計画の進行中の凍結がこれを持つとき、次の 3 つを拒む。(1) 同じ AC-ID で本文が変わった基準。(2) 前の凍結の基準と同じ本文で、AC-ID だけが新しい基準。(3) 同じ文で番号だけが変わった要求。hash は、種類の印、`(出典: ...)`、`- [ ]`、空白を除いて取る。計画から消えた基準の hash は次の凍結へ引き継ぐので、一度外した AC-ID を別の基準に使うことも拒む。言い回しだけを直した基準は標準入力の `"reworded": ["AC-NNN"]` に挙げ、`Define-Done-Reworded` として commit に残る (本文が変わっていない AC-ID を挙げると拒む)。hash を持たない凍結 (これまでの凍結) と、別の計画の凍結とは照合しない。#504 で、要求を変えたときに AC-001〜AC-013 と R-1〜R-22 を振り直し、「意味の変わらない基準と要求は番号を保つ」規則を破ったまま 2 回凍結できたため。
- **`check_seal.py seal` と `reseal` (読み込めない規則のテスト):** 規則の基準のテストが変更前の tree で結果を 1 つも出さなかった (skip ではない) ときは、実装のある tree でそのテストが通っていれば、落ちたものと数え、`unloaded: AC-NNN` を出す。実装のある tree は、`spike` を渡せば試作の実装を当てた tree、渡さなければ退避する前の作業ツリーである。その tree の実行に、対応する AC の無いテストか実行されないテストが 1 つでもあれば数えない。非影響の基準のテストは、これまでどおり実行されなければ拒む。これまでは、土台が変更前の tree に無い module を静的に import すると「実行されなかった」で拒まれた。#504 では、受け入れテストだけが使う遅延 import の土台が製品の repo に残った。
- **`check_seal.py seal` と `reseal` (実行が 1 回増える):** `spike` を渡さず、凍結の外に変更がある凍結は、上の確かめのために、退避の前に受け入れテストを 1 回多く流す。
- **`check_seal.py seal`:** Node のテストランナーが読み込めないファイルに付ける、ファイルの path を名前にした結果を、「対応する AC が無いテスト」に数えない。
- **`define-done` 5.9.0:** `acceptance-tests.md` に「要求が変わったとき」を足した。変えた要求は利用者の発言を引用して場所を `依頼` にし、意味の変わらない要求と基準は番号を保ち、変えた要求が正本と食い違うなら正本の更新を未決の判断に書く。土台の遅延 import が要るのは、試作の実装を渡さない最初の凍結だけ、と書いた。

- **残る制限:** 基準がすべて消えた凍結済みのファイルを消すことは、`seal` が「ファイルが無い」で拒むので、まだできない (#504 では起きていない)。
- **残る制限 (読み込めないテストの扱い):** unit test は Node のテストランナーだけで確かめた。bun は、2 つのテストファイルの片方が読み込めないとき、読めたファイルの結果だけを報告に書くことを手で確かめた (bun 1.4.4)。退避の前の実行が凍結の外のファイルを書き換えるテストコマンドでは、凍結の commit を作った後に、戻した変更が退避の前と一致しないと報告する。テストの名前がテストファイルの path か拡張子を除いた名前と同じ結果 (pytest の `tests/test_cart.py` の `test_cart` など) は、「対応する AC が無いテスト」の検査に掛からない。
- **見送ったもの:** #504 の retro で挙げた 5 件のうち、凍結し直した理由を commit に残す、`report` が凍結し直した後も古い試作の patch を出す、`seal` と `reseal` の `--help` が入力の key を出さない、の 3 件は入れていない。
- **retro の提案と違う点:** 基準を減らす手段は、提案の「対応を全部置き換える入力を足す」でなく、計画から消えた基準を `reseal` が自動で外す形にした。計画が基準の集合を既に持つので入力が要らず、渡し忘れが起きないためである。
- **eval:** `check_seal.py` の unit test は 20 件を足して 141 件 (うち 15 件は旧 script で落ち、5 件は誤って拒まないことの番)。case 47 (`47-requirement-changed-after-seal`、凍結の後に要求を 2 つ変えて凍結し直す) を足した。全 42 case を with arm で 3 run ずつ回し、chain 2 case も回した (全 suite $98.5、chain $4.9、case 47 の fixture を直す前後の試し流しで $9)。5.8.0 から通過率は 0.972 → 0.978。2 run 以上下がった grader は 24 `existing-interface-used` (3/3 → 1/3) だけで、落ちた 2 run を判定し直すと 3 票とも PASS だった (trace でも、受け入れテストは土台を通して既存の `createCart`・`add`・`total` で観測している)。1 run 下がったのは 08 `requirements-listed` と 18 `not-run-recorded` (どちらも 3/3 → 2/3、判定し直していない)。上がったのは 08 `permission-branch` 0/3 → 2/3 と、01 `stage-scope-declared`、05 `purpose-covered`、17 `convention-out-of-scope`、35 `supersedes-recorded` の 2/3 → 3/3。chain は invite-owner が 3/3 (コードも隠しテストを全部通す)、string-quantity は前の版と同じく 3 run とも Gate で停止。受け入れテストの変異の採点は、25 の「全テストが有効な run」が 1/3 → 2/3 になったほかは前の版と同じ値。
- **eval (版を区別しないもの):** case 47 は、旧版も新版も 8 つの grader がすべて 3/3 だった。違いは経路で、旧版は 3 run とも `reseal` を使わず全部の対応を渡し直す `seal` で凍結し、新版は 3 run とも `reseal` が 1 回で通った。旧版の agent も AC-ID を振り直さなかったので、ID の照合が拒む場面は eval では起きていない (根拠は unit test)。この case は、hash を持つ凍結を凍結し直す経路の回帰の番として残す。
- **eval (fixture の直し):** case 47 の最初の fixture は、計画の 4 節の外 (変更対象の表) が古い要求のままで、旧版も新版も 6 run すべてが規則どおり Gate を止めた。4 節の外は利用者が直してある設定に改めた。
- **eval (測っていないもの):** 読み込めない規則のテストの扱いと、試作を渡さない凍結での土台の遅延 import は、`outcomes.md` に assertion を足したが grader が無い (根拠は unit test)。

## v20.8.0 - 2026-11-19

### Changed

- **`check_seal.py reseal` (不具合の修正):** 1 つの AC に同じファイルの複数のテストを対応させた凍結を、凍結し直せる。これまでは対応を AC とファイルの組で引いていたので 2 本目のテストが落ち、「対応する AC が無いテスト」で拒まれた (標準入力の `tests` に全部を渡しても同じだった)。標準入力の `tests` に渡した AC とファイルの組は、その組のテストが渡したものに置き換わる (テスト名を変えたら、その組のテストをすべて渡す)。taimei-auth の #500 で、`seal` を流し直して回避したため。
- **`check_seal.py seal` と `reseal` (不具合の修正):** 凍結の外の変更の退避が、stage した改名と削除で壊れない。これまでは `git stash push -- <path>` が、index からも作業ツリーからも消えた path で exit 128 になり、stash が 1 つ残って、復旧の案内も出なかった。stage した削除は退避の前に index へ戻し、復元の後に stage し直す。index からだけ消して file を残した変更 (`git rm --cached`) でも、HEAD の製品コードで流す。退避が失敗して stash だけが残り、作業ツリーが変わっていなければ、その stash を消す。
- **`check_seal.py seal` (拒む計画が増える):** `## Requirements` の行のうち、要求の文 (引用の前) が検査コマンドの通過だけを述べる行 (`` `<コマンド>` が通る``) と、今回は作らないものを述べる行 (「まだ作らない」「今回は作らない」など) を拒む。`reseal` でも照合する。`requirements.md` はこの 2 つを要求にしないと定めているが、taimei-auth の #487、#488、#489、#499、#500 の計画で 9 行が要求になっていた。
- **`check_seal.py seal`:** 標準入力の `plan` に渡した計画の path を、repo の git dir の `define-done-plans` に記録する。`reseal` と `report` は、計画が repo の外にあっても path 無しで読む (5.7.0 の PR が次の版で直すとした点)。記録した計画が消えていれば、これまでどおり path を求める。
- **`check_seal.py spike-open`:** git が無視する `.env*` が repo にあれば、複製に無いことと、runner の flag で repo の file を指すことを 1 行出す。#500 では文書の同じ指示を読み落とし、複製の中の 1 回目のテストが DB に接続できずに全部落ちた。
- **`check_seal.py seal`:** テストが実行されず、凍結の外の変更を退避していたときは、凍結するファイルが凍結に含めない変更に頼っていないかを確かめる 1 行を足す。
- **`check_seal.py check` と `verify`:** `seals:` の行は進行中の凍結だけを並べ、完了済みは件数にする (taimei-auth では 53 個の SHA が毎回出ていた)。
- **`define-done` 5.8.0:** 最終回答の未検証は、同じ事柄を指す行を 1 行にまとめ、凍結の後の作業で確かめたものには確かめた方法と結果を添える。#500 では、1 つの未検証が `report` の出力に 3 行で出た。凍結の後の `/security-audit` が確かめた後も `report` は未検証のまま出すので、最後の報告で手で言い直した。

- **見送ったもの:** 試作が覆した決定のうち検査が理由でないものに、Gate を止めない行き先を足す案は入れていない。#500 の 2 件に当てはめると、1 件 (challenge を消す順) は外から観測できる振る舞いが変わるので「検査が拒んだ決定」の条件 (3) を満たさず、計画を直して `spike-open` からやり直す今の規則が正しい行き先だった。もう 1 件 (試行枠の数え方) は、`## Ground Review` の前提の確認で依存先の値を実行環境で観測していれば見つかった。
- **eval:** `check_seal.py` の unit test は 16 件を足して 121 件 (うち 13 件は旧 script で落ち、3 件は誤って拒まないことの番)。全 41 case を with arm で 3 run ずつ回し、chain 2 case も回した (全 suite $91、chain $5、case 01 と 08 の同じ日の流し直しで $17、下の試し流しで $5)。5.7.0 から通過率は 0.979 → 0.972。2 run 以上下がった grader は 01 `envvar-covered` (3/3 → 1/3) だけで、同じ日に流し直すと旧版 1/6、新版 4/6 だった (この grader は 5.6.0 から 1/3 → 3/3 → 1/3 と揺れていて、版の差とは言えない)。1 run 下がった grader のうち、01 `stage-scope-declared`、14 `retry-unverified`、27 `bug-caught` は判定し直すと PASS、40 `impl-not-sealed` は grader の誤検知 (凍結の commit に実装は入っていない。同じ呼び出しの `git diff --stat` の出力に regex が当たった)、05 `purpose-covered`、17 `convention-out-of-scope`、35 `supersedes-recorded` は FAIL のまま。08 `permission-branch` は 1/3 → 0/3 で、同じ日の流し直しは旧版も新版も 1/3。04、15、24、29 と 27 の凍結まわり 3 つは 2/3 → 3/3 に上がった。chain は invite-owner が 3/3 (コードも隠しテストを全部通す)、string-quantity は旧版と同じく 3 run とも Gate で停止。受け入れテストの変異の採点は前の版と同じ値 (25 の「全テストが有効な run」は 1/3 のまま)。
- **eval (再現しなかったもの):** 検査コマンドの通過と作らないものが要求になる取りこぼしは、この形の要求を持つ前の計画を隣に置き、計画が「形はそれに合わせる」と名指しする fixture でも、旧版 3/3、新版 3/3 で再現しなかった (前の計画の本文は fixture の作成で 6 run とも文脈にあり、うち 2 run は file を開き直した)。旧版と新版を区別できないので、この case は suite に足していない。`seal` の検査の根拠は unit test と、過去の計画と eval の要求 3,629 行への照合 (当たるのは上の 9 行だけ) である。
- **eval (測っていないもの):** 最終回答の未検証の扱い (同じ事柄を 1 行に、確かめた方法を添える) は、`outcomes.md` に assertion を足したが grader が無い。case 01 の新版の流し直しで `residual-risk-destination` が 6 run 中 2 run 落ちた (全 suite は 3/3、同じ日の旧版は 6/6)。今回変えた文は残ったリスクの表に触れていないので版の差とは見ていないが、切り分けはしていない。

## v20.7.0 - 2026-11-19

### Changed

- **`define-done` 5.7.0 (最終回答の置き場所が変わる):** 依頼が凍結の後の作業 (実装など) まで求めているときは、最終回答をその作業を終えた最後の報告の先頭に置く。凍結の直後に返してから実装へ移る、という 5.5.0 の規定は外した (eval で 2/3 のまま上げられず、taimei-auth の #499 でも凍結の直後は 1 行だけで実装へ進んだ)。凍結で終わる依頼は、これまでどおり凍結の後に最終回答を返す。最終回答は `check_seal.py report` の出力を写して書く。
- **`check_seal.py report`:** `## Ground Review` の `### 未決の判断` と `### 未検証の結論` の行、`## MECE Review` の `- 未検証` で始まる箇条を抜き出す (「無い」「なし」の行は出さない)。凍結し直した後も、進行中の凍結が記録した全ファイルを出す (これまでは直近の凍結の commit のファイルだけだった)。試作の patch の path を出す。
- **`check_seal.py seal`:** `spike` を渡して凍結したとき、patch の path を repo の git dir の `define-done-spike-patches` に記録する (`report` が読む)。commit の trailer には書かない (手元の一時 dir の path が push される履歴に残るため)。patch が消えていれば `report` は path を出さない。
- **`check_seal.py seal` (拒む計画が増える):** `## MECE Review` の残ったリスクの表 (`### 残ったリスク` を含む見出しの下) の守る先が、`AC-NNN`、`実装のテスト:`、`既存のテスト:`、`規約`、`未検証:` のどれでも始まらない行と、計画に無い AC-ID を守る先にした行を拒む。`reseal` でも照合する。
- **`check_seal.py verify`:** 通ったとき、最後の報告の先頭に `report` の最終回答を置くよう促す 1 行を出す。
- **`check_seal.py check <repo> <ファイル>...`:** ファイルを渡したときは保護の状態だけを出し、exit 0 を返す。これまでは、凍結の前に流すと「進行中の凍結の commit が HEAD から辿れない」で exit 1 になった。
- **`define-done` 5.7.0:** 引用元の複数の文が同じ結果を述べるとき (issue の「やること」と「受け入れ条件」など) は 1 件の要求にし、それぞれの原文を引用に並べる。片方の文が細目を足していれば、要求はその細目まで述べる。taimei-auth の #499 で、同じ結果が別々の要求になって 18 件に膨らみ、最終回答が 7 件を 1 行に畳んで引用を落としたため。
- **`define-done` 5.7.0:** 残ったリスクの守る先に `既存のテスト: <ファイル>` (変更の前からあるテストがそのリスクで落ちるもの) を足した。`## Ground Review` の未決の判断と未検証の結論は、`### 未決の判断` と `### 未検証の結論` の見出しの下に 1 件 1 行で書く。

- **eval:** case 43 を、凍結の後の実装まで求める依頼で「最後の報告が要求を引用付きで省かず並べる」ことを測る形に書き直し (`43-report-after-continuing`)、case 45 (正本の issue が「やること」と「受け入れ条件」の 2 節で同じ結果を述べ、受け入れ条件に検査コマンドの通過が並ぶ) を足した。`check_seal.py` の unit test は 9 件を足して 105 件。全 41 case を with arm で 3 run ずつ回し、chain 2 case も回した (全 suite $91、chain $5、旧版での基準取りと試し流しで $13、認証の失敗で流し直した 2 case で $5、下の case 25 の切り分けで $24)。旧版 → 新版で、43 の 2 つの grader は 2/3 → 3/3 (試し流しを足すと、出す版は 9/9、`verify` の 1 行が無い版は 6/6。5.6.0 の全 suite の run に同じ grader を当てると 0/3)、45 `paraphrased-outcome-listed-once` は 0/3 → 3/3 (旧版は、旧版の run が書いた計画に同じ regex を当てた値)。45 のほかの 5 つの grader は旧版でも 3/3 で、検査コマンドの通過と作らないものが要求になる #499 の取りこぼしは、この形の fixture では再現しなかった (文言は変えていない)。5.6.0 から 2 run 以上下がった grader は無い。Gate を止める case (08、14、22、28) の grader は、08 `permission-branch` (2/3 → 1/3。判定し直すと 3 票とも PASS) を除いて旧版と同じ。1 run 下がった 04 `unresolved-reported` は判定し直すと PASS、15 `new-criterion-semantics` と 29 `untested-ac-listed` は判定し直しても FAIL、27 の凍結まわりの 3 つは 1 run が計画のバグを見つけて Gate で止まった (前からの揺れ)。上がったのは 01 `envvar-covered` 1/3 → 3/3、14 `retry-unverified` 2/3 → 3/3、18 `not-run-recorded` 2/3 → 3/3。残ったリスクの守る先の照合が凍結を拒んだ run は無く、凍結まで進んだ 63 run のうち 18 run が `既存のテスト:` の行を書いた。chain は `chain-invite-owner` が 3/3 (コードも隠しテストを全部通す)、`chain-string-quantity` は前の版と同じく 3 run とも Gate で止まった。
- **eval (受け入れテストの変異の採点):** 25 `real-bug-admin-mints-owner` の「全テストが有効な run」が 3/3 → 1/3 に下がった (要件適合度とバグ検出率は満点のまま)。無効なテストはどれも「ADMIN の招待を既存の OWNER が受諾しても OWNER のまま」で、資料が決めていない振る舞いを基準にしている。同じ日の旧版でも同じ率で出るので、版の差とは言えない。同じ日に旧版 (5.6.0) を 9 run 流すと、テストを書いた 7 run のうち 2 run が同じテストを書いた (5.0.0 からの 5 回の記録では、テストを書いた 14 run 中 0)。新版は 9 run 流してテストを書いた 8 run のうち 3 run、要求の抜き出しの文を外した版は 4 run 中 1 run、残ったリスクの文を外した版は 5 run 中 2 run だった。前の日までの記録との差が何から来たかは分かっていない (CLI の版と model の ID は同じ)。ほかの題材 (23、24、26、29、30) は前の版と同じ値。
- **eval (測っていないもの):** `verify` が出す 1 行は、有る版も無い版も case 43 が 6/6 で、効果を測れていない (会話が要約された後に最終回答を書けるかは、eval で再現していない)。case 43 の要求は 2 件で、#499 で起きた形 (18 件の要求を最後の報告が畳み、引用を落とす) も再現していない。chain の採点の `--record` は、記録先の `evals/mutant-record.json` が repo の root に無く失敗するので、chain の値は記録していない (前の版も同じ)。

## v20.6.0 - 2026-11-18

### Changed

- **`define-done` 5.6.0 (Gate の規則が変わる):** 計画の決定が選んだ形 (名前、export、置き場所、書き方) を repo の検査 (lint、型検査、dead code の検査) が拒んでも、次の 3 つがすべて成り立てば Gate を止めず、`## MECE Review` の `### 検査が拒んだ決定` の表に書いて凍結まで進む。(1) その形で書いたコードに検査を流して拒まれるのを見た。(2) その形をやめてもすべての要求を満たせる。(3) やめた形で、基準も外から観測できるものも変わらない。1 つでも成り立たなければ、これまでどおり必要な上流の修正に書いて Gate を止める。計画の 4 節の外は直さず、決定を直すのは呼び出し側である。これまでは、どの段で気づいても必要な上流の修正として Gate を止めていた (新しい case 44 で、旧版は 3 run とも `## Ground Review` で気づいて止まる)。
- **`check_seal.py spike-open` / `seal`:** `spike-open` に計画の path を渡すと、その時点の計画の 4 節の外の hash を patch の先頭行 (`Define-Done-Plan-Outside:`) に記録する。`seal` は、凍結する計画の 4 節の外がその hash と食い違えば凍結しない (`reseal` では比べない)。見るのは `spike-open` より後の書き換えだけで、それより前の書き換えは見ない。先頭行があっても patch は `git apply` でそのまま当たる。
- **`check_seal.py report`:** 進行中の凍結と計画から、最終回答の材料 (引用付きの要求の行、Gate、種類別の AC 数、凍結の SHA、基準の無い要求、実装が足すテスト、未検証、検査が拒んだ決定) を抜き出す subcommand を足した。repo の外の計画は path を続けて渡す。
- **`check_seal.py check`:** file の path を続けて渡すと、file ごとに保護の状態 (`permanent`、`in-progress`、`released`、`unsealed`) を出す。旧い形式の凍結で保護が解けているかを、script の source を読まずに確かめられる。
- **`define-done` 5.6.0:** 残ったリスクの表の `実装のテスト` は、守る実装を外すと結果が変わる入力と、その結果で書く (基準が条件を場合分けしているなら、どの場合かを名指しする)。
- **`define-done` 5.6.0:** `references/acceptance-tests.md` の「凍結」の 1 段落を、`seal` に渡す JSON、`seal` が確かめること、凍結した後に使う command、番号付きの凍結の手順に割った。最終回答で凍結の SHA と patch の path を返す 2 句は、同じことを定める SKILL.md の最終回答の規定に任せて外した。ほかの文は移しただけである。

- **eval:** case 44 (repo の lint が計画の決定どおりの形を拒むが、その形をやめても要求を満たせる) を足した。`check_seal.py` の unit test は 10 件を足して 96 件。全 40 case を with arm で 3 run ずつ回し、chain 2 case も回した (全 suite $89、chain $4、旧版での case 44 の基準取り、Gate まわりの 7 case の試し流し、case 43 の比較で $29)。case 44 は旧版 → 新版で `sealed` 0/3 → 3/3 (旧版は 3 run とも `## Ground Review` で衝突に気づいて Gate を止める)、`plan-body-kept` と `overturned-decision-reported` はどちらの版も 3/3。Gate を止める case (08、14、22、28) の grader は旧版と同じ。5.5.0 から 2 run 以上下がった grader は無い。1 run 下がった 18 `not-run-recorded` と 24 `existing-interface-used` は判定し直すと 3 票とも PASS、01 `envvar-covered` は 2/3 → 1/3 (判定し直しても FAIL)。上がったのは 05 `purpose-covered` 0/3 → 3/3 (前からの揺れ)、08 `permission-branch` 1/3 → 2/3、15 `new-criterion-semantics` 2/3 → 3/3、37 `superseded-ac-recorded` 2/3 → 3/3。受け入れテストの変異の採点は前の版と同じ水準。chain は `chain-invite-owner` が 3/3 (コードも隠しテストを全部通す)、`chain-string-quantity` は前の版と同じく 3 run とも Gate で止まった。
- **eval (届かなかった改善):** 43 `report-before-implementing` (凍結の後、実装へ進む前に要求の一覧を返す) は 2/3 のままで、上げられなかった。`seal` が最終回答の中身を出力に出す版は 0/3 (agent は報告済みと受け取って実装へ進む)、`seal` と `check` が「実装の前に最終回答を文章で返す」の 1 行だけを出す版は 2/6、凍結の手順を文書の末尾に置いて完了の条件を書き足した版は 3/6 で、どれも旧版 (2 回測って 4/6) を上回らなかった。`seal` と `check` の出力は変えず、材料を抜き出す `report` だけを残した。「実装が足すテストを、守る実装を外すと結果が変わる入力で書く」は測る題材が無く、`outcomes.md` で未計測とした。

## v20.5.0 - 2026-11-18

### Changed

- **`check_seal.py seal`:** 凍結の前に計画を読み、整合を確かめる。確かめるのは、Gate が ready であること、`- AC IDs:` の行が基準の AC-ID と一致すること、テストを対応させた AC が計画にあり種類の印がファイルの種類と合うこと、基準の出典の `R-n` が要求にあること、要求の表の各行がその要求を出典に挙げる AC-ID か `未検証:`・`範囲外:`・`不足情報:` で始まること。食い違えば exit 1 で凍結しない。計画は凍結するファイルの中から探し、repo の外の計画は JSON の `plan` で渡す。
- **`check_seal.py seal`:** commit の subject を計画の path から作る (`test: plans/tags.md の受け入れテスト`、repo の外の計画は末尾の 2 要素)。`reseal` は末尾に「を直す」を付ける。JSON の `subject` は省ける。計画のファイル名だけを使う雛形では、`<issue の dir>/design.md` に置いた計画の凍結の commit がどれも同じ subject になっていた。
- **`check_seal.py seal`:** 渡したファイルのほかの凍結済みのファイルに未 commit の変更があれば、テストを流す前に拒む。これまでは凍結に成功し、その後の `check` で初めて改ざんと分かった。
- **`check_seal.py spike-open` / `spike-close`:** 試作の実装を書く一時的な複製を作る subcommand を足した。`spike-open` は HEAD の worktree を repo の外に作り、gitignore された依存の dir (`node_modules`、`.venv`、`vendor/bundle`) を link し、渡した受け入れテストと土台を写す。`spike-close` は試作の実装の差分だけを repo の外の patch に出して複製を消す。写したファイルが複製の中でだけ変わっていれば拒む。env の file は link も複写もしない。
- **`define-done` 5.5.0:** 要求にするのは、完了したときに製品か文書に成り立つ結果だけにした。作業の進め方の指示は従うだけにし、repo の検査コマンドが通ることは `check_command` に渡し、依頼が今回は作らないと述べたものは計画の範囲外の宣言と突き合わせる。資料が値を決めていない要求は、要求の表に `不足情報:` と書く。
- **`define-done` 5.5.0:** `## MECE Review` に残ったリスクの表を足した。`## Ground Review` が反証できずに残したリスクごとに、守る先 (AC、実装のテスト、規約、未検証) を書く。`実装のテスト` の行は、最終回答に実装が足すテストとして並べる。
- **`define-done` 5.5.0:** 最終回答を、依頼の後続の作業 (実装など) へ移る前に出す (完了条件にも入れた)。AC ごとのテスト名と要求ごとの対応は、凍結の commit と計画にあるので回答から外し、種類別の AC 数、試作の実装の patch の path (実装はこの patch を当てて始めてよい)、実装が足すテスト、enforce-conventions に渡す規約を返す。
- 上の 7 点は taimei-auth の #489 の振り返りから来ている。残ったリスク 1 件にテストが付かないまま実装が終わり、「すべて推奨で決める」が要求になって対応する AC の無い行が Gate を通り、凍結の直後の回答を飛ばして実装へ進み、試作の worktree の準備に往復がかかった。
- **eval:** case 42 (作業の進め方の指示、作らないものの宣言、検査コマンドの通過を要求にしない) と 43 (凍結の後、実装へ進む前に要求の一覧を返す) を足し、case 01 に残ったリスクの守る先、case 41 に `spike-open` の利用と patch の path の返却の grader を足した。`check_seal.py` の unit test は 16 件を足して 86 件。全 39 case を with arm で 3 run ずつ回し、chain 2 case も回した ($98。旧版での新しい case の基準取り、pilot、流し直しを含む)。新しい grader は、旧版 → 新版で、01 `residual-risk-destination` 0/3 → 3/3、41 `spike-by-script` 0/3 → 3/3、41 `patch-path-returned` 1/3 → 3/3、42 `no-check-command-requirement` 0/3 → 3/3、42 `no-non-goal-requirement` 2/3 → 3/3、43 `report-before-implementing` 0/3 → 2/3 (完了条件に入れる前の中身でも 2/3。最終の中身で落ちた 1 run は、回答を先に出すと述べたうえで、実装の道具の呼び出しが回答より先に出た)。旧版の値は、01 が 5.3.0 の run の計画を同じ基準で判定し直したもの、41 が 5.3.0 の trace に同じ regex を当てたもの、42 と 43 が 5.4.0 で回したもの。42 `no-process-requirement` は旧版でも 3/3 で、この fixture では差が出ない。5.3.0 から 2 run 以上下がった grader は 05 `purpose-covered` (2/3 → 0/3) だけで、同じ中身で流し直すと 3/3 だった (5.2.0 では 1/3。計画の「仕様」の節から要求を引くかで合否が割れる、前からの揺れ)。1 run 下がった 14 `retry-unverified` と 15 `new-criterion-semantics` は、判定し直すとどちらも PASS だった。14 `billing-decided` は最終回答を見る grader で、1/3 → 0/3 に下がった。請求作成の対応の判定は計画に書いてあり、新しい最終回答は要求ごとの対応を写さないので、grader の見る先を計画に替えて case 14 を流し直した。替えた grader は、旧版の run の計画でも新版でも 3/3。受け入れテストの変異の採点は前の版と同じ水準で、30 の 1 run はテストを書いて凍結したが、trace から復元できず採点できなかった。chain は `chain-invite-owner` が 3/3 (コードも隠しテストを全部通す)、`chain-string-quantity` は 3 run とも計画の D1 のバグを理由に Gate で止まった。

## v20.4.0 - 2026-11-17

### Changed

- **`define-done` 5.4.0:** 受け入れテストと計画を固定する commit の呼び名を「封」から「凍結」に変えた (凍結の commit、凍結の時点、凍結し直す)。「封」は日本語の開発の語として通じにくく、「仕様凍結」の「凍結」なら説明なしで通じるため。`seal`、`reseal`、`Define-Done-Seal:` の trailer、`check_seal.py` の名前は変えないので、既にある凍結の commit はそのまま読める。`check_seal.py` のエラーメッセージ、GLOSSARY、eval の prompt と grader も同じ語に揃えた。
- **`enforce-conventions` 3.2.0:** 保護するパスの説明の「封の commit」を「凍結の commit」に揃えた。
- **eval:** 語が変わった prompt と grader を持つ define-done の 10 case、chain 2 case、enforce-conventions の case 05 を with arm 3 run で回した ($36、main での比較 run を含む)。5.3.0 から 2 run 以上下がった grader は 27 の凍結まわり (3/3→1/3) と chain-string-quantity の `acceptance-test-written` (2/3→0/3) で、落ちた run はどれも計画の D1 のバグを見つけて Gate で止まっていた。main でも回すと 27 は 2/3、chain-string-quantity は 0/3 で、今回の変更による低下ではない。全 suite は回さず、`last-run.json` は理由付きで waive した。

## v20.3.0 - 2026-11-17

### Changed

- **`check_seal.py seal`:** 渡したファイルの外の変更 (実装の途中の変更と追跡していないファイル) を自分で退避して HEAD の製品コードで流し、終わったら戻す。戻した tree が退避の前と一致しなければ、退避を stash に残して戻すコマンドを出す。既存の stash には触れない。規則の基準は、未 commit の製品コードの変更ではなく HEAD の製品コードで落ちることを見る。
- **`check_seal.py seal`:** JSON に任意の `spike` (repo の外の、試作の実装の patch) と `check_command` を足した。`spike` を当てた tree で `[規則]` と `[非影響]` のテストと `check_command` が通ることを確かめ、外してから封をする (`AC-001: rule spike=pass now=fail`)。名前が一致しないテストには、そのファイルで流れたテスト名を出す。
- **`check_seal.py reseal`:** 直前の封の trailer から JSON を組み立て、標準入力の JSON (`subject`、足す `tests`、`spike`、`check_command`) で上書きして封をし直す。
- **`define-done` 5.3.0:** 前提の確認で、決定が頼る値は受け入れテストを流す実行環境で依存先を呼んで観測し、型定義と doc comment を根拠にしない。実行環境で変わる分岐は、CI と本番がどちらに当たるかを挙げる。土台が実行環境の機能に頼るときは CI の実行環境の版でも使えることを確かめる。封の前に試作の実装を一時的な worktree で書き、`spike` と `check_command` を `seal` に渡す。taimei-auth の #486 で、library の既定が実行環境で変わることを doc comment から見落とし、土台が型の上だけの値を読み、lint の違反と CI の Bun の版の違いが封の後に見つかって、封を 4 回作り直したため。
- **eval:** case 39 (実行環境で変わる依存先の既定)、40 (作業ツリーに実装の途中の変更がある状態での封の作り直し)、41 (封の前に試作の実装と repo の check を通す) を足した。封の grader は `reseal` も受け入れる。全 37 case を with arm で 3 run ずつ回した (新しい 3 case は with-without、$79。旧版での新しい case の基準取りは別に $12)。新しい case はすべて 3/3 (5.2.0 では 41 の `green-before-seal` が 0/3、39 と 40 は 3/3)。5.2.0 から 2 run 以上下がった grader は無い。1 run 下がった 4 grader のうち 17 `convention-out-of-scope` と 24 `existing-interface-used` は判定し直すと 3/3、01 `envvar-covered` と 37 `superseded-ac-recorded` は今回の変更が触れない段の 1 run の差。

## v20.2.0 - 2026-11-17

### Changed

- **`check_seal.py seal`:** 渡したファイルのうち HEAD から変わったものだけを封の `Define-Done-Files` に記録し、commit する。封の後に土台だけを直して流し直すと、変わっていないファイルまで記録して commit の変更と一致せず、`check` が改ざんと報告していた。どのファイルも変わっていなければ拒む。
- **`define-done` 5.2.0:** 封の前に repo の test command 全体を 1 回流し、新しく落ちたテストが規則の基準のテストだけであることを確かめる。土台が受け入れテストの外と共有する状態 (プロセスの中の store、試行の計数、一時ファイル) は各テストの後に戻す。封の後に受け入れテスト・土台・計画を直したら、実装の変更を退避して同じ JSON で `seal` を流し直す。置き換える基準が既定の branch から辿れる旧い形式の封にあれば、そのテストを封に含めず、AC-ID を `## MECE Review` に書く。taimei-auth の #484/#485 で、土台が IP の試行の計数を残して既存のテストを落とし、直した封が改ざんと判定され、旧い形式の封の行を書き換える手順が無かったため。
- **eval:** case 36 (封の後に土台を直す)、37 (旧い形式の封の基準を置き換える)、38 (1 プロセスで流す test command と共有する計数) を足した。全 31 case と足した 3 case を with arm で 3 run ずつ回した (case 34 の再実行を含め $74)。新しい case はすべて 3/3。5.1.0 から 2 run 以上下がった grader は 08 `requirements-listed` (3/3 → 1/3、判定し直すと 3/3) と 34 の封の 3 grader (3/3 → 1/3) だけ。34 は新旧を同じ条件で 3 run ずつ流し直すと 5.1.0 も 5.2.0 も 2/3 で、落ちた run はどちらも、要件が適用の入口を名指ししないので Gate を not ready にしていた (今回の変更が触れない 2 段目の判断)。

## v20.1.0 - 2026-11-16

### Changed

- **`define-done` 5.1.0:** 受け入れテストのテスト名は観測する振る舞いを業務の言葉で書き、テストと土台のコードに AC-ID を書かない。AC とテストの対応は `seal` に渡す JSON の `tests` に書き、封の trailer `Define-Done-Test: AC-001 = <ファイル> › <テスト名>` に記録する。`seal` は、テストの無い AC、AC の無いテスト、実行されなかったテスト、コードの中の AC-ID を拒む。結果はファイルとテスト名で照合するので、封の外のテストの結果を混ぜない (bun・node・vitest・Playwright の JUnit と RSpec の JSON で確かめた)。
- **`define-done` 5.1.0:** repo が開発用に示すローカルの DB とコンテナを起動してよく、テスト用の DB へ migration を流してよい。自分が起動したものは最後に止め、ローカルの外への接続と送信、アプリのサーバの起動はしない。`{report}` は repo の root からの相対の path に置き換わり、コマンドは repo の root で流れるので、コンテナの中で流すランナー (sign の `dip rspec` など) でも結果を読める。
- **`check_seal.py verify`:** 新しい形式の封は、`seal` が封を作るときに測った結果を信じ、今の tree だけを流す。封の時点の tree を `/tmp` に展開して流すと、repo をマウントするコンテナのランナーでは今の tree を流してしまい、規則の基準を「封の時点で通った」と誤判定していた。旧い形式の封は封の時点の tree を流し直す。
- **eval:** case 18 を `18-db-start-or-unverified` に改め、「DB を起動しない」をやめて、repo が示す手順で起動を試み、起動できなければ未検証に並べることを見る。case 34 (前の封の受け入れテストがあり土台が無い repo) と case 35 (要求が恒久の規則の基準を変える) を足した。何も測っていなかった 28 の 2 grader (Gate で止まるのが正解の case の後段) と、skill に根拠の無い 29 の「Write か Edit で書く」を外した。採点は AC-ID ではなく、土台の外の `*.test.js` を受け入れテストとして流す。全 30 case と足した 3 case を with arm で 3 run ずつ、chain eval 2 case を回した ($64)。新しい case はすべて 3/3、テストを書いた case は 30 の 1 run (無効なテスト 3 本) を除き要件適合度・バグ検出率とも満点。5.0.0 から 2 run 以上下がった grader は 01 `stage-scope-declared` (3/3 → 1/3、旧版の通算 13/18 で今回の変更が触れない段) だけ。

## v20.0.0 - 2026-11-16

### Changed

- **`define-done` 5.0.0 (BREAKING):** AC を外から観測できる振る舞いだけにし、計画が新しく作る **規則の基準** (`[規則]`、変更前は成り立たない) と、壊してはならない今の振る舞いの **非影響の基準** (`[非影響]`、変更前から成り立つ) に分けた。`[振る舞い]` と `[禁止]` は廃止し、コードにあってはならないもの・設定・依存・bundle の上限などの規約は、範囲外として enforce-conventions に回す。封は、規則の基準を恒久に、非影響の基準を計画の完了 (封が `origin` の既定の branch から辿れる) まで守る。taimei-auth で封を書き直した 14 本のうち、業務の要求が変わったのは 1〜2 本で、残りは AC やテストが実装・規約・移行の途中の状態を固定していたためだった。
- **`check_seal.py`:** `seal` を足した。標準入力の JSON で受け入れテストのコマンドと種類ごとのファイルを受け取り、今の tree で流して、規則が落ち非影響が通るときだけ、ファイルと種類を trailer に記録した封の commit を作る。実行されなかったテスト、受け入れテストからの `harness/` (土台) とテストランナーの外の import も拒む。結果は JUnit XML と RSpec の JSON を読む。`verify` は AC ごとに、規則は封の時点で落ちて今通るか、非影響は両方で通るかを判定する。封の commit に入れたファイルはすべて保護し (golden を含む)、記録したファイルの一覧と commit の変更が一致しないもの (squash merge など) は封に数えない。要求が恒久の規則を変えるときは、`supersedes` を付けた封だけが書き直せる。旧い形式の封はこれまでどおり判定する。
- **受け入れテスト:** 種類ごとに別のファイルに書き、外の境界には土台だけを通して触れる。土台が無ければ define-done が要る分だけ作る。画面は実ブラウザでビルドした画面を開き、通信の契約・認証ライブラリの公開 API・ブラウザの API だけを差し替える。DB やサーバの起動が要るテストは書かずに未検証として返す (起動済みのものは使ってよい)。
- **GLOSSARY / ADR:** 「受け入れ基準」「封」「保護するパス」を改め、「規則の基準」「非影響の基準」「計画の完了」「土台」を足した。理由は `docs/adr/0001-seal-protects-by-criterion-kind.md`。
- **eval:** case 06 (不在を探すコマンドの dry-run) を削除し、case 17 を規約を範囲外に返す case (`17-convention-not-ac`) に作り替えた。受け入れテストの置き場所は dir で指定し、`mutant.json` は `"tests"` に dir を書く。採点は dir の下に書かれた受け入れテストと土台をすべて復元する。30 case を with arm で 3 run ずつ回した ($56)。受け入れテストを書いた 7 case は全 run で要件適合度・バグ検出率とも満点で、全 run が `check_seal.py seal` で封を作った。旧版から 2 run 以上下がった grader は 29 の「受け入れテストを Write か Edit で書く」(11/12 → 0/3) だけで、新版は受け入れテストと土台を 1 回の heredoc でまとめて書く。skill の本文に根拠の無い癖の grader で、採点は heredoc から復元できるので、受け入れた損失とした。

## v19.1.0 - 2026-11-14

### Fixed

- **`define-done` 4.4.0:** `check_seal.py` は、trailer `Define-Done-Seal:` か `Define-Done-Supersedes:` を持っていても、受け入れテストと計画 (`.md`) のほかのファイルを変えた commit を封に数えない。封を含む branch を squash merge すると、squash の commit の本文が封の trailer で終わり、PR の全ファイルが保護するパスになって、次の PR がそれらを変えると改ざんと判定されていた。受け入れテストは path で見分ける (`test`・`tests`・`__tests__`・`spec`・`specs`・`e2e` の dir の下、`test_` で始まる名前、`.test.`・`_test.`・`-test.`・`.spec.` などを含む名前)。
- **`enforce-conventions` 3.1.0:** 保護するパスを、GLOSSARY の「封」の commit (受け入れテストと計画だけを変えたもの) のファイルに揃えた。
- **GLOSSARY:** 「封」に、他のファイルを変えた trailer 付きの commit は封に数えないことを足した。

## v19.0.0 - 2026-11-11

### Changed

- **`enforce-conventions` 3.0.0 (BREAKING):** どこにも述べられていなくても、作業ツリーの全箇所が満たし、利用する側が当てにしている約束を「観測した規約」として、破るコードを書けないか型検査で落ちる形にする。満たす箇所は 1 箇所でもよい。2.0.0 の出典「2 箇所以上が同じ形で守っている」と、禁止の「規約を作らない、変えない、広げない」は外した。満たさない箇所が 1 つでもある約束、外から来る値の型、利用する側が当てにしていない約束、既定の枝が 2 個以上の値をまとめて受ける分岐は、変えずに報告する (2.0.0 は 2 対 1 の多数を規約と読んで型を絞っていた)。決めるのは結果だけで、手段は名指さず、repo に同じ種類の約束を守る書き方があればそれに合わせる。値の形は変えず、今ある値を新しく弾く検査は足さない。取りうる値をすべて扱う分岐は、値を足すと型エラーになる形にする。観測した規約の判断に読んだ箇所は `path:line` で報告する。観測した規約の細目は `references/observed-conventions.md` に分けた。case を 3 つ足した (型検査が動く fixture でのステートマシンの正例、変えてはいけないものの hold-out、既存の書き方に合わせる正例)。12 case を with arm で 3 run ずつ回し、足した case の critical な grader はすべて 3/3、既存の grader で 2.0.0 より 2 run 以上下がったものは無い。critical でない grader のうち 3/3 でなかったのは 2 つで、どちらも 2/3 だった (検査の無い関数の引数の絞り込み、封のファイルを名指す報告)。2.0.0 で未計測だった「型検査で違反が落ちるのを見てから実行時の検査を外す」は、型検査が動く fixture で 3/3 を観測した。計測は TypeScript だけで、Ruby での動きは未計測である。
- **eval:** package の install が要る fixture を、`case.yaml` の `scaffold_script` で作る形を足した。case 01 の union 型を前提にした grader 2 つを、手段を問わず結果で判定する 1 つに替えた。
- **GLOSSARY:** 「述べられた規約」「観測した規約」「外から来る値」「値の形」を足し、「規約」の定義をこの 2 種類で言い直した。Evaluation に、scaffold の作り方と、scaffold と sandbox の性質 3 件を足した。

## v18.0.0 - 2026-11-10

### Changed

- **`enforce-conventions` 2.0.0 (BREAKING):** テスト、実行時の検査、lint の rule が既に落としている規約も、より強い場所で覆えるなら移す。1.0.0 は仕組みが何も検査していない規約だけを移し、既に仕組みが落とす規約には触れなかった。移した先で規約を破る例が落ちるのを見た規約は、それまで落としていた実行時の検査とテストを外す。見ていなければ外さず、型を通らない値が届く境界 (外部入力の読み込み) の検査は残す。型で書ける言語なら、型検査のコマンドが repo に無くても型を置ける場所に数え、落ちるのを見られなければ未検証と報告する。「振る舞いを変えない」は「型が受け入れる値に対する振る舞いを変えない」に絞った。case を 2 つ足した (テストが落としている import の向きを lint へ移す正例、型検査の無い repo で実行時の検査を外さない hold-out)。9 case を with arm で 3 run ずつ回し、全 case 1.00、旧版と比べて下がった grader は無い。without arm は足した正例で 0.36、hold-out で 0.89 だった。実行時の検査を型へ移して検査を外す正例は、sandbox に型検査が無いため未計測である。
- **GLOSSARY:** 「規約」の定義に、テスト、実行時の検査、lint が既に落としているものを足した。

## v17.1.0 - 2026-11-10

### Added

- **`check-pr` 1.0.0:** PR を出す前に、リポジトリの検査項目表 (`.github/pr-checks.md`。列は ID・対象の glob・項目) に照らして差分を検査し、検査結果ブロックを作る。検査する行は、対象の glob が変更ファイルに一致する行のすべて。判定は `OK` / `NG` / `判断不能` で、根拠は `path:line` かコマンドの出力に限る。ブロックには検査した HEAD の SHA を書くので、CI は「ブロックがある・SHA が最新の commit と一致する・対象の行がすべて載っている・`NG` が 0 件」を照合できる。`NG` は直さずに返す。2 case を両 arm で 3 run ずつ回し、with は両 case 1.00、without は正例 0.38・負例 1.00 だった。素の arm は skill が無いので検査結果ブロックを書かず、差には skill の有無そのものが含まれる。判断不能、承認なしの依頼、未 commit の変更、検査項目表が無い場合は未計測。
- **GLOSSARY:** 「検査項目表」と「検査結果ブロック」を足した。

## v17.0.0 - 2026-11-10

### Removed

- **`express-intent-in-code` (BREAKING):** plugin を廃止した。コードが既に言っていることを言い直すコメントの削除、jargon の改名、外部制約のコメントをテストへ移す働きは、どの plugin も引き継がない。定型プロンプトの仕上げの段は `enforce-conventions` に替える。

### Added

- **`enforce-conventions` 1.0.0:** 実装差分が守っているか破っている規約のうち、仕組みが検査していないものを、構造・型、lint、テストのうち覆える最も強い場所へ移す。規約は、差分のコメントと文書、repo の文書、作業ツリーの 2 箇所以上が同じ形で守っている約束から集め、製品が何を出力するかの固定は対象にしない。置いた仕組みは、規約を破る例で落ちるのを実行して確かめる。封の commit のファイルは変えず、変えないと通らない変更は戻して次の場所で試す。7 case を両 arm で 3 run ずつ回し、with は全 case 1.00、without は負例を除いて 0.25〜0.83 だった。素の arm は skill が無いと答えて作業を止める run が多く、差には skill の有無そのものが含まれる。
- **GLOSSARY:** 「規約」と「強制の場所」を足した。

## v16.3.0 - 2026-11-08

### Changed

- **`define-done` 4.3.0:** どの実装・部品・runtime・file が担うか (実装の選択) と、移行の途中の状態 (まだ移していない、〜のまま) を受け入れ基準にしない。要求がそれを名指しても、URL を開いた時に出る内容などの結果で観測する。実装の選択を返す関数と、その戻り値を固定する既存の試験は、外の境界にも既存の保証にもしない。case 33 で、旧版は 3 run すべてで基準に実装の選択を書き、新版は 3 run すべて書かなかった。
- **`define-done` の問い返し:** 問いが 0 件のときの結びに、`/define-done <計画のパス>` と計画のパスを書く。AC の規則を足した版で case 32 の「次の一歩を促す」が旧版 5/6 から 2/6 に下がったので直し、6/6 に戻した。
- **`check_seal.py`:** 改ざんの検査を、file ごとに、その file を最後に封じた commit から数える。封をし直せば、その前の変更は改ざんに数えない。要求の変更で古くなった前の封の AC を書き直すだけの commit は、`Define-Done-Supersedes: <置き換える AC-ID>[, ...]` の trailer で封じる。この封は改ざんの検査では封として数え、`verify` が流す封 (振る舞いを足した最後の `Define-Done-Seal:` の封) には選ばない。出力の最後の行に `exit: <code>` を出す。

## v16.0.0 - 2026-11-06

### Removed

- **`implement-plan` と `verify-plan` (BREAKING):** 2 plugin を廃止した。define-done の封の commit と `check_seal.py verify` だけで完了を判定する。実装は「封の受け入れテストと計画を変えずに実装する」という依頼で足り、変えれば `verify` が落ちる。サイクルごとの refactor の規律と、実装中の矛盾での早い停止は失う。既存 suite の回帰は CI に任せる。

### Changed

- **`define-done` 4.0.0 (BREAKING):** `check_seal.py` の `at-seal` を廃止し、`verify` を足した。`verify` は封の確認のあと、受け入れテストが封の時点の tree で落ち、今の tree で通るときだけ exit 0 を返す。実画面、CI や deploy の後でしか観測できない AC はテストを書かず、観測の手段を添えて回答の未検証に並べる。
- chain eval: implement-plan の代わりに、封のファイルを変えない実装の依頼と `verify` を流す依頼にした。
- eval: staging でしか観測できない AC を未検証に並べるかを測る case 29 を足した。case 17 の grader が、v15 で受け入れテストを書く契約に変えた後も「計画のほかに書かない」のままだったので、受け入れテストのファイルを許す形に直した。

## v15.1.0 - 2026-11-06

### Changed

- **`define-done` 3.1.0:** 要求の条件を満たさない入力 (条件の外側) は「資料が決めていない値」に当たらないとした。要求が入力の受け付ける範囲を広げるか変えるとき、条件を満たさない入力が変更前に受けていた扱い (拒否、例外) を保つことを、要求とその入力の検査を出典にした非影響の基準にする。既存の保証に、製品コードの中で入力を拒む検査を含めると明記した。chain eval の string-quantity で、`"1.5"` などを「決めていない」として基準にせず、計画の決定 (`parseInt`) どおりの実装で既存の検査が壊れていた。
- **採点:** `score_results` は、Gate で止まった run のコードを、隠しテストを落としたコードと数えず「Gate で停止」と数える。

## v15.0.0 - 2026-11-06

### Changed

- **`define-done` 3.0.0 (BREAKING):** 5 段目を検証の対応付け (`## Verification Plan`) から受け入れテストに替えた。各 AC を AC-ID で始まる名前の実行できるテストに翻訳し、変更前に振る舞いの不在で落ちることを確かめてから、受け入れテストと計画だけを含む封の commit (trailer `Define-Done-Seal:` と `Define-Done-Test-Command:`) を作る。起動は封の commit を作る承認を含む。資料に無い値を依頼が決めるよう求めていても、それだけでは Gate を止めず未決の判断に置く。`check_plan.py` と fingerprint をやめた。
- **`implement-plan` 3.0.0 (BREAKING):** 入力を封の commit にした。編集の前と最後に `check_seal.py check` を流し、封の受け入れテストと計画を変えずに red、green、refactor で通す。テストが要求や仕様と矛盾すれば直さずに止め、define-done のやり直しを返す。tripwire をやめた。
- **`verify-plan` 4.0.0 (BREAKING):** 封の確認 (`check_seal.py check`)、封の時点の tree で受け入れテストが落ちることの再現 (`at-seal`)、今の tree での受け入れテストの合否、封の時点からの回帰で判定する。テストの無い AC だけを直接観測で判定する。
- v14 の計画 (`## Verification Plan` を持ち封の commit の無いもの) は `implement-plan` と `verify-plan` の入力にならない。`define-done` をやり直すと受け入れテストと封の commit が作られる。
- eval: `define-done` に受け入れテストと封の commit の case を足し、廃止した Verification Plan だけを測る case と grader を除き、runner が受け付けない `(?m)` の grader を `flags: m` に直した。`implement-plan` に封の commit を持つ fixture 2 件 (受け入れテストを green にする、テストが仕様と矛盾したら止まる) を、`verify-plan` に 4 件 (FAIL、封の後の改ざん、振る舞いを見ないテスト、全件 PASS) を足し、v14 の Verification Plan を前提にした case を除いた。サイクルごとの refactor、計画外の変更での停止、baseline の区別、UI の引き渡し、指摘台帳、本番データの承認の assertion は未計測に残した。受け入れテストの翻訳の質を参照実装と要求の変種で数える `scripts/eval/mutant_score.py` と、trace からファイルを復元する `scripts/eval/restore_file.py` を足した。

## v14.1.0 - 2026-11-05

### Changed

- **`define-done` 2.1.0:** 要求どうしが範囲を定め合うとき (「旧名が残らない」と「移行の文書の言及は残す」) を矛盾として扱わず、基準の範囲を絞って両方を満たす規則を足した。他の要求が残すと定める文書や作らせる試験を、禁止と不在の範囲の「変更後も残る行」に戻した。種類の印や出典を足すだけなら AC の意味の変更に数えない。 計画の決定が要求を満たすかが依存先の振る舞いで決まり、その振る舞いを source か文書で確かめられないときは Gate を ready にしない。要求の表の `未検証` は外から観測する手段が無い要求だけに使う。 Ground Review の前提の確認で、DB やコンテナの起動、migration、外部への送信が要る確かめ方は実行しない。
- `define-done` の eval の計測器を、v14 の契約に合わせて直した (AC-ID の番号と件数への依存、節の位置の限定、assertion との食い違いを除いた)。

## v14.0.0 - 2026-11-05

### Changed

- **`define-done` 2.0.0 (BREAKING):** 受け入れ基準 (AC) を、依頼から抜き出した要求 (`## Requirements` の `R-n`、原文の引用付き) と既存の保証 (base にある試験・guard・不変条件の文書) だけから引くようにした。各 AC は行末に `(出典: …)` を持ち、計画の決定は出典にできない。段は要求の抜き出しを先頭に足した 5 段。MECE は要求 → AC、AC → 出典、決定 → 要求の 3 つだけを突き合わせ、要求を範囲外にした計画は Gate を ready にしない。`[禁止]` は検証の対応付けの `- Forbidden row:` (pattern と正の pathspec) にだけ持ち、oracle は定型にした。Ground Review に、決定が頼る依存先の振る舞いを依存先の source で反証する前提の確認を足した。書き終えたら同梱の `scripts/check_plan.py seal` で書式・出典・網羅・禁止を検査して封をする。
- **`implement-plan` 2.0.0 (BREAKING):** 始める前に同梱の `scripts/check_plan.py check` を流し、落ちたら編集しない。`[禁止]` の tripwire は書かず、最後に `check-green` で禁止の検査を確かめる。
- **`verify-plan` 3.0.0 (BREAKING):** 入力の検査 (fingerprint、エントリの欠け、見本の欠け) と `[禁止]` の判定を、同梱の `scripts/check_plan.py check-green` に置き換えた。AC が要求を満たせないと分かったときは計画の直し案を返さず、要求の見直しが要ることと根拠だけを返す。
- v13 の書式の計画 (`## Requirements` と出典の無いもの) は `implement-plan` と `verify-plan` の入力にならない。`define-done` をやり直すと新しい書式で書き直される。
- `CONTEXT.md` を `GLOSSARY.md` に改名し、完了の定義の用語 (受け入れ基準、要求、既存の保証、出典、決定、封、禁止の行) を足した。

## v13.0.0 - 2026-10-21

### Changed

- **`ground-design-in-codebase`、`define-acceptance-criteria`、`mece-plan-review`、`prepare-plan-for-implementation` → `define-done` (BREAKING):** 4 段のパイプラインを 1 スキルに統合した。設計境界のレビュー、受け入れ基準、MECE レビュー、検証の対応付けを順に行い、計画に `## Ground Review`、`## Acceptance Criteria`、`## MECE Review`、`## Verification Plan` を書く。止まるのは Gate が ready でないときの Verification Plan だけ。各段の規則は `references/` に置く。後続が読む節の書式は変えない。

## v10.0.0 - 2026-08-27

### Changed

- **`finalize-plan` → `prepare-plan-for-implementation` (BREAKING):** ready 済みの Acceptance Criteria と MECE Review から、依存順の実装作業と同一 plan 内の Verification Plan を準備する責務が名前から分かるようにした。Skill の実行契約は変更しない。

## v9.7.0 - 2026-08-22

### Changed

- **`create-pr` skill: レビュー物語の合成 (presentation commits) を導入 (1.2.0 → 1.3.0)**: commit 境界の作り方を「時系列履歴の救出」から「最終 tree からレビュー用の物語を合成する」方式へ変更。現行プランの commit-level change map を分割仕様として消費し、未 commit worktree や blended な未公開履歴では soft-reset + selective staging で commit を積み直す (境界を跨ぐファイルは `git diff` から切り出した hunk patch を `git apply --cached`、interactive tool は禁止)。push 前に最終 commit の tree が検証済み tree と bit 一致すること (`git diff <verified-ref>` が空) を必須化し、中間 commit の green は個別 commit が main に残る merge 戦略 (rebase / merge commit) の場合のみ要求 — squash 運用では endpoint 一致で足り、PR 本文に読み順を書く。「真に不可分なら 1 commit」の逃げ道条項は「plan にも変更自体にも分割線が無い場合のみ・分割コスト単独では不成立」へ絞り込み。evals/outcomes.md に blended worktree + change map + squash 運用の合成シナリオを追加。

## v8.0.0 - 2026-08-18

### Changed

- 19 skillsをobservable outcome、authorization boundary、failure handlingだけからclean-room再実装した。
- `apply-findings`のreview-onlyを除くnamed mode、skill固有argument、暗黙のcross-skill起動、agent/reference topologyを削除した。
- fixed regressionをoutcome evaluationとfresh executor / blind judge / hold-out検証へ置換し、validatorを構造契約へ限定した。
- Jira、任意のDesign Doc template、必須のcareer visionという現行config contractだけを保持した。
- 未参照のGoogle Docs export wrapperと、暗黙起動を促すredundancy hook一式を削除した。

## v7.0.0 - 2026-08-16

### Changed

- **`qa-ui` 2.0.0 (BREAKING):** 利用者が選ぶ Manual / Automation / Orchestrated モードを廃止。QA-ID source がある場合は `finalize-plan` の `manual` / `auto` 手段をそのまま実行し、QA-ID source がない場合だけ browser fallback を使う。
- Orchestrated 用 escalation ledger、held ID、browser 生成 QA-ID を削除し、QA ledger は初期化・auto command gate・完了集計に限定。QA-ID なし fallback と委譲時の handoff 境界は維持した。
- ルートの agent 指示を Claude Code と Codex で共有するため、`AGENTS.md` を `CLAUDE.md` への相対 symlink として追加した。

## v6.3.0 - 2026-08-15

### Changed

- 15 skills を frontier-model 向けに縮約し、重複説明・履歴・実行環境固有の制御を削減。判断境界と安全ゲートを自己完結させた。
- 各 skill の fixed regression を fresh executor で再検証し、description・plugin metadata・marketplace metadata を現行契約へ同期した。

## v3.100.0 - 2026-08-08

### Changed

- **`finalize-plan` skill: eval 繰り越し 10 件を消化 (2.10.0 → 2.11.0)**: PR #139 の fresh executor 再実行で観測した spec gap 10 件を、薄い規則 (表記の SSOT 整合・1〜2 行の規則・位置宣言) だけで消化した。表記 SSOT 整合: Step 1.7 の `0/0` という独自略記 (テンプレに実在せず executor が redo した) を output-template.md の `カテゴリ名+0` へ統一。lite tier の下流規定: 自動QA サブセクションは節ごと落とさず `自動QA: lite tier のため対象外 (auto 0 件)` の 1 行を残し (canonical 文言は output-template.md)、Step 4 は auto 0 件を正常扱いとする。代行時に `agents/manual-qa-planner.md` を Read する手続き (in-context fallback と同一) も明記。位置 SSOT: Step 3.5 のゲート結果行は「手動QA手順の末尾 = `### 自動QA` 見出しの直前」と output-template.md で宣言し、SKILL.md は参照のみ。
- **孤児 QA-ID を完了ブロック側へ**: manual/auto どちらの planner 出力にも載らない QA-ID の初期状態を `対象外(N/A)` (完了集計で許容) から手段 `-`・状態 `要人間確認` (許容されない) へ変更。割当漏れで実際に落ちた AC が黙って完了判定を通る穴を塞ぐ。`要人間確認` は qa-ui の完了判定 Bash (終端状態は `PASS` / `検証不能(真の制約)` / `対象外(N/A)` のみ) がそのままブロックするため、qa-ui 側の変更は不要。
- **照合・判定の曖昧さ解消ほか**: planner が出した検証内容が enumerate 元 AC と対応しない QA-ID は統合せず `要人間確認` に回す規則を Step 3 に追加 (QA-ID だけ合っていて中身がすり替わる経路は既存ゲートが素通しするため)。Step 3.5 の「実質同一」判定はプラン本文を対象とすると明記。Step 1.5 の ledger 駆動例外に固定の終了メッセージを追加 (従来は出力未定義の分岐だった)。⛔ 中断メッセージ 3 行目を「分析ファイルを一度も作っていない場合」に限定し、AC 済み・MECE 未了のプロトタイプ先行ユーザーを ledger 代替へ差し戻さないようにした。preflight は権限用途の逆算補完 (逆算元 QA-ID が特定できる範囲) とセル注記禁止 (後段が機械的に読む表のため) を明文化。evals/regression.md は孤児 QA-ID の assertion を追随更新 (シナリオ追加なし)。

## v3.99.0 - 2026-08-08

### Changed

- **`finalize-plan` skill: ブランチ戦略ロールを廃止 (2.9.0 → 2.10.0)**: Step 2A (起点ブランチ確定 + 作業ブランチ命名 + 重複チェック) と `## 実装準備` の `### ブランチ戦略` 出力サブセクション (新規作成形式・カレント継続形式の 2 テンプレ) を撤去し、Step 2B を Step 2 へ改称した。実装開始時に「カレントブランチから新しく切って実装」と指示すれば足り、事前のブランチ計画は欠陥検出に寄与しないため (利用者決定 2026-08-08)。2026-08-02 の branch-planner インライン化に続く簡素化で、`## 実装準備` は 手動QA手順 / 自動QA（テストコード仕様） の 2 サブセクションになった。
- **preflight の 起点ブランチ 欄は存置し、供給元だけ差し替え**: `/review-plan-diff` がこの欄を diff 比較元として読む (git 参照は禁止されている) ため欄自体は残し、Step 5 が `git branch --show-current` の値を機械転記する方式に変更 (判断・命名は行わない。detached HEAD 等で取得できない場合は `未定` として既存の AskUserQuestion 一括確認へ流す)。
- **連動更新**: `iterate-with-prototypes` (0.18.0 → 0.19.0) の ledger 駆動フォールバックを「ブランチ戦略 + QA 手順の 2 点」→「QA 手順」へ、`define-acceptance-criteria` (0.31.0 → 0.32.0) の併用推奨記述を「ブランチ・QA 手順を起こす」→「QA 手順を起こす」へ。両 plugin の evals/regression.md の該当 assertion も新仕様へ移行。finalize-plan の trigger から「ブランチ戦略を決めて」を削除。

## v3.98.0 - 2026-08-08

### Added

- **setup.sh Section E + `scripts/register-redundancy-guard-hook.sh`: redundancy-guard hook の settings.json 登録を自動化**: plain skill インストールで運べない唯一のマシンローカル要素だった PostToolUse 配線 (`~/.claude/settings.json`) を、対話セットアップの Section E または単体スクリプトで登録できるようにした。冪等 (登録済み検知)・非破壊 (jq 検証 → .bak 退避 → atomic mv)・不正 JSON は無変更で中止・settings 未存在時は新規作成。`CLAUDE_SETTINGS` で対象を差し替え可能 (テスト用)。これで新マシン導入は「skills install → setup.sh (または register スクリプト単体)」に閉じる。検証: fixture 6 種 (hooks なし / Stop のみ / 他 PostToolUse あり / 登録済み / 不正 JSON / ファイル無し) + 実 settings への冪等 no-op を確認。

## v3.97.0 - 2026-08-08

### Changed

- **`express-intent-in-code` skill: redundancy-guard.sh を skill 配下 `scripts/` へ収容し repo 管理化 (0.21.0 → 0.22.0)**: これまで `~/.claude/hooks/` 置きだった PostToolUse hook スクリプトを `skills/express-intent-in-code/scripts/redundancy-guard.sh` に移し、`skills update` で各マシンの `~/.agents/skills/express-intent-in-code/scripts/` へ配布されるようにした。user settings の hook コマンドは installed パスを `bash` 起動する形へ切替済み (exec bit 不問)。旧 `~/.claude/hooks/redundancy-guard.sh` は削除。マシンローカルに残るのは settings.json の配線 1 ブロックのみ (plain skill インストールは hook 登録を運べないため。新マシン導入 = skills install + settings 追記の 2 ステップ)。切替後の発火は live-fire で確認済み。

## v3.96.0 - 2026-08-08

### Changed

- **`express-intent-in-code` skill: ponytail 由来の「書く前の再利用梯子」を追加 (0.20.0 → 0.21.0)**: 新しい関数・ヘルパー・ファイルを書く前に ⓪要るか → ①codebase に既にあるか (隣接 grep) → ②言語標準 → ③プラットフォーム標準 → ④導入済み依存 → ⑤最小コード、を最初に該当した段で打ち切る 6 行を新設 (DietrichGebert/ponytail の ladder を翻案、MIT)。suppression を書きたくなったら①へ戻る接続も明記。description に new-file / before-writing トリガーを追加 (SKILL.md 42→48 行)。対の検知として user settings の redundancy-guard hook に「未追跡ファイル + 同 dir 同拡張子の隣接あり」で 1 回だけ `[reuse-ladder]` を注入する検出を追加。根拠: PR 40148 実測の再発明 4 件 (Capybara.string 不使用 / セレクタだけ違う複製関数 / 既存 pushText 再インライン / shared_examples 不使用) は全て梯子①で止まるべきケースで、5 スキルの誰も所有していなかった。`empirical-prompt-tuning` 2 シナリオ (再利用誘惑 / 移植回帰) で検証: 誘惑側は bias-free executor が書く前に梯子を自己適用し既存ヘルパー 2 本を import (複製ゼロ)、回帰側は純化健在。全 [critical] ○。
- **申し送り**: 既存ファイル内へのコピペブロック追加 (shared_examples ケース) は新規ファイル検知に掛からない — コミット時/CI 層 (バイト一致検知・dry-ssot-text 配線) が未実装の宿題。移植回帰で JSDoc 形式のやや長い why 文面が観測された (非クリティカル、文面は code-comments 7 原則の管轄)。

## v3.95.0 - 2026-08-08

### Changed

- **`express-intent-in-code` skill: 限界薄化 + 発火のハーネス移管 (0.19.0 → 0.20.0, BREAKING)**: SKILL.md を 163 行 → 42 行へ書き直し、references 8 本 (decision-procedure / generation-recipe / technique-catalog 等、計 ~760 行) と agents/intent-reader.md を撤去 (git 履歴に保存。ローカル退避: `~/.agents/skills/.archive/express-intent-in-code-v0.19/`)。残したのは判断規範のみ — 命名梯子 (造語禁止・caller 観測)、コメント昇格先マップ、真の why 4類型の残置基準、歯止め (drive-by 禁止・**n=1 は既存再利用 / rule of three は新抽象** の tie-break を新設)、fresh-eyes 検証。description は 1,048 → 356 chars (trigger-only)。
- **発火責務の分離**: 経路2 (生成時) の発火は user settings の PostToolUse hook (`redundancy-guard.sh`) が決定論的に担う — Edit/Write ごとに diff からコメント追加 / lint-suppression 追加を検知し、本スキルの適用指示を stderr (exit 2) で model へ自動注入する (セッション×ファイル単位の増分 dedup 付き)。根拠: SIGNPBL-103 の transcript 検証で、スキルが実装時に起動・全文ロード済みでも冗長コメントを生成し、効いたのはレビュー時の機械測定だけと判明 (CONTENT LIMIT)。プロンプト量はモデルの推論性能を奪うため、手続き記述を捨て検知をハーネス層へ移した。
- **申し送り**: 薄化後の empirical eval 未実施 (evals/regression.md の A/B 記録は旧 v0.8.0 構成のもの)。batch 起動時の 3 兆候スクリーニング (多義衝突 / 段0 ノイズ語) と出力フォーマット・委譲実行節は撤去 — 必要になった場合は hook 側の検知拡張で対応する方針。

## v3.94.0 - 2026-08-07

### Changed

- **`finalize-plan` skill: Figma 正本の未抽出検知 (能動ゲート) を Step 1.5 に追加 (2.8.0 → 2.9.0)**: プラン/DD 本文に Figma URL があるのに分析ファイルへ `## 正本抽出結果` が無い場合、警告して `/extract-figma-spec` の先行実行を提案する (委譲実行では要人間確認項目に含めて続行)。受動的な併用推奨だけでは実行が飛ばされ、実装後の Figma 照合で 24 atom 中 7 差分・2 ラウンドの手戻りが発生した実測に基づく。あわせて Gotchas に「QA planner への dispatch prompt で列構成を独自指定しない (qa-ui 審判ゲートの 6 列契約が壊れる)」を追記。`empirical-prompt-tuning` で 2 シナリオ (発火系 / 誤発火なし系) を検証し全 [critical] ○、accuracy 100%。
- **申し送り (今回未修正の既知課題)**: 分析ファイル内 Tier 表記の競合解決規則なし / 正本カバレッジ skip 行文言の SSOT 不一致 (SKILL.md・coverage-gate-bash・output-template) / lite tier と Step 3 テンプレ・Step 4 割当の整合未定義 / dual coverage 規則で manual 行が全消滅するケース / preflight の 未定 vs 該当なし の適用順。empirical 検証の executor 申告から採取。

## v2.2.0 (BREAKING for map-user-stories consumers) - 2026-05-15

### Changed

- **`map-user-stories` skill: タスク TSV カラム構造を再設計 (0.1.0 → 0.2.0, BREAKING)**: 旧フォーマットの「説明」列にプレフィックス記法（`完了条件: ` / `AC: `）を、「備考」列に `やらない: ` / `対象外: ` を書く運用を廃止し、専用列 `やること / やらないこと / 完了条件` の 3 列を新設。タスク TSV は 7 列 → 9 列に拡張。カラム順は Jira description のセクション順（`着手条件 → やること → やらないこと → 完了条件`）に揃え、`US_ID	Task_ID	タスク名	やること	やらないこと	完了条件	依存タスク	Jira	備考` とする。「備考」列は Ready 条件・参考リンク等の自由テキスト枠として残置（プレフィックス禁止）。US テーブル側の「技術メモ」列はプレフィックス記法を維持（後方互換）。`empirical-prompt-tuning` で 2 シナリオ（中規模 DD / 小規模仕様）を subagent 派遣検証して全 [critical] ○、accuracy 100%。
- **影響範囲**: `create-jira-issues` 側のパース仕様は別途追従が必要（タスク description の「やること」「やらないこと」「完了条件」の抽出元列名が変わる）。`map-user-stories` から出力された旧 7 列フォーマットのファイルは `create-jira-issues` で正しくパースされなくなる可能性があるため、本 bump 以降は新フォーマットでの再生成を推奨。

## v2.0.0 (BREAKING) - 2026-05-14

**破壊的変更:** モノリス plugin `omokawa-skills` (v0.11.0) を廃止し、14 個の独立 plugin に分割。

### 移行手順

```
/plugin uninstall omokawa-skills@omokawa-skills
/plugin marketplace update omokawa-skills
/plugin install <必要な skill>@omokawa-skills
```

### 新規 plugin (各 v0.1.0)

- `define-acceptance-criteria`, `mece-plan-review`, `finalize-plan` (+ agent), `review-design` (+ agent), `review-code-quality` (+ agent), `polish-before-commit` (+ agent), `model-data`, `map-user-stories`, `qa-ui`, `create-jira-issues`, `set-jira-story-points`, `translate-to-vision-story`, `dry-ssot-text`
- `create-pr` (slash command-only plugin)

### 理由

ユーザーが必要な skill だけを選択的に install できるようにするため。Jira/ChromeDevTools/個人 vision 関連は利用者によっては不要だが、旧構造ではすべて同梱されていた。

## [0.8.0] - 2026-05-14

### Added

- **`polish-before-commit` skill: Dead mock 削除ステップ (Step 6) 追加**: 実装側で `delegate :X` / `def X` を撤去した PR で、spec の対応 mock (`receive(:X)` / `receive_messages(X:)` / `instance_double(..., X:)` / `double(..., X:)`) が残置していないか検証し、orphaned mock を user 承認後に削除する。CI も lint も検出できない「dead mock 残置」によるレビュー差し戻しを構造的に防ぐ。
  - 削除単位の分類 (auto / Manual Review) を明文化: `receive(:X)` 単独 + `receive_messages` 全 key 削除済 → auto / `receive_messages` 部分削除 → Manual Review (書換え候補併記可)。
  - 同一 PR 内で同名 method が `+` で再追加されている場合は除外する exclusion ロジック。
  - 編集後は触った spec 全件を `bundle exec rspec <file1> <file2> ...` で検証し 0 failures を確認。
  - 非 Ruby プロジェクト (`*.rb` 変更なし or `spec/` 不在) では `[dead mock: スキップ (Ruby/RSpec 対象外)]` を最終レポートに明記してスキップ。
- `empirical-prompt-tuning` skill で 3 iteration 検証: median / partial-removal / non-Ruby-skip の 3 シナリオで Accuracy 100%、iter 3 で plateau。出典: 社内プランのレビュー指摘。

## [0.7.0] - 2026-05-14

### Added

- **`/omokawa-skills:create-pr`: カレントブランチ妥当性検証ステップ (1.5) 追加**: PR 作成前に current branch が conventional prefix (`feature/`, `fix/`, `refactor/`, `docs/`, `chore/`, `test/`, `perf/`, `style/`, `ci/`, `build/`) を持つか / default branch と同名か / プロジェクト規約 (`.github/CLAUDE.md` 等) に合致するかを検証し、雑なブランチ名 (worktree 名等) や default branch にいる場合は変更ドメインから推定した `<type>/<scope>-<short-desc>` で `git switch -c` を自動実行する。コミット後の rename は GitHub Branch Rename API の副作用で関連 PR が CLOSED される事故が観測されたため、コミット **前** に切替する設計。`empirical-prompt-tuning` skill で 2 iteration 検証済 (iter 1 baseline accuracy 43% → iter 2 で全 3 シナリオ accuracy 100% + [critical] 全 ○、iter 3 で micro-fix を bundle 適用)。

## [0.6.0] - 2026-05-14

### Added

- **`dry-ssot-text` skill 新設 (engineering bucket)**: AI 生成長文を DRY/SSOT 形式に refactor する。必要重複 (TOC / progress table / checklist) と不要重複 (説明文の二重書き) を判定基準 table で識別、不要重複のみ canonical location (文書末尾 §設計詳細) に集約してアンカーリンクで参照置換する。実証例: 1074 行 plan を 328 行に圧縮。
  - `empirical-prompt-tuning` skill で 3 iteration 検証済 (Accuracy 3 連続 100%、新 unclear points は iter 2 以降 0 件で plateau 確認)。

### Fixed

- `.claude-plugin/marketplace.json` の version が `.claude-plugin/plugin.json` と乖離していた問題を解消 (両方 0.6.0 に統一)。

## [0.2.0] - 2026-05-06

### Added

- **Claude Code marketplace 形式対応**：`/plugin marketplace add YasuakiOmokawa/skills` で 1 行配布が可能に
  - `.claude-plugin/marketplace.json` 新規追加
  - 単一リポで marketplace + plugin を兼任する形式（anthropic-agent-skills と同パターン）
- **`scripts/setup.sh` 新規追加**：bash 経由で `~/.claude/skills-config/*.md` を対話生成
- **`examples/skills-config/`** に設定値テンプレート 3 ファイル
- **`CHANGELOG.md`**（このファイル）

### Changed

- **設定値の保管方式をグローバル化**：プロジェクトごとの `docs/agents/*.md` → ユーザーマシンごとの `~/.claude/skills-config/*.md`
- **skills フラット構造化**：`skills/<bucket>/<name>/SKILL.md` → `skills/<name>/SKILL.md`（Claude Code autodiscovery が 1 階層しか見ない仕様への対応）
- **commands フラット構造化**：`commands/<dir>/<name>.md` → `commands/<name>.md`（コマンド名の冗長表記 `:create-pr:create-pr` を解消）
- **`plugin.json` を簡素化**：skills/commands/agents 配列を削除（Claude Code はファイル構造から autodiscovery する）
- **README**：クイックスタートを `/plugin marketplace add` 方式のみに統一
- **CLAUDE.md / CONTEXT.md**：フラット構造前提に書き換え。「engineering / personal」は説明上の分類のみで、物理ディレクトリは廃止

### Fixed

- `plugin.json` と `marketplace.json` の version 不整合（0.1.0 / 0.2.0）を 0.2.0 に統一
- `agents/*.md` 内の `${CLAUDE_PLUGIN_ROOT}/skills/<bucket>/<name>/` パスを `${CLAUDE_PLUGIN_ROOT}/skills/<name>/` に修正

### Security

- **セットアップ時の機密値が AI のコンテキストに乗らない設計に変更**
  - 旧: `/setup-omokawa-skills` スラッシュコマンド（Claude が AskUserQuestion で値を受け取る → transcript / API ログに残留）
  - 新: `bash scripts/setup.sh`（bash の `read` で値を直接ファイル書き込み、Claude 介在ゼロ）
  - 対象: Jira Cloud ID, プロジェクトキー, MCP プレフィックス等

### Removed

- `commands/setup-omokawa-skills/` スラッシュコマンド（bash 化に伴い廃止）
- 他リポ参照（mattpocock らへの言及、`npx skills` 案）— このリポジトリだけ読めば自己完結する文書に
- `docs/agents/` ディレクトリ（`examples/skills-config/` に移動）
- `.gitignore` の `~/.claude/skills-config/*.md` 関連エントリ（リポ外パスなので不要）

### Verified

別 Claude Code セッションで実機検証済み:

- skill 呼び出し: `omokawa-skills:define-acceptance-criteria` ✓ Successfully loaded
- command 呼び出し: `/omokawa-skills:create-pr` ✓ 単一名で認識・実行
- agents 認識: 4 個（review-design / review-code-quality / finalize-plan / polish-before-commit）

## [0.1.0] - 2026-05-06

### Added

- 初版リリース。プラン駆動開発（spec → AC → MECE → finalize → implement → review）を支える skills 集として公開
- **Skills（11 個）**:
  - `define-acceptance-criteria` — プランに 4 カテゴリ × 観点マトリクスで AC を定義
  - `mece-plan-review` — AC に対し 3 視点（QA / Tech / Red Team）で MECE 検証
  - `finalize-plan` — プラン → 実装可能形式へ変換、4 サブエージェント並列
  - `review-design` — 設計判定、4 reviewer 並列（Clean Architecture / Hexagonal / DDD / Anti-pattern）
  - `review-code-quality` — 設計レベル品質、3 analyzer 並列（凝集度 / 結合度 / 可読性）
  - `polish-before-commit` — コミット前のパターン一貫性自動修正
  - `model-data` — 要求文書から DBML 形式の ER 図生成
  - `map-user-stories` — 設計書 / Jira epic から US/Task 分解
  - `qa-ui` — ChromeDevTools MCP で UI 検証、Generator-Evaluator 分離
  - `create-jira-issues` — Jira チケット一括作成
  - `set-jira-story-points` — Story Points 一括設定
- **Commands（1 個）**: `/create-pr`（Conventional Commits + テンプレ準拠 + ラベル自動付与）
- **Agents（4 個）**: review-design / review-code-quality / finalize-plan / polish-before-commit
- `scripts/`: `link-skills.sh`, `link-commands.sh`, `link-agents.sh`, `list-skills.sh`
- ライセンス: MIT

[0.2.0]: https://github.com/YasuakiOmokawa/skills/releases/tag/v0.2.0
[0.1.0]: https://github.com/YasuakiOmokawa/skills/releases/tag/v0.1.0
