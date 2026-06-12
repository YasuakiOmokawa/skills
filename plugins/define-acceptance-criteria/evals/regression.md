# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: standard tier / 複数主種別 (api_change + service_change)

plan mode (git 未着手) の plan: CSV エクスポート API (GET /api/exports/users.csv) に列 1 つ追加、変更ファイル予定 = controller + service + spec、「認可は既存のまま変更しない」。分析ファイル全文と `## 品質検証` サマリーをインラインで出させる。

### Requirements checklist
1. [critical] 必須セクション構成 (## 受け入れ条件 / ### 正常系 / 異常系 / エッジケース / 非影響確認) と AC 行頭 `- [ ] <controlled label>:` を遵守
2. [critical] tier = standard、主軸 3 軸 × 必須 3 カテゴリ = 9 セル全充填
3. 複数主種別のため deterministic classifier + ドロップ規則を使い根拠を `### 検討観点` に明記。既存認可 (存在するが不変) のドロップ時は非影響確認に regression 1 行
4. 技術リスク 3 件 (3 点セット、各 1 文、検証はコマンド入り)
5. `## 品質検証` の M 算出が実カウントと一致
6. `### Tier` 行を分析ファイル冒頭に記録
