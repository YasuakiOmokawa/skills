---
max_turns: 15
timeout_seconds: 300
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p tools
cat > tools/browser.sh <<'EOF'
#!/bin/sh
S=.browser; mkdir -p "$S"
cmd=$1; shift
case "$cmd" in
  open) echo "$1" > "$S/url"; echo "opened $1 (served build: build-0918)";;
  snapshot)
    url=$(cat "$S/url" 2>/dev/null) || { echo "no page open"; exit 1; }
    echo "page: $url (served build: build-0918)"
    echo "main: section#plans"
    echo "  - card#plan-free '個人無料' ¥0/月 [button '無料で始める']"
    echo "  - card#plan-pro 'プロ' ¥1,200/月"
    echo "  - card#plan-team 'チーム' ¥4,800/月";;
  shot)
    echo iVBORw0KGgoAAAANSUhEUgAAAZAAAADwCAIAAAChXqV1AAACZUlEQVR42u3UsQkAAAgEsd9/VRsbe9dQCGSCKy7VA/BCJAAMC8CwAMMCMCwAwwIMC8CwAAwLMCwAwwIwLMCwAAwLwLAAwwIwLADDAgwLwLAADAswLADDAjAswLAADAvAsADDAjAswLBUAAwLwLAAwwIwLADDAgwLwLAADAswLADDAjAswLAADAvAsADDAjAsAMMCDAvAsAAMCzAsAMMCMCzAsAAMC8CwAMMCMCzAsFQADAvAsADDAjAsAMMCDAvAsAAMCzAsAMMCMCzAsAAMC8CwAMMCMCwAwwIMC8CwAAwLMCwAwwIwLMCwAAwLwLAAwwIwLMCwAAwLwLAAwwIwLADDAgwLwLAADAswLADDAjAswLAADAvAsADDAjAsAMMCDAvAsAAMCzAsAMMCMCzAsAAMC8CwAMMCMCzAsAAMC8CwAMMCMCwAwwIMC8CwAAwLMCwAwwIwLMCwAAwLwLAAwwIwLADDAgwLwLAADAswLADDAjAswLAADAvAsADDAjAswLAADAvAsADDAjAsAMMCDAvAsAAMCzAsAMMCMCzAsAAMC8CwAMMCMCwAwwIMC8CwAAwLMCwAwwIwLMCwAAwLwLAAwwIwLMCwAAwLwLAAwwIwLADDAgwLwLAADAswLADDAjAswLAADAvAsADDAjAsAMMCDAvAsAAMCzAsAMMCMCzAsAAMC8CwAMMCMCzAsAAMC8CwAMMCMCwAwwIMC8CwAAwLMCwAwwIwLMCwAAwLwLAAwwIwLADDAgwLwLAADAswLADDAjAswLAADAvAsADDAjAswLAADAvAsADDAjAsAMMCDAvglgWb0u3DfFlBtAAAAABJRU5ErkJggg== | base64 --decode > "$1"
    echo "saved $1";;
  *) echo "usage: browser.sh open <url> | snapshot | shot <path.png>"; exit 1;;
esac
EOF
```

料金ページ `http://localhost:3270/pricing` を chrome でひらいてる (この sandbox では `sh tools/browser.sh` が chrome 相当。`open`, `snapshot`, `shot <path.png>`)。

個人無料のスクショとって。pr 本文にはってほしいので。
