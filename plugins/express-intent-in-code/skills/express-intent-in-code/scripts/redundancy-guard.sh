#!/usr/bin/env bash
# PostToolUse (Edit|Write) guard: deterministic trigger for /express-intent-in-code.
# Detects, per edited code file (diff vs git HEAD; whole file if untracked):
#   1. net-added comment lines (added - removed) -> inject the express-intent judgment directive
#   2. added lint-suppression lines (rubocop:disable / eslint-disable / ts-ignore ...)
# Feedback is delivered to the model via exit 2 + stderr. Per-session/per-file dedup:
# re-fires only when the count grows, so settled judgments are not re-nagged.
set -u

payload=$(cat)
f=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_response.filePath // empty' 2>/dev/null)
sid=$(printf '%s' "$payload" | jq -r '.session_id // "ns"' 2>/dev/null)
[ -n "$f" ] && [ -f "$f" ] || exit 0

case "$f" in
  */node_modules/*|*/vendor/*|*/dist/*|*/build/*|*.min.*) exit 0 ;;
esac

ext="${f##*.}"
case "$ext" in
  rb|rake|py|pl|r) style=hash ;;
  ts|tsx|js|jsx|mjs|cjs|go|java|kt|swift|c|h|cc|cpp|hpp|cs|scss|php|rs) style=slash ;;
  *) exit 0 ;;
esac

if [ "$style" = hash ]; then comment_re='^[[:space:]]*#([^!]|$)'; else comment_re='^[[:space:]]*(//|/\*|\*)'; fi
suppress_re='rubocop:disable|eslint-disable|@ts-ignore|@ts-expect-error|# *noqa|type: *ignore'

dir=$(dirname "$f")
if git -C "$dir" ls-files --error-unmatch "$f" >/dev/null 2>&1 && git -C "$dir" rev-parse HEAD >/dev/null 2>&1; then
  file_diff=$(git -C "$dir" diff HEAD -- "$f" 2>/dev/null)
  added_lines=$(printf '%s\n' "$file_diff" | grep -E '^\+[^+]|^\+$' | cut -c2-)
  removed_lines=$(printf '%s\n' "$file_diff" | grep -E '^-[^-]|^-$' | cut -c2-)
else
  added_lines=$(cat "$f")
  removed_lines=""
fi
# net = added - removed: comment-reducing rewrites must not
# fire. Trade-off: an equal-count rewrite passes silently — acceptable, the goal is add-suppression.
added_comments=$(printf '%s\n' "$added_lines" | grep -Ec "$comment_re" || true)
removed_comments=$(printf '%s\n' "$removed_lines" | grep -Ec "$comment_re" || true)
comments=$(( added_comments - removed_comments ))
[ "$comments" -lt 0 ] && comments=0
suppress=$(printf '%s\n' "$added_lines" | grep -Ec "$suppress_re" || true)

file_comments=$(grep -Ec "$comment_re" "$f" || true)
file_nonblank=$(grep -c '[^[:space:]]' "$f" || true)
ratio=0
[ "${file_nonblank:-0}" -gt 0 ] && ratio=$(( file_comments * 100 / file_nonblank ))

statedir="${TMPDIR:-/tmp}/claude-eiic-guard"
mkdir -p "$statedir" 2>/dev/null || true
key=$(printf '%s' "$f" | md5sum | cut -c1-32)
state="${statedir}/${sid}-${key}"
first_sight=0
[ -f "$state" ] || first_sight=1
prev_comments=0; prev_suppress=0
[ -f "$state" ] && read -r prev_comments prev_suppress < "$state" 2>/dev/null
[ "$comments" -lt "${prev_comments:-0}" ] && prev_comments=$comments
[ "$suppress" -lt "${prev_suppress:-0}" ] && prev_suppress=$suppress
printf '%s %s' "$comments" "$suppress" > "$state" 2>/dev/null || true

warnings=""
if [ "$first_sight" = 1 ] && ! git -C "$dir" ls-files --error-unmatch "$f" >/dev/null 2>&1; then
  sibling=$(find "$dir" -maxdepth 1 -type f -name "*.${ext}" ! -name "$(basename "$f")" 2>/dev/null | head -1)
  if [ -n "$sibling" ]; then
    warnings="${warnings}[reuse-ladder] ${f}: 新規ファイル。書き終える前に、同 dir の隣接ファイルに再利用できる実装・イディオムが無いか確認する (梯子: ①codebase に既にあるか → ②言語標準 → ③プラットフォーム標準 → ④導入済み依存 → ⑤最小コード。最初に該当した段で止める)。新規ファイル追加はインライン処置の範囲外 — Skill ツールで express-intent-in-code を起動し、本文の再利用梯子・命名梯子に従って判定すること (各段の判定基準と歯止めは本文にのみある)。\n"
  fi
fi
if [ "$comments" -gt "${prev_comments:-0}" ]; then
  if [ "$comments" -le 2 ]; then
    warnings="${warnings}[express-intent] ${f}: コメント追加 計${comments}行 (ファイル全体のコメント率 ${ratio}%)。この規模 (1〜2 行) はこの場で判定してよい: 名前/型/定数/private メソッド/静的テスト (禁止規律) への昇格で置換できないか判断し、残せるのは真の why 4類型 (外部仕様/実測根拠/危険・セキュリティ/FIXME) と正本参照 1 文 (ADR / 正本コメントへのポインタ) を名前付き定義の直上に置くものだけ。対象名や機構を反復せず、理由・制約だけを書く。既存の 4類型コメント・正本参照は削らない。\n"
  else
    warnings="${warnings}[express-intent] ${f}: コメント追加 計${comments}行 (ファイル全体のコメント率 ${ratio}%)。3 行以上の追加はインライン処置の範囲外 — Skill ツールで express-intent-in-code を起動し、本文の昇格表・命名梯子・歯止めに従って全コメントを判定すること (この文面の要約には梯子と歯止めが載っていない)。既存の 4類型コメント・正本参照 1 文 (ADR / 正本コメントへのポインタ) は削らない。\n"
  fi
fi
if [ "$suppress" -gt "${prev_suppress:-0}" ]; then
  warnings="${warnings}[lint-suppression] ${f}: suppression 追加 計${suppress}行 (rubocop:disable / eslint-disable / ts-ignore 等)。suppression は非イディオムな書き方の兆候 — 隣接ファイルが同じ問題を suppression なしでどう解いているか確認してから残すこと。\n"
fi

if [ -n "$warnings" ]; then
  warnings="${warnings}subagent として実行中の場合は、この指摘と処置内容 (残した / 昇格した / スキル起動した) を呼び出し元への最終報告に 1 行含めること。\n"
  printf '%b' "$warnings" >&2
  exit 2
fi
exit 0
