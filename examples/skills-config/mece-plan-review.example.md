# mece-plan-review 設定（example）

## このファイルの使い方

このファイルを `~/.claude/skills-config/mece-plan-review.md` にコピーし、自社の値で書き換えてください（`bash scripts/setup.sh` の対話生成の対象外なので手動でコピーします）。

omokawa-skills の `mece-plan-review` が、Wiki Researcher に渡す関連リポジトリ一覧を `gh repo list <org>` で集めるときにこのファイルを Read します。

## 設定値

- github_org: your-github-org
  - 関連リポジトリを探索する GitHub organization 名
  - `gh repo list <github_org>` で列挙できる名前と一致させる

## このファイルが無い場合

`git remote get-url origin` の `<org>/<repo>` から `<org>` を推定します。推定もできない場合（remote 未設定の non-git ディレクトリ等）は関連リポジトリ調査自体をスキップし、カレントリポジトリのみで MECE 検証を続行します。設定は任意で、無くても skill は止まりません。

## 注意

- organization 名は**機密値ではない**前提（public な GitHub org 名であり、漏洩しても直接攻撃にはならない）
- 配置先は `~/.claude/skills-config/mece-plan-review.md`（**マシンユーザーごとのグローバル設定**）。複数 org を行き来する場合は、主に使う org を書いておき、それ以外は git remote 推定に任せる運用を推奨
