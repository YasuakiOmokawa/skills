---
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo && cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
git config user.email dev@example.com
git config user.name dev
mkdir -p plans src
cat > package.json <<'EOF'
{"type": "module", "scripts": {"test": "node --test"}}
EOF
cat > src/slug.js <<'EOF'
export function toSlug(title) {
  throw new Error('not implemented');
}
EOF
cat > plans/slug.md <<'EOF'
# 記事の slug 設計

## 1. 目的
記事の題名から、URL に使う slug を作れるようにする。

## 2. 仕様
- S-1: 公開 interface は `src/slug.js` の `toSlug(title)` とする。`title` は文字列で、戻り値も文字列。呼び出し側は文字列以外を渡さない。
- S-2: ASCII の英字の大文字 (A〜Z) だけを小文字 (a〜z) にする。ASCII 以外の文字は小文字にせず、S-4 で取り除く。
- S-3: 空白は半角スペース (U+0020)、タブ (U+0009)、LF (U+000A)、CR (U+000D) の 4 文字だけとする。空白が 1 文字以上続く所は `-` 1 つにする。全角スペースなどほかの文字は空白ではなく、S-4 で取り除く。
- S-4: a〜z、0〜9、`-` 以外の文字 (記号、`_`、全角の英数字、日本語などの ASCII 以外の文字を含む) は取り除く。日本語を含む題名でも、残った英数字はそのまま残す。
- S-5: S-2〜S-4 をこの順に当てた後、`-` が 2 つ以上続く所は `-` 1 つにし、先頭と末尾の `-` は取り除く。
- S-6: S-2〜S-5 を当てた結果が空になるとき (空文字、記号や日本語だけの題名など) は、空文字 `''` を返す。
- S-7: 長さの上限は設けない。
- 例: `toSlug('Hello, World!')` は `'hello-world'`、`toSlug('  A  -- B ')` は `'a-b'`、`toSlug('Node.js 入門')` は `'nodejs'`、`toSlug('日本語のタイトル')` は `''`、`toSlug('A\rB')` は `'a-b'`、`toSlug('A　B')` (全角スペース) は `'ab'`。
## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/slug.js | toSlug の実装 |

## 4. 決定
- D1: S-2〜S-5 の順に処理を当てて実装する。
EOF
git add -A && git commit -qm base
```

以下は、`repo/plans/slug.md` について、ここまでの私とあなたの議論です。

> 私: 記事の題名から URL の slug を作りたい。仕様は plans/slug.md の 2 節に全部書いた。日本語だけの題名は slug が空になってよい。空のときの扱いは別の issue で決めるので、この関数は空文字を返せばいい。
>
> あなた: 理解した内容です。要求は、`toSlug(title)` が plans/slug.md の 2 節の S-1〜S-7 のとおりに題名から slug を作ることです。ASCII の A〜Z だけを小文字にし、4 種類の空白の並びは `-` 1 つにし、a〜z、0〜9、`-` 以外は取り除き、`-` の連続は 1 つにして前後の `-` を取り除きます。結果が空なら空文字を返し、長さの上限はありません。やってはいけないことは、2 節に無い変換を足すことと、長さで切ることです。背景は、記事の URL に題名から作った slug を使いたいことで、空の slug の扱いは別の issue で決めます。
>
> 私: その理解で合っています。

/define-done plans/slug.md について、これまで議論した要求/要件のうち、まだ曖昧なものを自分に問い返してください。
