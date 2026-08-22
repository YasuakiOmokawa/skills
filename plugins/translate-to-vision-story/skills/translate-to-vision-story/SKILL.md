---
name: translate-to-vision-story
description: Use when creating a vision-linked article draft from project evidence for a target audience and goal, or revising an existing evidence-based draft under an approved direction; the vision may be supplied or configured.
---

# Workflow

1. 依頼と利用可能な文脈から、提供されたビジョン、活動を裏付ける証拠、対象読者、記事の目的、指定された草稿を特定する。ビジョンが未提示なら `~/.claude/skills-config/vision.md` を読み、存在しなければ草稿を作らず不足前提を返す。改稿では、承認済みの修正方針も特定する。
2. 提供された証拠から、ビジョンとの関係が明確な記事草稿を作る。
3. 初稿の書き込みを指定された草稿に限定する。改稿は承認済みの修正方針だけを反映し、外部公開や既存記事の変更は具体的な対象と変更内容が承認されている場合だけ行う。
4. 保存後に指定草稿を読み直し、実在することと、証拠、ビジョンとの関係、未確認事項が反映されていることを確認する。承認に基づいて外部公開または既存記事の変更を行った場合は、その反映も返却値または再取得した実状態から確認する。
5. 保存権限がない場合や保存内容を確認できない場合は初稿未作成または改稿未完了として報告し、保存済みと扱わない。
6. 草稿の保存先と保存状態、使用した証拠、解釈、未確認事項、失敗、未検証事項を返す。
