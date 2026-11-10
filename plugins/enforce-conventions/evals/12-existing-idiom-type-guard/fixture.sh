set -eu
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
printf 'node_modules/\n' > .gitignore
cat > package.json <<'EOF'
{
  "name": "onboarding",
  "private": true,
  "type": "module",
  "scripts": { "test": "node --test", "typecheck": "node node_modules/typescript/bin/tsc --noEmit" },
  "devDependencies": { "@types/node": "24.19.2", "typescript": "5.9.3" }
}
EOF
cat > tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "strict": true,
    "noEmit": true,
    "module": "nodenext",
    "target": "es2022",
    "allowImportingTsExtensions": true,
    "types": ["node"],
    "skipLibCheck": true
  },
  "include": ["src"]
}
EOF
NODE_OPTIONS=--use-system-ca npm install --include=dev --no-audit --no-fund --silent --fetch-retries=1
mkdir -p src
cat > src/email.ts <<'EOF'
export type Email = string & { readonly __brand: "Email" };

export function isEmail(input: string): input is Email {
  return /^[^@\s]+@[^@\s]+$/.test(input);
}
EOF
cat > src/welcome.ts <<'EOF'
import { type Email, isEmail } from "./email.ts";

export function welcomeSubject(to: Email): string {
  return `ようこそ <${to}>`;
}

export function welcomeSubjectFor(input: string): string | null {
  if (!isEmail(input)) return null;
  return welcomeSubject(input);
}
EOF
cat > src/welcome.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { welcomeSubjectFor } from "./welcome.ts";

test("メールアドレスなら件名を返す", () => {
  assert.equal(welcomeSubjectFor("aoi@example.com"), "ようこそ <aoi@example.com>");
});
test("メールアドレスでなければ null を返す", () => {
  assert.equal(welcomeSubjectFor("aoi"), null);
});
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
cat > src/postal-code.ts <<'EOF'
export function isPostalCode(input: string): boolean {
  return /^\d{3}-\d{4}$/.test(input);
}
EOF
cat > src/shipping-label.ts <<'EOF'
import { isPostalCode } from "./postal-code.ts";

export function shippingLabel(postalCode: string, name: string): string {
  if (!isPostalCode(postalCode)) throw new Error("postalCode must be checked with isPostalCode before it is used");
  return `〒${postalCode} ${name} 様`;
}

export function shippingLabelFor(input: { postalCode: string; name: string }): string | null {
  if (!isPostalCode(input.postalCode)) return null;
  return shippingLabel(input.postalCode, input.name);
}
EOF
cat > src/shipping-label.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { shippingLabel, shippingLabelFor } from "./shipping-label.ts";

test("郵便番号の形なら宛名ラベルを返す", () => {
  assert.equal(shippingLabelFor({ postalCode: "123-4567", name: "葵" }), "〒123-4567 葵 様");
});
test("郵便番号の形でなければ null を返す", () => {
  assert.equal(shippingLabelFor({ postalCode: "1234567", name: "葵" }), null);
});
test("確かめていない郵便番号では宛名ラベルを作れない", () => {
  assert.throws(() => shippingLabel("1234567", "葵"), /isPostalCode/);
});
EOF
