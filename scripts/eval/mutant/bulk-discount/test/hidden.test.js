import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createCart } from '../src/cart.js';

const catalog = new Map([['pen', 101], ['note', 250], ['clip', 7]]);

function cartWith(entries) {
  const cart = createCart({ catalog });
  for (const [sku, quantity] of entries) cart.add(sku, quantity);
  return cart;
}

test('9 items are not discounted', () => {
  assert.equal(cartWith([['note', 9]]).total(), 2250);
});

test('10 items are discounted by 10 percent', () => {
  assert.equal(cartWith([['note', 10]]).total(), 2250);
});

test('discounted subtotal is rounded down to the yen', () => {
  assert.equal(cartWith([['pen', 11]]).total(), 999);
});

test('each discounted line is rounded down separately', () => {
  assert.equal(cartWith([['pen', 11], ['clip', 13]]).total(), 999 + 81);
});

test('quantities of different products are not combined', () => {
  assert.equal(cartWith([['note', 5], ['pen', 5]]).total(), 1250 + 505);
});

test('quantity is the total of repeated adds of the same product', () => {
  assert.equal(cartWith([['note', 5], ['note', 5]]).total(), 2250);
});

test('undiscounted lines keep their full price next to a discounted line', () => {
  assert.equal(cartWith([['note', 10], ['pen', 3]]).total(), 2250 + 303);
});
