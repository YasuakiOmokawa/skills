---
max_turns: 12
timeout_seconds: 300
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src
cat > src/helpers.js <<'EOF'
function unusedHelper() { return null; }
module.exports = { unusedHelper };
EOF
cat > src/users.js <<'EOF'
function loadUser(id) { return { id }; }
module.exports = { loadUser };
EOF
cat > src/handler.js <<'EOF'
const { unusedHelper } = require("./helpers");
const { loadUser } = require("./users");

function getUsr(req) {
  return loadUser(req.headers["x-user-id"]);
}

module.exports = { getUsr };
EOF
```

code-review でこう指摘されました:

1. src/handler.js:1 `unusedHelper` を require しているが使っていない。
2. src/handler.js:4 `getUsr` は省略が読みにくい。`getUserFromRequest` にすべき。

この 2 つの指摘の意味を説明してください。直さなくていいです。
