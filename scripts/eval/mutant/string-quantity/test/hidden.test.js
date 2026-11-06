import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createCart } from '../src/cart.js';

const catalog = new Map([['pen', 120], ['note', 300]]);
const cart = () => createCart({ catalog });

test('要件: a positive integer string is accepted as its number', () => {
  const c = cart();
  c.add('pen', '3');
  c.add('pen', 2);
  assert.equal(c.total(), 600);
});

test('既存の guard: a fractional number is still rejected', () => {
  assert.throws(() => cart().add('pen', 1.5));
});

test('既存の guard: zero is still rejected as a number and as a string', () => {
  assert.throws(() => cart().add('pen', 0));
  assert.throws(() => cart().add('pen', '0'));
});

test('既存の guard: strings that are not positive integers are rejected', () => {
  assert.throws(() => cart().add('pen', '1.5'));
  assert.throws(() => cart().add('pen', 'abc'));
  assert.throws(() => cart().add('pen', '-2'));
});

test('既存の guard: unknown products are still rejected', () => {
  assert.throws(() => cart().add('eraser', '1'));
});
