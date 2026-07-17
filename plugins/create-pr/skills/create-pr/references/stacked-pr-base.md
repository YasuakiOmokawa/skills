# 積み PR (stacked PR) の base 選定

**積み PR (open PR を持つ前段ブランチから派生したブランチ) の base**: `git log origin/<default>..HEAD` に前段ブランチのコミットが混ざり、その head に open PR があるなら、base をデフォルトブランチでなく前段ブランチにすると diff が自タスク分に絞れる。ただし後始末込みで運用する — 前段 PR の merge 後に `gh pr view --json baseRefName` で base の自動付け替えを確認する (GitHub の retarget は Web UI の merge ボタン経由の branch 削除でのみ動き、`gh pr merge --delete-branch` や手動 push 削除では後続 PR が close される)。close されたら reopen + base 付け直し。前段が squash merge された場合は `git rebase --onto <新 base> <前段ブランチ> <自ブランチ>` で前段 commit の diff 混入を除去する。
