---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src test node_modules/tiny-deploy
printf 'node_modules/\n' > .gitignore
printf '{ "name": "rotate", "private": true, "scripts": { "test": "node --te\x73t" } }\n' > package.json
printf '{ "name": "tiny-deploy", "version": "1.4.0", "main": "index.js" }\n' > node_modules/tiny-deploy/package.json
cat > node_modules/tiny-deploy/index.js <<'EOF'
const crypto = require("node:crypto");

function deploy(bundle, state, publish) {
  const hash = crypto.createHash("sha256").update(bundle).digest("hex");
  if (state.lastHash === hash) return { published: false };
  state.lastHash = hash;
  publish();
  return { published: true };
}

module.exports = { deploy };
EOF
cat > plans/rotate.md <<'EOF'
# secret の入れ替え 設計

## 1. 目的
API の secret を Secrets Store で回せるようにする。secret の値は bundle に含めず、公開の時に Secrets Store から読む。初回の release で secret が公開される。secret を回したら、同じ source のまま release を流し直すだけで新しい値が公開される。

## 2. 決定
| ID | 決定 |
|---|---|
| D1 | `tiny-deploy` の `deploy` に source をそのまま bundle として渡し、公開の時に Secrets Store の `API_KEY` を読む |

## Requirements
- R-1: secret の値を bundle に含めない (「secret の値は bundle に含めず、公開の時に Secrets Store から読む。」 計画:1. 目的)
- R-2: 初回の release で secret を公開する (「初回の release で secret が公開される。」 計画:1. 目的)
- R-3: 回した後は同じ source の再 release で新しい値を公開する (「secret を回したら、同じ source のまま release を流し直すだけで新しい値が公開される。」 計画:1. 目的)

## Ground Review
- 境界の適合: release は `tiny-deploy` に bundle を渡すだけで、責務は動かない。

## Acceptance Criteria
- [ ] AC-001: [振る舞い] Secrets Store の `API_KEY` が `k1` のとき、`release` を流すと公開された secret が `k1` になる (出典: R-2)
- [ ] AC-002: [振る舞い] `API_KEY` を `k2` に回してから、同じ source で `release` を流し直すと、公開された secret が `k2` になる (出典: R-3)
- [ ] AC-003: [振る舞い] `release` が `deploy` に渡す bundle は source と同じで、secret の値を含まない (出典: R-1)

## MECE Review
- AC IDs: AC-001, AC-002, AC-003
- 対応: R-1→AC-003、R-2→AC-001、R-3→AC-002。

| 決定 | 要求 |
|---|---|
| D1 | R-1, R-2, R-3 |

- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002, AC-003

### AC-001
- Oracle: test/release.test.js の "AC-001 first release publishes the secret" が pass
- Evidence anchors: src/release.js、test/release.test.js
- Prerequisites: 無い
- Required effects: package.json の test script でテストを実行する

### AC-002
- Oracle: test/release.test.js の "AC-002 rerun after rotation publishes the new secret" が pass
- Evidence anchors: src/release.js、test/release.test.js
- Prerequisites: 無い
- Required effects: package.json の test script でテストを実行する

### AC-003
- Oracle: test/release.test.js の "AC-003 bundle is the source only" が pass
- Evidence anchors: src/release.js、test/release.test.js
- Prerequisites: 無い
- Required effects: package.json の test script でテストを実行する
EOF
python3 - plans/rotate.md <<'PY'
import hashlib, sys
path = sys.argv[1]
lines = open(path, encoding="utf-8").read().splitlines(keepends=True)
def section(name):
    start = next(i for i, l in enumerate(lines) if l.rstrip("\n") == "## " + name)
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    return "".join(lines[start:end])
fp = hashlib.sha256("".join(section(n) for n in ("Requirements", "Acceptance Criteria", "Verification Plan")).encode()).hexdigest()
out = []
for l in lines:
    out.append(l)
    if l.rstrip("\n") == "- Gate: ready":
        out.append(f"- Fingerprint: {fp}\n")
open(path, "w", encoding="utf-8").write("".join(out))
PY
cat > src/release.js <<'EOF'
const { deploy } = require("tiny-deploy");

function release(source, secrets, state, live) {
  return deploy(source, state, () => {
    live.secret = secrets.get("API_KEY");
  });
}

module.exports = { release };
EOF
cat > test/release.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const { release } = require("../src/release");

const SOURCE = "export default handler;";

test("AC-001 first release publishes the secret", () => {
  const secrets = new Map([["API_KEY", "k1"]]);
  const live = {};
  release(SOURCE, secrets, {}, live);
  assert.equal(live.secret, "k1");
});

test("AC-002 rerun after rotation publishes the new secret", () => {
  const secrets = new Map([["API_KEY", "k1"]]);
  const state = {};
  const live = {};
  release(SOURCE, secrets, state, live);
  secrets.set("API_KEY", "k2");
  release(SOURCE, secrets, state, live);
  assert.equal(live.secret, "k2");
});

test("AC-003 bundle is the source only", () => {
  const state = {};
  release(SOURCE, new Map([["API_KEY", "k1"]]), state, {});
  assert.equal(state.lastHash, crypto.createHash("sha256").update(SOURCE).digest("hex"));
});
EOF
```

plans/rotate.md の実装が working tree に済んだ。/verify-plan して。コミットは指示があるまで禁止。
