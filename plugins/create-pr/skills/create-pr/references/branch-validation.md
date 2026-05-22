# ブランチ妥当性検証 (Step 1.5)

カレントブランチ名を以下の判定基準で検証する。**いずれかに該当する場合は新ブランチに切替必須**。**切替は必ずコミット前に実行する** (コミット後の rename は GitHub Branch Rename API 副作用で関連 PR が CLOSED されてしまう)。

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
4. `git switch -c <new-branch-name>` を実行
5. 切替後、`git branch --show-current` を再取得

## 該当しない場合

そのまま続行（既に `feature/order-notification` 等の正しいブランチ名なら no-op）。

## 注意

- `git switch -c` で切替できる前提として、`git status` で worktree が clean か uncommitted のみであることを確認
- merge / rebase 最中などで状態が複雑な場合はユーザに状況確認を促す
