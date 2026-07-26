---
name: create-design-doc
description: プロトタイプと案件プランファイルの申し送り節から DD (Design Doc) を作成するときに使用。「DD を作って」「デザインドックを起こして」「設計書にして」で起動。テンプレートは ~/.claude/skills-config/create-design-doc/dd_template.md を参照し、未配置なら「テンプレートなしで作成」と宣言して進める。
---

# create-design-doc

プロトタイプで確定した設計を DD に起こす。

## 手順

1. プランファイルの `## 申し送り (プロトタイプ → DD)` と、プロトタイプの実装を読む
   (実装は PR があれば PR、無ければブランチの diff とコミット履歴。節が無ければその diff
   から設計判断・根拠・スコープ外を自分で整理してから始める)
2. `~/.claude/skills-config/create-design-doc/dd_template.md` を Read し、その見出し構成を
   骨組みにする (節の追加・削除・改番はしない)。未配置なら「テンプレートなしで作成」と宣言し、
   背景 / スコープ / 設計 / 設計判断と根拠 / Did not adopt / 未確定事項 の 6 節で書く。参考実例
   `~/.claude/skills-config/create-design-doc/dd_reference.md` があれば構成の参考にする
   (未配置ならスキップ)
3. DD を作成し、案件ディレクトリに `dd_<案件ディレクトリ名>.md` として保存する。設計判断は
   申し送りの根拠を転記し、採らなかった案は Did not adopt、スコープ外にしたことはスコープ外に
   残す。材料が無い項目は推測で埋めず、変更が発生しないなら「該当なし」、未決なら「未確定」と
   理由付きで書く。プロトタイプ側の欠落・矛盾も未確定に挙げる
4. DD に /dry-ssot-text → /purge-private-vocab (レビュー依頼前に plan 造語を除染)。DD は
   仕様書なので、節構成・節番号・表・コードブロックは崩さない
5. 保存したらここで停止し、人間の DD レビュー → LGTM を待つ (タスク分解・起票・本実装には
   進まない)

## Gotchas

- 申し送り節が無くて自分で整理した内容は、プランファイルに書き戻さず DD に書く (再構成が次の読者に一次情報として読まれる)

## 併用推奨 skill

- /map-user-stories, /create-jira-issues — LGTM 後のタスク分解と Jira 起票
- /build-poc, /build-prototype — 前工程 (この skill はそれらの申し送り節を入力にする)
