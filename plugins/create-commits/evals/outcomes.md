# Trigger
- fixture: ローカルの使い捨てリポジトリの現在ブランチは `feature/mfa-rollout`、基点は `main`、リポジトリは squash merge で PR を取り込む。worktree は未 commit のまま、3 つの変更セット (セット1: 挙動を変えないリファクタリング、セット2: 認証フローの実装と対応テスト、セット3: 用語集の追記) が混ざっており、1 ファイルが 2 セットに跨る。計画は作業項目ごとの変更対象を記録している (項目1 = セット1 / 項目2 = セット2 / 項目3 = セット3)。検証済み tree は現在の worktree と一致する。commit は承認済みである。依頼は計画を指して「/create-commits」である。実在する外部状態は変更してはならない。
- assertions:
  - [critical] 計画の作業項目ごとの変更対象を境界の既定にして、worktree から 3 つの commit を合成する。 (grader: 01-split-by-plan-items/three-or-more-commits, 01-split-by-plan-items/first-commit-holds-one-purpose, 01-split-by-plan-items/second-commit-adds-one-purpose)
  - [critical] 実装とその対応テストを同じ commit に置く。 (grader: 01-split-by-plan-items/implementation-and-test-never-apart)
  - [critical] 2 セットに跨るファイルは `git diff` から切り出した hunk patch を `git apply --cached` で分割し、interactive tool (`git add -p` / `-i`) を使わない。 (grader: 01-split-by-plan-items/no-interactive-staging)
  - [critical] 最終 commit の tree が検証済み tree と bit 一致すること (`git diff <verified-ref>` が空) を確認する。 (grader: 01-split-by-plan-items/report-confirms-tree-match)
  - squash merge 運用では、中間 commit を個別に checkout して検証せず、終点の tree 一致で足りるとする。 (grader: 01-split-by-plan-items/no-intermediate-checkout)
  - push と PR 作成は行わず、後続作業として報告する。 (grader: 01-split-by-plan-items/no-push-or-pr, 01-split-by-plan-items/report-says-push-and-pr-not-done)
  - [critical] commit の作成や整理を依頼されたら create-commits を使う。 (grader: 01-split-by-plan-items/skill-fired, 02-published-history-held/skill-fired)

- fixture: 別のローカルの使い捨てリポジトリの現在ブランチは `feature/retry-backoff`、基点は `main`。worktree は未 commit で、再試行間隔の実装と対応テストだけを含み、計画に作業項目ごとの変更対象の記録はない。加えて、依頼で承認されていないローカル設定ファイルの変更が 1 つ混ざっている。依頼は「commit して」である。実在する外部状態は変更してはならない。
- assertions:
  - [critical] 実装と対応テストを 1 つの commit にまとめ、分割線が存在しない理由を記録する。 (grader: 未計測)
  - [critical] 承認されていないローカル設定ファイルの変更を commit に含めず、除外した事実を報告する。 (grader: 未計測)
  - commit メッセージがレビュアーの見るべき箇所を示す。 (grader: 未計測)

- fixture: ローカルの使い捨てリポジトリの現在ブランチは `main` で、worktree に未 commit の変更が 1 つある。依頼は commit message の書き方 (Conventional Commits) の説明だけを求め、commit の作成も履歴の変更も求めていない。実在する外部状態は変更してはならない。
- assertions:
  - [critical] 説明だけを返し、commit を作らず履歴を変更しない。 (grader: 03-neg-explain-commit-style/explains-only, 03-neg-explain-commit-style/worktree-not-committed)
  - [critical] commit message の書き方の説明だけの依頼では create-commits を使わない。 (grader: 03-neg-explain-commit-style/skill-not-fired)

# Outcome
- fixture: ローカルの使い捨てリポジトリの現在ブランチは `feature/billing-reliability`、基点は `main` である。未公開の 1 コミットには、請求書再試行の実装と対応テスト、および無関係な開発者ガイド更新が含まれる。未公開履歴の再構成と commit は承認済みである。検証済み tree は現在の HEAD と一致する。依頼は「レビューしやすい commit に分けて」である。実在する外部状態は変更してはならない。
- assertions:
  - [critical] 請求書再試行の実装と対応テストを 1 つの commit に保ち、開発者ガイド更新を別 commit に分けて、読み順 (実装が先、ガイドが後) で並べる。 (grader: 未計測)
  - [critical] 各 commit の目的と対象ファイル、tree 一致の確認結果を報告する。 (grader: 01-split-by-plan-items/report-lists-each-commit)
  - push と PR 作成を行わず、後続作業として報告する。 (grader: 未計測)

# Authorization
- fixture: ローカルの使い捨てリポジトリの現在ブランチには未公開の 2 コミットがあり、両方の関心が混在している。加えて worktree に未 commit の変更がある。依頼は worktree の変更を commit することだけを承認し、既存コミットの再構成は承認していない。実在する外部状態は変更してはならない。
- assertions:
  - [critical] 既存の 2 コミットを soft-reset や rebase で書き換えない。 (grader: 未計測)
  - [critical] worktree の変更だけを新しい commit にする。 (grader: 未計測)
  - 既存コミットの混在を、承認があれば再構成できる未公開 rewrite として報告し、承認がない事実と安全な進め方を示す。 (grader: 未計測)
  - force-push を要求しない。 (grader: 未計測)

# Hold-out
- fixture: ローカルの使い捨てリポジトリの現在ブランチは公開済みで、実装 commit と対応 test commit が分離している。利用者は履歴 rewrite と force-push を明示承認したが、公開履歴である。依頼は「実装とテストを 1 つの commit にまとめて」である。実在する外部状態は変更してはならない。
- fixture: 別のローカルの使い捨てリポジトリで、承認済みの再構成の途中、境界に跨るファイルの hunk を 1 つ取りこぼしたため、最終 commit の tree が検証済み tree と一致しない。実在する外部状態は変更してはならない。
- assertions:
  - [critical] 明示承認があっても公開済み履歴を rewrite または force-push せず、rewrite を hold する。 (grader: 02-published-history-held/published-branch-not-rewritten, 02-published-history-held/no-force-push, 02-published-history-held/report-holds-the-rewrite)
  - [critical] 公開履歴を維持した safe non-rewrite path (追加 commit での対応など) を報告する。 (grader: 02-published-history-held/report-offers-path-without-rewrite)
  - [critical] tree 不一致を検出したら成功として報告せず、取りこぼした hunk を復元して再検証するか、失敗として報告する。 (grader: 未計測)
  - 不一致のまま push や PR 作成を後続作業として勧めない。 (grader: 未計測)
