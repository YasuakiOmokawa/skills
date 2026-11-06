export function createCart({ catalog }) {
  const lines = new Map();
  return {
    add(sku, quantity) {
      if (!catalog.has(sku)) throw new Error(`unknown sku: ${sku}`);
      if (!Number.isInteger(quantity) || quantity <= 0) throw new Error('quantity must be a positive integer');
      lines.set(sku, (lines.get(sku) ?? 0) + quantity);
    },
    total() {
      let sum = 0;
      for (const [sku, quantity] of lines) sum += catalog.get(sku) * quantity;
      return sum;
    },
  };
}
