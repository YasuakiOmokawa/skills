# Auto-apply / verification / handoff specification

SKILL.md Step 4 の仕様。Step 3 で統合した **🔴 Critical / 🟠 Major** の指摘を「自動適用」と「申し送り」に振り分け、適用後に検証し、申し送りを `/polish-before-commit` へ渡すための contract を定義する。

## スコープ

- 対象は **🔴 Critical / 🟠 Major のみ**。🟡 Minor / 🔵 Info はレポート提案のみ (適用も申し送りもしない)。
- 自動適用は **main thread** が行う。analyzer agent (`agents/*.md`) は検出のみで従来通り「提案のみ・自動修正しない」。
- **Edit / Bash が使えない nested 実行時**は自動適用を行わず、🔴/🟠 を **全件申し送り** に回し、レポート冒頭に `[auto-apply: skipped (Edit/Bash 不可) → 全件申し送り]` を明示する。
  - nested 実行では Bash (`git rev-parse`) / Write も使えず**申し送りファイルへ書き込めない**ことが多い。その場合は申し送り内容 (下記フォーマット) を**レポート inline に転記して返し**、`[handoff: inline (write 不可)]` を明示する。申し送りの不変条件は「ファイルへ保存できたこと」ではなく**「情報が失われないこと (握りつぶし防止)」**。永続化は呼び出し元 / 後続 `/polish-before-commit` 実行に委ねる。

## 振り分け: auto-apply-safe vs needs-judgment

### auto-apply-safe (下記 5 条件を **すべて** 満たす finding のみ自動適用)

1. 単一ファイル内・局所スコープで完結する (cross-file 編集を伴わない)
2. public interface を変えない (メソッド名 / 引数 / 戻り値の型 / export シンボル)
3. 意味を保存する (挙動不変)、または挙動変更でも既存 spec/test がカバー済み
4. リスク領域 (auth / billing / payment / migration) に該当しない
5. business-impact 観点の finding ではない

具体例 (readability 中心):

- 関数内ローカル変数の曖昧名リネーム (`flag` → `isProcessing` 等、スコープが当該関数に閉じる)
- 否定形ブール → 肯定形 (局所)
- マジックナンバー → named constant (同一ファイル内)
- early return / guard clause 化
- デッドコード削除 (参照 0 を grep で確認できるもの)
- コードと矛盾するコメントの修正 / What コメントの削除 / 理由なし TODO への理由追記
- 局所的な nil ガード追加 (挙動保存。戻り値型が変わる Null Object 化は ④⑤ で除外)

### needs-judgment (常に申し送り。自動適用しない)

- cohesion: クラス分割 / 責務分離 / モジュール抽出
- coupling: 依存方向の変更 / rescue 設計変更 / cross-file な密結合解消
- 引数型・シグネチャ変更 (caller 経路 spec の audit が必要 — `~/.claude/rules/ruby-coding.md` 参照)
- ファイル / メソッドの行数超過に対する「分割」(分割単位は設計判断)
- public symbol のリネーム (cross-file 影響)
- レイヤー違反の移動 (templates→hooks 等、import 経路 = cross-file)
- business-impact 観点の **全 finding** (リスク認識であり機械的修正ではない)
- 修正方針が複数あり一意に定まらないもの

**axis / リスク領域の優先規則**: finding の所属 axis (cohesion / coupling / business-impact) と リスク領域 (条件④: auth / billing / payment / migration) は、auto-apply-safe の具体例文言に**優先する**。例: billing 領域の `rescue` finding が文面上「局所的な nil ガード追加」に見えても、coupling axis かつ billing 領域なので **needs-judgment**。safe 具体例 (リネーム / nil ガード等) は **readability axis かつ非リスク領域** のときだけ適用する。

**判断に迷ったら needs-judgment 側に倒す** (誤った自動 refactor より、握りつぶし防止の申し送りの方が安全)。

## 適用手順

1. 適用前に対象ファイルを **Read** し、正確な `old_string` を構成する (行番号だけでは置換できない)。
2. auto-apply-safe を Edit で適用する。**1 finding = 1 Edit** を原則とし、`old_string` / `new_string` を記録する (revert 用)。
   - **局所リネームの注意**: 変数名リネームは宣言行だけでなく **当該スコープ内の全参照** を同一 Edit (`replace_all` 相当) で同時に置換する。宣言行のみ置換すると参照箇所が未定義変数になり、意味保存 (条件③) に違反する。スコープが当該メソッドに閉じていることを Read で確認してから適用する。
3. 編集ファイルを言語別に集約し、次節の検証を実行する。

## 検証 (言語別、適用後に必ず実行)

| 言語 | コマンド |
|---|---|
| Ruby | `bundle exec rubocop <files>` → 編集ファイルに対応する `spec/` を `bundle exec rspec <specs>` |
| TypeScript/JavaScript | `yarn eslint <files> --fix` → `yarn prettier --check <files>` |
| その他 / コマンド不明 | 検証不可。適用済み finding に `未検証 (test/lint コマンド不明)` を付す |

- **検証 fail 時**: 該当 finding の Edit を **逆 Edit で revert** し (記録した `new_string`→`old_string`)、その finding を needs-judgment 扱いで申し送りに移し、理由 `auto-fix 試行→検証 fail で revert` を付す。pass した他の適用は維持する。
- 編集 spec を一意に特定できない場合は、変更ファイル群に関連する spec を広めに実行する。

## 申し送りファイル (contract — `/polish-before-commit` と共有)

- パス: `$(git rev-parse --git-dir)/quality-review-handoff.md` (= `.git/` 配下。commit されず repo-scoped、session / skill 跨ぎで永続)
- 書き込みは **overwrite** (毎 run、現 diff に対する needs-judgment の完全集合を上書き)。append しない。
- needs-judgment が **0 件なら申し送りファイルは作らない** (既存があれば削除する)。
- フォーマット:

```markdown
# 判断が必要な品質指摘 (review-code-quality 申し送り)
branch: <git branch --show-current の値>

<!-- /polish-before-commit がフロー末尾で読み込み・提示・クリアする -->

- 🔴 `/abs/path:line`: <finding 要約> — 見送り理由: <設計判断 / cross-file / business-impact 等>
- 🟠 `/abs/path:line`: <finding 要約> — 見送り理由: ...
```

## レポートへの反映

統合レポート ([integration-output.md](integration-output.md)) の各 🔴/🟠 finding に状態サフィックスを付す:

- 自動適用・検証 pass: `✏️ 自動適用済 (検証 pass)`
- 自動適用・revert: `↩️ 適用 revert (検証 fail) → 申し送り`
- 申し送り: `⏭ 申し送り → /polish-before-commit`

`### 総合サマリー` の直下に 1 行追加する:

`自動適用: N 件 (検証 pass) / revert: M 件 / 申し送り: K 件 → /polish-before-commit`
