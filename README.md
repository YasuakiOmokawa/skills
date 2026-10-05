# YasuakiOmokawa/skills

独立して導入できる agent skills の marketplace。

## Install

```bash
npx skills add YasuakiOmokawa/skills
```

## Plugins

| Plugin | Purpose |
|---|---|
| [`apply-findings`](./plugins/apply-findings/skills/apply-findings/SKILL.md) | レビュー指摘を適用する。依頼が機械的に安全な編集を承認しているとき、またはファイルを変更せずに具体的な編集候補を求めているときに使う。 |
| [`build-poc`](./plugins/build-poc/skills/build-poc/SKILL.md) | 技術選定または実現可能性を、実行可能な環境で成功基準に照らしたPoCや最小実験によって判断する必要があるときに使う。 |
| [`build-prototype`](./plugins/build-prototype/skills/build-prototype/SKILL.md) | 承認済みのPoCまたは同等の根拠があり、選定方式がコードベースの責務、慣習、契約に適合するかを実コードで確かめる必要があるときに使う。 |
| [`create-commits`](./plugins/create-commits/skills/create-commits/SKILL.md) | 現在のブランチの未commitまたは未公開の変更を、レビュアーが順に読める境界のcommitにまとめる。公開前のcommit、分割、ローカル履歴の再構成を求められたときに使う。 |
| [`create-design-doc`](./plugins/create-design-doc/skills/create-design-doc/SKILL.md) | 承認済み計画と、PoCとプロトタイプまたは同等の根拠による実現可能性とコードベース適合性の根拠から、実装判断に使うDesign Docを指定または導出した保存先に作る必要があるときに使う。 |
| [`create-pr`](./plugins/create-pr/skills/create-pr/SKILL.md) | 現在のブランチに対応するPRを作成または更新する。PRを開く、内容を改める、明示的にレビュー可能な状態にすることを求められたときに使う。 |
| [`define-acceptance-criteria`](./plugins/define-acceptance-criteria/skills/define-acceptance-criteria/SKILL.md) | 既存の計画や仕様を観測可能な受け入れ基準に変換する。成功、失敗、境界、非影響の振る舞いを判定可能にする必要があるときに使う。 |
| [`dry-ssot-text`](./plugins/dry-ssot-text/skills/dry-ssot-text/SKILL.md) | 正本文書と対象範囲の文書が特定されているとき、重複した読み手向けの手順を、読み手ごとの差異を保ったまま集約する。 |
| [`express-intent-in-code`](./plugins/express-intent-in-code/skills/express-intent-in-code/SKILL.md) | コメント、boolean、nullableな戻り値に置かれた意図を、名前、直和型、全域関数、テストへ移す。コードで言えることを言い直すコメント、ありえない状態を許すbooleanやoptionalの組み合わせ、2つの意味を持つ1つのnull、振る舞いを選ぶboolean引数、I/Oに埋もれた判断を含むコードが渡されたときに使う。 |
| [`extract-figma-spec`](./plugins/extract-figma-spec/skills/extract-figma-spec/SKILL.md) | 提供または取得できるFigmaの根拠を原子的な確認項目に分解し、指定されたフレーム、状態、部品について特定された実装とデザイン差分表で比較する必要があるときに使う。 |
| [`ground-design-in-codebase`](./plugins/ground-design-in-codebase/skills/ground-design-in-codebase/SKILL.md) | 関連する仕様と既存コードが責務とリスクについて具体的な根拠を示せるとき、提案された設計境界を実装前にレビューする。 |
| [`implement-plan`](./plugins/implement-plan/skills/implement-plan/SKILL.md) | Verification Planが全受け入れ基準を対応付けている準備済みの計画を実装する。テストで観測できる各基準を、計画の依存順にred、green、refactorで進める。 |
| [`map-user-stories`](./plugins/map-user-stories/skills/map-user-stories/SKILL.md) | 渡されたプロダクトの根拠をユーザーストーリーマップにする。ユーザー価値、ストーリー、実行可能なタスク、提供順序を追跡可能にする必要があるときに使う。 |
| [`mece-plan-review`](./plugins/mece-plan-review/skills/mece-plan-review/SKILL.md) | 計画と受け入れ基準を仕様とコードの根拠と比較する。MECEな網羅性レビュー、または明示的に承認されたレビュー更新を求められたときに使う。 |
| [`model-data`](./plugins/model-data/skills/model-data/SKILL.md) | 業務要求を既存のスキーマやSQLに照らしてモデル化し、一貫したデータモデル、必要に応じたDBML、データ設計、エンティティ関係、スキーマ整合性、SQLアンチパターンについての根拠付きの指摘を作る必要があるときに使う。 |
| [`prepare-plan-for-implementation`](./plugins/prepare-plan-for-implementation/skills/prepare-plan-for-implementation/SKILL.md) | 有効な受け入れ基準とreadyのMECE Reviewを持つ既存の計画を、具体的な作業の順序付けと同じ計画内の検証対応付けによって実装に備えさせる。計画の実装には使わない。 |
| [`purge-private-vocab`](./plugins/purge-private-vocab/skills/purge-private-vocab/SKILL.md) | 渡された定義により対象読者にとっての意味を確認できるとき、依頼で許可された読み手向け文書の内輪の用語を置き換える。 |
| [`qa-ui`](./plugins/qa-ui/skills/qa-ui/SKILL.md) | 観測可能な確認項目、期待状態、アクセス可能な描画済みページ、許可された操作が依頼で示されているとき、実装済みUIを検証する。 |
| [`verify-plan`](./plugins/verify-plan/skills/verify-plan/SKILL.md) | 実装済みの変更を、完了とみなす前に計画または受け入れ基準に照らして検証する必要があるときに使う。 |

`create-design-doc` は、存在する場合だけ `~/.claude/skills-config/create-design-doc/` のテンプレートと参考文書を使い、なければ取得済み根拠へ縮退する。

## Configuration

`bash scripts/setup.sh` で非機密のグローバル設定を生成できる。サンプルは [`examples/skills-config/`](./examples/skills-config/) にある。

## License

[MIT](./LICENSE)
