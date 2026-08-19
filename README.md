# YasuakiOmokawa/skills

独立して導入できる agent skills の marketplace。

## Install

```bash
npx skills add YasuakiOmokawa/skills
```

## Plugins

### Engineering

設定なしで動作する。利用可能な根拠と現在のリポジトリ規約を使い、不足情報は未検証または未解決として返す。

| Plugin | Purpose |
|---|---|
| [`apply-findings`](./plugins/apply-findings/skills/apply-findings/SKILL.md) | Applies review findings when a request authorizes mechanically safe edits or asks for concrete edit candidates without changing files. |
| [`build-poc`](./plugins/build-poc/skills/build-poc/SKILL.md) | 一つの実現可能性の問いを局所的な最小測定で判断する。成功基準と実行可能な環境があり、PoCや最小実験による可否判断を求められたときに使う。 |
| [`build-prototype`](./plugins/build-prototype/skills/build-prototype/SKILL.md) | 承認済みのPoCまたは同等の検証根拠を、対象リポジトリの慣習に沿うプロトタイプへ移す。対象コードと期待する振る舞いが示され、既存アプリへのプロトタイプ化を求められたときに使う。 |
| [`create-design-doc`](./plugins/create-design-doc/skills/create-design-doc/SKILL.md) | 承認済み計画と取得可能なプロトタイプまたは検証根拠からDesign Docを作る。計画が合意済みで、実装判断に使う設計文書と保存先を求められたときに使う。 |
| [`create-pr`](./plugins/create-pr/skills/create-pr/SKILL.md) | Create or update the pull request associated with the current branch when the user asks to open it, revise its content, or explicitly make it reviewable. |
| [`define-acceptance-criteria`](./plugins/define-acceptance-criteria/skills/define-acceptance-criteria/SKILL.md) | Convert an existing plan or specification into observable acceptance criteria when success, failure, boundary, or non-impact behavior must be made decidable. |
| [`dry-ssot-text`](./plugins/dry-ssot-text/skills/dry-ssot-text/SKILL.md) | Consolidates duplicated reader-facing procedures when a canonical document and in-scope documents are identified, while preserving audience-specific differences. |
| [`express-intent-in-code`](./plugins/express-intent-in-code/skills/express-intent-in-code/SKILL.md) | Clarifies intent in existing code when unclear names, responsibilities, comments, or lint suppressions need behavior-preserving cleanup. |
| [`extract-figma-spec`](./plugins/extract-figma-spec/skills/extract-figma-spec/SKILL.md) | 提供または取得できるFigmaの根拠を原子的な確認項目へ分解し、実装の観測値と比較する。対象フレーム、状態、部品と比較対象の実装が示され、デザイン差分の判定表を求められたときに使う。 |
| [`finalize-plan`](./plugins/finalize-plan/skills/finalize-plan/SKILL.md) | Finalize an implementation-ready plan from acceptance criteria and coverage evidence when work order, dependencies, change targets, and necessary QA material must be settled before implementation. |
| [`map-user-stories`](./plugins/map-user-stories/skills/map-user-stories/SKILL.md) | Turn supplied product evidence into a user story map when user value, stories, executable tasks, and delivery order must be made traceable. |
| [`mece-plan-review`](./plugins/mece-plan-review/skills/mece-plan-review/SKILL.md) | Compare a plan and acceptance criteria with specification and code evidence when a MECE coverage review or an explicitly authorized review update is requested. |
| [`model-data`](./plugins/model-data/skills/model-data/SKILL.md) | 業務要求と取得可能な既存スキーマやSQLから一貫したデータモデルを導き、必要に応じてDBMLを作り、SQLアンチパターンを指摘する。データ設計、ER相当の関係整理、既存スキーマの整合性確認を求められたときに使う。 |
| [`purge-private-vocab`](./plugins/purge-private-vocab/skills/purge-private-vocab/SKILL.md) | Replaces private vocabulary in authorized reader-facing documents when supplied definitions make the intended meaning checkable for the target audience. |
| [`qa-ui`](./plugins/qa-ui/skills/qa-ui/SKILL.md) | Verifies an implemented UI when the request provides observable checks, expected states, an accessible rendered page, and permitted interactions. |
| [`review-design`](./plugins/review-design/skills/review-design/SKILL.md) | Reviews a proposed design boundary before implementation when relevant specifications and existing code can provide concrete evidence about responsibilities and risk. |
| [`verify-plan`](./plugins/verify-plan/skills/verify-plan/SKILL.md) | Use when an implemented change must be verified against a plan or acceptance criteria before it can be considered complete. |

`create-design-doc` は、存在する場合だけ `~/.claude/skills-config/create-design-doc/` のテンプレートと参考文書を使い、なければ取得済み根拠へ縮退する。

### Personal

`~/.claude/skills-config/jira.md` に利用者のJira設定を置く。

| Plugin | Purpose |
|---|---|
| [`create-jira-issues`](./plugins/create-jira-issues/skills/create-jira-issues/SKILL.md) | Create Jira issues when the user explicitly asks to file listed, approved stories or tasks in a specified project and issue type, with per-item keys and failures. |
| [`set-jira-story-points`](./plugins/set-jira-story-points/skills/set-jira-story-points/SKILL.md) | Set Jira Story Points when the user provides explicit issue-key-to-point mappings and asks to update those issues, with requested and confirmed values reported per issue. |

### Career

`~/.claude/skills-config/vision.md` が必須。

| Plugin | Purpose |
|---|---|
| [`translate-to-vision-story`](./plugins/translate-to-vision-story/skills/translate-to-vision-story/SKILL.md) | プロジェクト活動の証拠を、提供されたビジョンとの関係が明確な記事草稿へ変換する。ビジョン、活動記録、対象読者、記事の目的が示された初稿作成、または承認済み方針による改稿を求められたときに使う。 |

## Configuration

`bash scripts/setup.sh` で非機密のグローバル設定を生成できる。サンプルは [`examples/skills-config/`](./examples/skills-config/) にある。

## License

[MIT](./LICENSE)
