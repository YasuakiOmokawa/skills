#!/usr/bin/env bash
# gdocs タブ単体 markdown エクスポート (build-poc PRD 凍結スナップショット・縮退(1) 用 wrapper)。
# tab= は非公開パラメータ — 壊れたら正本の規定どおり全文エクスポートへ切替える。
# token は shell 変数から curl の stdin header へ渡し、argv・表示・ファイルへ残さない。
# operator prerequisite: 実行前に chmod +x と必要な Bash permission を設定済みにする。agent は permission を追加しない。
set -euo pipefail

if [ $# -ne 3 ]; then
  echo "usage: $(basename "$0") <docID> <t.tabID> <output-path>" >&2
  exit 2
fi

doc_id=$1
tab_id=$2
out=$3
out_dir=$(dirname -- "$out")
out_name=$(basename -- "$out")
tmp=$(mktemp "${out_dir}/.${out_name}.tmp.XXXXXX")

cleanup() {
  if [ -n "$tmp" ]; then
    rm -f -- "$tmp"
  fi
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

fetch() {
  local access_token fetch_rc xtrace_was_enabled=0
  case $- in
    *x*) xtrace_was_enabled=1; set +x ;;
  esac
  access_token=$(rclone config dump | jq -r '.drive.token | fromjson | .access_token')
  if [ -z "$access_token" ] || [ "$access_token" = "null" ]; then
    access_token=''
    unset access_token
    if [ "$xtrace_was_enabled" -eq 1 ]; then set -x; fi
    echo "export failed: OAuth access token unavailable" >&2
    return 1
  fi
  if printf 'Authorization: Bearer %s\n' "$access_token" | \
      curl -sSL -w '%{http_code}|%{content_type}' -o "$tmp" -H @- \
        "https://docs.google.com/feeds/download/documents/export/Export?id=${doc_id}&exportFormat=markdown&tab=${tab_id}"; then
    fetch_rc=0
  else
    fetch_rc=$?
  fi
  access_token=''
  unset access_token
  if [ "$xtrace_was_enabled" -eq 1 ]; then set -x; fi
  return "$fetch_rc"
}

parse_fetch_result() {
  status=${fetch_result%%|*}
  content_type=${fetch_result#*|}
}

if ! fetch_result=$(fetch); then
  echo "export failed: curl transport error" >&2
  exit 1
fi
parse_fetch_result
if [ "$status" = "401" ]; then
  if ! rclone about drive: > /dev/null; then
    echo "export failed: OAuth refresh failed" >&2
    exit 1
  fi
  if ! fetch_result=$(fetch); then
    echo "export failed: curl transport error after OAuth refresh" >&2
    exit 1
  fi
  parse_fetch_result
fi

if [ "$status" = "403" ]; then
  echo "export failed: HTTP 403; switch to rclone full without retry" >&2
  exit 43
fi

if [ "$status" != "200" ]; then
  echo "export failed: HTTP $status" >&2
  exit 1
fi

content_type=$(printf '%s' "$content_type" | LC_ALL=C tr '[:upper:]' '[:lower:]')
if [[ "$content_type" == text/html* || "$content_type" == application/xhtml+xml* ]]; then
  echo "export failed: HTML Content-Type $content_type" >&2
  exit 1
fi

if ! python3 -c 'import pathlib, sys; text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"); sys.exit(0 if any(not (char.isspace() or char == "\ufeff") for char in text) else 1)' "$tmp" 2> /dev/null; then
  echo "export failed: empty, non-UTF-8, or whitespace-only response" >&2
  exit 1
fi

if LC_ALL=C grep -Eqi '<!doctype[[:space:]]+html|<html([[:space:]>]|$)|<head([[:space:]>]|$)|<body([[:space:]>]|$)' "$tmp"; then
  echo "export failed: HTML response (auth/permission error)" >&2
  exit 1
else
  html_scan_rc=$?
  if [ "$html_scan_rc" -ne 1 ]; then
    echo "export failed: HTML validator error" >&2
    exit 1
  fi
fi

mv -- "$tmp" "$out"
tmp=''
trap - EXIT HUP INT TERM

echo "saved: $out ($(wc -c < "$out") bytes)"
