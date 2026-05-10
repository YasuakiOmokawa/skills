---
name: translate-to-vision-story
description: プロジェクト活動 (commits/PRs/README/ADR) を `~/.claude/skills-config/vision.md` のビジョン要素と照合し、対話型 draft → revise loop で Zenn 記事下書きを生成する。プロジェクト単位の物語化・キャリアブランディング・月次記事執筆時に使用。
---

# translate-to-vision-story

**プロジェクト単位の活動を、ビジョン整合した Zenn 記事下書きに翻訳する。**

## 何を解決するか

プロジェクトでやったこと (taimei-auth, freee-mcp, ID統合設計など) を、自分のビジョンに繋がる物語として記事化したい。しかし「何をどう書けばビジョンと整合するか」を毎回ゼロから考えるのは負担で、結果としてふりかえりが「単なる技術深掘り」で終わり、ブランディングに繋がらない。

このスキルは、`~/.claude/skills-config/vision.md` に書かれたビジョン要素と照合しながら、5 ステップの対話フローで Zenn 記事下書きを生成する。

## 入出力

- **入力**: プロジェクトディレクトリのパス (例: `~/mydev/taimei`)
- **出力**: Zenn 記事下書き Markdown ファイル (デフォルト: `<project-path>/docs/draft/YYYY-MM-DD-<title>.md`)

## 前提

- `~/.claude/skills-config/vision.md` が存在すること
  - 存在しない場合は `references/vision-config-template.md` をコピーして編集を促す

## 5 ステップ対話フロー

(続く section で各ステップを定義)
