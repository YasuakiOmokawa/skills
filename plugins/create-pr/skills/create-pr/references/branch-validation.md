# ブランチ妥当性検証 (Step 1.5)

最初に current branch の open PR を read-only query し、その branch 名と結果を cache してから、以下の判定基準を検証する。query 失敗時は新 branch を作らず、commit / push 前に停止する。命名違反なら新ブランチ名を決めるが、open PR が確認済みなら全 tier で branch を切り替えず、その PR の更新経路を保ち、命名違反だけを完了報告へ残す。open PR 0件では deep は関連検索が重複なしで完了するまで切り替えず、他 tier は決定直後に切り替える。切替は必ずコミット前に実行する。

## 判定基準

1. **同名禁止**: カレントブランチが `[base-branch]` と同一（例: `develop` チェックアウト中で base が `develop`）
2. **規約違反**: カレントブランチ名が conventional prefix を持たない。conventional prefix は以下のいずれか:
   - `feature/` / `feat/` / `fix/` / `refactor/` / `docs/` / `chore/` / `test/` / `perf/` / `style/` / `ci/` / `build/`
   - 例: `omo/gtr-2`, `wip-test`, `tmp`, worktree ディレクトリ名そのままは **規約違反**
3. **プロジェクト規約違反**: リポジトリの `.github/CLAUDE.md` / `<repo>/CLAUDE.md` / `<repo>/.claude/rules/git-branch*.md` にブランチ命名規約が明記されている場合、それに従わないブランチ名は規約違反扱い
   - **「命名規約明記」の定義**: ブランチ名の **prefix / pattern / 正規表現** がファイル内で明示されていること（例: `feature/機能名`, `^(feat|fix|refactor)/.+`）
   - base ブランチ指定のみ（「PR base は `develop`」）は **命名規約ではない**ため対象外

## 該当時の自動切替手順

1. Step 1 の `git diff [base-branch]...HEAD --stat` と `git status` の出力から **変更ドメイン** を推定
   - **diff 取得方法**: HEAD==base または uncommitted のみのケースでは diff が空を返すため、`git diff --stat`（unstaged）と `git diff --cached --stat`（staged）の **合算** で最大 dir / module 名を採用
   - **scope 候補の優先順位**:
     1. **ユーザ向け価値を生む機能ドメイン** を優先 (例: `order` / `license` / `auth`)
     2. **技術手段** は非優先 (例: `mailer` / `flipper` / `middleware` は scope にしない)
     3. モデル名 / コントローラ名 prefix があればそれを採用
2. branch 名を組み立てる:
   ```
   <type>/<scope>-<short-desc-kebab-case>
   ```
   - `<type>`: Step 5 の type 優先順位（`feat` > `fix` > ...）から仮選定
   - `<scope>`: 推定したドメイン
   - `<short-desc-kebab-case>`: 変更主目的を英小文字 kebab-case で 2〜4 単語
3. 生成例:
   - 注文確定通知メーラー追加 → `feature/order-notification-mailer`
   - 認証 token rotation バグ修正 → `fix/auth-token-rotation`
   - rubocop 違反修正 → `refactor/rubocop-cleanup`
4. deep なら `<new-branch-name>` を preflight state に保持し、関連検索が継続判定を返した直後に `git switch -c <new-branch-name>` を実行する。他 tier はここで実行する
5. 実行した場合は `git branch --show-current` を再取得

## 該当しない場合

そのまま続行（既に `feature/order-notification` 等の正しいブランチ名なら no-op）。

## 注意

- `git switch -c` で切替できる前提として、`git status` で worktree が clean か uncommitted のみであることを確認
- merge / rebase 最中などで状態が複雑な場合、状況（検出した状態・判断に迷う理由）を最終メッセージに説明し、処理を終了する（返答を待たない）
