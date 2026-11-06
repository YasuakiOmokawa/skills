export function createCart({ catalog }) {
  const lines = new Map();
  return {
    add(sku, quantity) {
      if (!catalog.has(sku)) throw new RangeError(`no such product: ${sku}`);
      const count = typeof quantity === 'string' && /^[0-9]+$/.test(quantity) ? Number(quantity) : quantity;
      if (!Number.isInteger(count) || count <= 0) throw new TypeError('invalid quantity');
      lines.set(sku, (lines.get(sku) ?? 0) + count);
    },
    total() {
      let sum = 0;
      for (const [sku, quantity] of lines) sum += catalog.get(sku) * quantity;
      return sum;
    },
  };
}
