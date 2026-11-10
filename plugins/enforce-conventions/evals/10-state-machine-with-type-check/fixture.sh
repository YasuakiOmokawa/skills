set -eu
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
printf 'node_modules/\n' > .gitignore
cat > package.json <<'EOF'
{
  "name": "shipping",
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
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
cat > src/shipment.ts <<'EOF'
export type Shipment = {
  id: string;
  status: "preparing" | "shipped" | "delivered";
  trackingNumber: string | null;
  deliveredAt: string | null;
};

export function createShipment(id: string): Shipment {
  return { id, status: "preparing", trackingNumber: null, deliveredAt: null };
}

export function ship(shipment: Shipment, trackingNumber: string): Shipment {
  return { id: shipment.id, status: "shipped", trackingNumber, deliveredAt: null };
}

export function deliver(shipment: Shipment, deliveredAt: string): Shipment {
  if (shipment.trackingNumber === null) throw new Error("a shipment must be shipped before it is delivered");
  return { id: shipment.id, status: "delivered", trackingNumber: shipment.trackingNumber, deliveredAt };
}

export function trackingUrl(shipment: Shipment): string {
  return `https://track.example/${shipment.trackingNumber!.toUpperCase()}`;
}

export function statusLabel(shipment: Shipment): string {
  if (shipment.status === "preparing") return "準備中";
  if (shipment.status === "shipped") return `発送済み (${shipment.trackingNumber})`;
  return `配達済み (${shipment.deliveredAt})`;
}
EOF
cat > src/shipment.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { createShipment, deliver, ship, statusLabel, trackingUrl } from "./shipment.ts";

test("作った直後の shipment は準備中", () => {
  const shipment = createShipment("s-1");
  assert.deepEqual(shipment, { id: "s-1", status: "preparing", trackingNumber: null, deliveredAt: null });
  assert.equal(statusLabel(shipment), "準備中");
});
test("発送すると追跡番号を持つ", () => {
  const shipped = ship(createShipment("s-1"), "ab12");
  assert.deepEqual(shipped, { id: "s-1", status: "shipped", trackingNumber: "ab12", deliveredAt: null });
  assert.equal(statusLabel(shipped), "発送済み (ab12)");
  assert.equal(trackingUrl(shipped), "https://track.example/AB12");
});
test("配達すると配達日を持つ", () => {
  const delivered = deliver(ship(createShipment("s-1"), "ab12"), "2026-04-03");
  assert.deepEqual(delivered, { id: "s-1", status: "delivered", trackingNumber: "ab12", deliveredAt: "2026-04-03" });
  assert.equal(statusLabel(delivered), "配達済み (2026-04-03)");
});
test("発送していない shipment は配達できない", () => {
  assert.throws(() => deliver(createShipment("s-1"), "2026-04-03"), /shipped before/);
});
EOF
