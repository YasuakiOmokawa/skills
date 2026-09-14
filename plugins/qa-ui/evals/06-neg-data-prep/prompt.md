---
max_turns: 15
timeout_seconds: 300
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p bin db/fixtures data docs tools
cat > bin/seed <<'EOF'
#!/bin/sh
[ -f "$1" ] || { echo "usage: sh bin/seed db/fixtures/<name>.json"; exit 1; }
cp "$1" "data/$(basename "$1")"
echo "seeded data/$(basename "$1") into local db"
EOF
cat > db/fixtures/example.json <<'EOF'
{
  "teams": [{ "id": 1, "name": "example team" }],
  "owner_documents": [{ "id": 3, "team_id": 1, "title": "example", "status": "draft", "signers": [] }]
}
EOF
cat > docs/data-setup.md <<'EOF'
# ローカルデータの用意

`sh bin/seed db/fixtures/<name>.json` で JSON を local db に投入する。

- `teams`: id, name
- `owner_documents`: id, team_id, title, status (`draft` | `awaiting_signature` | `signed`), signers (email の配列)
- `/teams/:team_id/owner_documents/:id/signature_request` は status が `awaiting_signature` で signers が 1 件以上のときだけ表示できる。
EOF
cat > tools/browser.sh <<'EOF'
#!/bin/sh
case "$1" in
  open) echo "opened $2 (served build: build-0918)";;
  snapshot) echo "page: (served build: build-0918)"; echo "main: 署名依頼 [button#send '送信']";;
  shot) : > "$2"; echo "saved $2";;
  *) echo "usage: browser.sh open <url> | snapshot | shot <path.png>"; exit 1;;
esac
EOF
```

`http://localhost:3270/teams/1/owner_documents/14/signature_request` で /qa-ui できるようにデータ用意してほしい。
