# Trigger
- fixture: `guide/cancel.md`、`help/account.md`、`admin/offboarding.md` に同じ解約手順があり、集約先の正本は `guide/cancel.md` と指定され、管理者文書だけ監査上の注意を持つ。依頼Aは「手順を一つの正本へ集約して」、依頼Bは「二つの計算関数を共通化して」である。
- assertions:
  - [critical] 依頼Aでは読者向け解約手順を `guide/cancel.md` へ集約する。 (grader: 未計測)
  - [critical] 依頼Bではコードを変更しない。 (grader: 未計測)
  - 依頼Aで管理者向け注意を保持する。 (grader: 未計測)
  - 対象外の文章を編集しない。 (grader: 02-designated-canonical-consolidate/design-doc-untouched, 02-designated-canonical-consolidate/help-other-section-kept)
  - [critical] 文書の重複整理を求める依頼では、集約の作業を起動して進める。 (grader: 01-undesignated-canonical-config-wins/skill-fired, 02-designated-canonical-consolidate/skill-fired, 04-holdout-lint-scope-narrower/skill-fired)

- fixture: 作業ディレクトリに `eslint.config.js` と `tsconfig.json` があり、`CLAUDE.md` は `eslint.config.js` が強制する規則を、`README.md` は `tsconfig.json` の glob を書き写している。`README.md` の文は硬く冗長である。依頼は `README.md` の言い回しを読みやすく推敲することだけを求め、重複の整理は求めていない。
- assertions:
  - [critical] 言い回しの推敲だけを求める依頼では、重複を統合せず、書き写しを参照に替えず、削除しない。 (grader: 03-neg-polish-wording/glob-copy-kept, 03-neg-polish-wording/lint-rule-copy-kept, 03-neg-polish-wording/skill-not-fired)
  - 依頼された推敲を行う。 (grader: 03-neg-polish-wording/wording-changed)

# Outcome
- fixture: 三文書の四段階の解約手順は同義で、`guide/cancel.md` が正本に指定され、`admin/offboarding.md` の「監査記録を保存する」は管理者固有である。
- assertions:
  - [critical] 共通の四段階を指定された正本へ集約する。 (grader: 02-designated-canonical-consolidate/canonical-keeps-four-steps, 02-designated-canonical-consolidate/help-steps-removed, 02-designated-canonical-consolidate/admin-steps-removed)
  - [critical] 他の二文書から正本へ明確に到達できるようにする。 (grader: 02-designated-canonical-consolidate/help-links-canonical, 02-designated-canonical-consolidate/admin-links-canonical)
  - 管理者固有の監査上の注意を残す。 (grader: 02-designated-canonical-consolidate/admin-audit-kept)
  - 読者ごとの意味が変わっていないことを確認する。 (grader: 02-designated-canonical-consolidate/canonical-has-no-admin-note, 02-designated-canonical-consolidate/reread-after-edit)

- fixture: 作業ディレクトリに、`pg` の import を `src/db/client.ts` だけに許す lint 設定 (`eslint.config.js`) と、ビルド対象の glob を持つ `tsconfig.json` がある。`CLAUDE.md` は前者の規則を、適用範囲を含めて同じ意味で書き写し、`README.md` は後者の glob を書き写している。依頼は正本を指定しない。同じ文書には、どの仕組みも強制しない規則 (デバッグ用 `console.log` を commit しない、migration 番号の衝突確認) と手順 (ローカル DB の起動) もある。設計書 `docs/design/order-flow.md` も `pg` の規則を述べるが、依頼は設計書を対象外とする。
- assertions:
  - [critical] 正本が指定されないときは、強制力が最も強い場所 (型 > lint > テスト > 設定 > 文書) の記述を正本とし、文書側の言い直しを、その正本を指す参照に替えるか削除する。 (grader: 01-undesignated-canonical-config-wins/glob-copy-removed, 01-undesignated-canonical-config-wins/lint-rule-copy-removed)
  - [critical] 強制する仕組みを確認できない規則と手順は、文書に残す。 (grader: 01-undesignated-canonical-config-wins/console-log-rule-kept, 01-undesignated-canonical-config-wins/migration-rule-kept, 01-undesignated-canonical-config-wins/local-db-step-kept)
  - [critical] 正本にした設定ファイルとコードを変更しない。 (grader: 01-undesignated-canonical-config-wins/eslint-config-unchanged, 01-undesignated-canonical-config-wins/tsconfig-unchanged, 01-undesignated-canonical-config-wins/client-ts-unchanged)
  - 対象外の設計書を変更せず、正本としても指さない。 (grader: 01-undesignated-canonical-config-wins/design-doc-untouched, 01-undesignated-canonical-config-wins/no-design-doc-pointer)
  - 文書から外した規則と、それを強制する仕組みを報告する。 (grader: 01-undesignated-canonical-config-wins/report-names-enforcers)

# Authorization
- fixture: 編集許可は三つの指定文書だけにあり、`src/cancel.ts` は読み取りも編集も対象外で、外部文書庫への反映は許可されていない。固定された書き込み結果では `guide/cancel.md` と `admin/offboarding.md` の保存は成功し、`help/account.md` は権限エラー `EACCES` で保存されず、元の内容が残っている。
- assertions:
  - [critical] 変更を三つの指定文書だけに限定する。 (grader: 未計測)
  - [critical] `src/cancel.ts` と外部文書庫を変更しない。 (grader: 未計測)
  - `guide/cancel.md` と `admin/offboarding.md` の保存成功、および `help/account.md` の `EACCES` と未変更を部分失敗として報告する。 (grader: 未計測)
  - 参照先を確認できないまま重複文を削除しない。 (grader: 未計測)

# Hold-out
- fixture: パスワード再設定手順は二文書で同義だが、保存期間の記述は一般利用者向けが一年、規制対象者向けが七年で、法的区分に基づく差である。
- assertions:
  - [critical] 同義の再設定手順だけを正本へ集約する。 (grader: 未計測)
  - [critical] 一年と七年の保存期間を統一しない。 (grader: 未計測)
  - 各読者から再設定手順の正本へ到達できるようにする。 (grader: 未計測)
  - 保持した法的差異を結果として報告する。 (grader: 未計測)

- fixture: 作業ディレクトリの `eslint.config.js` は `pg` の import を `src/**/*.ts` で `src/db/client.ts` 以外に禁じるが、`CLAUDE.md` の同じ規則は `scripts/` を含む全ての TypeScript に適用すると述べ、`scripts/seed.ts` は lint の対象外にある。`README.md` は `tsconfig.json` の glob を同じ意味で書き写している。依頼は正本を指定しない。
- assertions:
  - [critical] 強制する仕組みの適用範囲が文書の規則より狭いときは、その規則を文書に残し、参照に替えず、削除しない。 (grader: 04-holdout-lint-scope-narrower/broader-rule-kept)
  - [critical] 同じ意味と確認できた `README.md` の glob だけを、参照に替えるか削除する。 (grader: 04-holdout-lint-scope-narrower/glob-copy-removed)
  - [critical] 適用範囲を広げるために lint 設定を変更しない。 (grader: 04-holdout-lint-scope-narrower/eslint-config-unchanged)
  - 規則を残した理由として、仕組みが覆わない範囲を報告する。 (grader: 04-holdout-lint-scope-narrower/report-explains-scope-gap)
