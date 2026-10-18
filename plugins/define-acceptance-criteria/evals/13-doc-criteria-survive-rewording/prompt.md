---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Write, Edit, Bash]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q
mkdir -p packages/sdk/src plans
cat > packages/sdk/src/auth-host.ts <<'EOF'
export const MAGIC_LINK_EXPIRES_IN_SECONDS = 300;
EOF
cat > packages/sdk/README.md <<'EOF'
# sdk

## session

- `SessionData.role` が `undefined` の時は、権限なしとして扱う。
- redirect は consumer が行う。

## SDK の export を使い、自分で書かないもの

| 書かないもの | 使う export |
|---|---|
| Magic Link の有効期限 (秒) | `MAGIC_LINK_EXPIRES_IN_SECONDS` |
| 事業所 id の形 | `COMPANY_ID_PATTERN` |
EOF
cat > GLOSSARY.md <<'EOF'
# Glossary

**Magic Link**:
メールアドレス宛に送る、1 回だけ使えるログイン用のリンク。有効期限は 5 分。

**多要素認証 (MFA)**:
2 つ以上の要素で本人であることを確認する仕組み。
EOF
cat > plans/just-signed-up.md <<'EOF'
# 新規登録の直後かを判定する関数を SDK から出す

## 1. 目的

consumer が `user.createdAt` と Magic Link の有効期限を自分で比べずに、新規登録の直後かを判定できるようにする。

## 2. 範囲

1. `packages/sdk/src/auth-host.ts` に `isJustSignedUp(data, now?)` を足す
2. README に 2 行足す
3. `GLOSSARY.md` に用語を足す

## 3. 設計

### 3.1 関数

`now - Date.parse(data.user.createdAt) < MAGIC_LINK_EXPIRES_IN_SECONDS * 1000` を返す。期限ちょうどは false。

### 3.2 README

「SDK の export を使い、自分で書かないもの」の表の `MAGIC_LINK_EXPIRES_IN_SECONDS` の行の後:

| 新規登録の直後か (`user.createdAt` と Magic Link の有効期限の比較) | `isJustSignedUp(sessionData, now?)` |

「session」の注意の `SessionData.role` の行の後:

- 新規登録の直後かは `isJustSignedUp(session.data)` で判定する。user を作ってから Magic Link の有効期限の内側なら `true` を返す。`user.createdAt` と有効期限を自分で比べない。

### 3.3 GLOSSARY

**Magic Link** の後、**多要素認証 (MFA)** の前に足す:

**新規登録の直後**:
user が作られてから、**Magic Link** の有効期限が過ぎるまでの間。
EOF
git add -A
git commit -qm init
```

`repo/plans/just-signed-up.md` 設計を /define-acceptance-criteria して、設計を確定する。
