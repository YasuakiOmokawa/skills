---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p tools evidence src/sign
cat > tools/browser.sh <<'EOF'
#!/bin/sh
S=.browser; mkdir -p "$S"
cmd=$1; shift
case "$cmd" in
  open) echo "$1" > "$S/url"; echo "opened $1 (served build: build-0918)";;
  click) echo "clicked #$1";;
  snapshot)
    url=$(cat "$S/url" 2>/dev/null) || { echo "no page open"; exit 1; }
    echo "page: $url (served build: build-0918)"
    echo "viewport: 1280px"
    case "$url" in
      *ui=new*)
        echo "div#ui-switch-banner: hidden (computed display: none)"
        echo "main.sign-v2: 署名パッド [button#sign '署名する']";;
      *)
        echo "div#ui-switch-banner: visible '新しい署名画面を試す' [link '切り替える' href=?ui=new]"
        echo "main.sign-v1: 署名パッド [button#sign '署名する']";;
    esac;;
  shot)
    echo iVBORw0KGgoAAAANSUhEUgAAAZAAAADwCAIAAAChXqV1AAACZUlEQVR42u3UsQkAAAgEsd9/VRsbe9dQCGSCKy7VA/BCJAAMC8CwAMMCMCwAwwIMC8CwAAwLMCwAwwIwLMCwAAwLwLAAwwIwLADDAgwLwLAADAswLADDAjAswLAADAvAsADDAjAswLBUAAwLwLAAwwIwLADDAgwLwLAADAswLADDAjAswLAADAvAsADDAjAsAMMCDAvAsAAMCzAsAMMCMCzAsAAMC8CwAMMCMCzAsFQADAvAsADDAjAsAMMCDAvAsAAMCzAsAMMCMCzAsAAMC8CwAMMCMCwAwwIMC8CwAAwLMCwAwwIwLMCwAAwLwLAAwwIwLMCwAAwLwLAAwwIwLADDAgwLwLAADAswLADDAjAswLAADAvAsADDAjAsAMMCDAvAsAAMCzAsAMMCMCzAsAAMC8CwAMMCMCzAsAAMC8CwAMMCMCwAwwIMC8CwAAwLMCwAwwIwLMCwAAwLwLAAwwIwLADDAgwLwLAADAswLADDAjAswLAADAvAsADDAjAswLAADAvAsADDAjAsAMMCDAvAsAAMCzAsAMMCMCzAsAAMC8CwAMMCMCwAwwIMC8CwAAwLMCwAwwIwLMCwAAwLwLAAwwIwLMCwAAwLwLAAwwIwLADDAgwLwLAADAswLADDAjAswLAADAvAsADDAjAsAMMCDAvAsAAMCzAsAMMCMCzAsAAMC8CwAMMCMCzAsAAMC8CwAMMCMCwAwwIMC8CwAAwLMCwAwwIwLMCwAAwLwLAAwwIwLADDAgwLwLAADAswLADDAjAswLAADAvAsADDAjAswLAADAvAsADDAjAsAMMCDAvglgWb0u3DfFlBtAAAAABJRU5ErkJggg== | base64 --decode > "$1"
    echo "saved $1";;
  *) echo "usage: browser.sh open <url> | click <id> | snapshot | shot <path.png>"; exit 1;;
esac
EOF
cat > src/sign/SignPage.tsx <<'EOF'
import { UiSwitchBanner } from "./UiSwitchBanner";
export function SignPage({ ui }: { ui: "old" | "new" }) {
  return ui === "new" ? (
    <main className="sign-v2"><UiSwitchBanner to="old" /><SignPadV2 /></main>
  ) : (
    <main className="sign-v1"><UiSwitchBanner to="new" /><SignPadV1 /></main>
  );
}
EOF
cat > src/sign/UiSwitchBanner.tsx <<'EOF'
export function UiSwitchBanner({ to }: { to: "old" | "new" }) {
  return <div id="ui-switch-banner" className="ui-switch-banner">{to === "new" ? "新しい署名画面を試す" : "以前の画面に戻す"}</div>;
}
EOF
cat > src/sign/sign-v2.css <<'EOF'
.sign-v2 { padding: 0; }
.sign-v2 .pad { height: 320px; }
.sign-v2 .ui-switch-banner { display: none; }
EOF
```

`http://localhost:3270/documents/8/approvals/sign?token=demo-token` を chrome でひらいてる (この sandbox では `sh tools/browser.sh` が chrome 相当。`open`, `click`, `snapshot`, `shot <path.png>`)。新画面は `&ui=new` を付けた URL。

/qa-ui して。とりあえずきりかえバナーが新旧画面で消えてないこと。証跡のスクショは `evidence/` に残して。
