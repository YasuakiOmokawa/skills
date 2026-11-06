const BULK_QUANTITY = 10;

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
      for (const [sku, quantity] of lines) {
        const subtotal = catalog.get(sku) * quantity;
        sum += quantity >= BULK_QUANTITY ? Math.floor((subtotal * 9) / 10) : subtotal;
      }
      return sum;
    },
  };
}
