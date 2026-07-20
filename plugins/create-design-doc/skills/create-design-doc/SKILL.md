---
name: create-design-doc
description: プロトタイプと案件プランファイルの申し送り節から DD (Design Doc) を作成するときに使用。「DD を作って」「デザインドックを起こして」「設計書にして」で起動。テンプレートは ~/.claude/skills-config/create-design-doc/dd_template.md を参照し、未配置なら「テンプレートなしで作成」と宣言して進める。
---

# create-design-doc

プロトタイプで確定した設計を DD に起こす。

## 手順

1. プランファイルの `## 申し送り (プロトタイプ → DD)` と、申し送りが指すプロトタイプ PR を
   読む (節が無ければプロトタイプの diff と会話から設計判断・根拠・スコープ外を自分で
   整理してから始める)
2. `~/.claude/skills-config/create-design-doc/dd_template.md` を Read する。未配置なら
   「テンプレートなしで作成」と宣言して進める。参考実例
   `~/.claude/skills-config/create-design-doc/dd_reference.md` があれば構成の参考にする
   (未配置ならスキップ)
3. DD を作成する。設計判断は申し送りの根拠を転記し、採らなかった案は Did not adopt に残す
4. DD に /dry-ssot-text → /purge-private-vocab → /cognitive-rhythm-writing (レビュー依頼前に
   plan 造語を除染)
5. (人間: DD レビュー → LGTM)

## 併用推奨 skill

- /map-user-stories, /create-jira-issues — DD 確定後のタスク分解と Jira 起票
- /build-poc, /build-prototype — 前工程 (この skill はそれらの申し送り節を入力にする)
