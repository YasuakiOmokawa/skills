---
max_turns: 25
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p figma src artifacts
cat > figma/button.json <<'EOF'
{"name":"Checkout","lastModified":"2026-10-02T04:11:09Z","nodes":{"12:345":{"document":{"id":"12:345","name":"Button / Default","type":"COMPONENT","layoutMode":"HORIZONTAL","paddingLeft":16,"paddingRight":16,"paddingTop":12,"paddingBottom":12,"fills":[{"type":"SOLID","color":"#246BFD"}],"children":[{"id":"12:346","name":"label","type":"TEXT","characters":"支払う","style":{"fontSize":14}}]}}}}
EOF
cat > src/Button.css <<'EOF'
.btn {
  padding: 12px;
  font-size: 14px;
  background: #246BFD;
}
.btn:disabled {
  opacity: 0.4;
}
EOF
```

/extract-figma-spec で、決済画面の「支払う」ボタンを Figma と実装で比較してください。

Figma の MCP はこの sandbox では使えません。`figma/button.json` (Figma API の応答を保存したもの) が Figma 側の唯一の根拠です。実装は `src/Button.css` です。

比較する観点は 余白、文字、色、無効時 です。結果は `artifacts/figma-check.md` に残してください。書き込んでいいのはそのファイルだけで、`figma/` と `src/` は変更しないでください。
