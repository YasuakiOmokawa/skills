#!/usr/bin/env bash
# gdocs タブ単体 markdown エクスポート (ai-prototype-flow 案件初期化・縮退(1) 用 wrapper)。
# tab= は非公開パラメータ — 壊れたら正本の規定どおり全文エクスポートへ切替える。
# token は rclone の OAuth access_token をコマンド置換で curl ヘッダへ直接渡し、
# 表示・保存しない (secret 衛生)。
# 導入: chmod +x と、settings の permissions.allow への Bash(<本スクリプト実パス>:*) 追加。
set -euo pipefail

if [ $# -ne 3 ]; then
  echo "usage: $(basename "$0") <docID> <t.tabID> <output-path>" >&2
  exit 2
fi

doc_id=$1
tab_id=$2
out=$3

fetch() {
  curl -sSL -w '%{http_code}' -o "$out" \
    -H "Authorization: Bearer $(rclone config dump | jq -r '.drive.token | fromjson | .access_token')" \
    "https://docs.google.com/feeds/download/documents/export/Export?id=${doc_id}&exportFormat=markdown&tab=${tab_id}"
}

status=$(fetch)
if [ "$status" = "401" ]; then
  rclone about drive: > /dev/null
  status=$(fetch)
fi

if [ "$status" != "200" ]; then
  echo "export failed: HTTP $status" >&2
  exit 1
fi

if head -c 256 "$out" | grep -qi '<html'; then
  echo "export failed: HTML response (auth/permission error)" >&2
  exit 1
fi

echo "saved: $out ($(wc -c < "$out") bytes)"
