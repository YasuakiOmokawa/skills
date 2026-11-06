import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createReset } from '../src/reset.js';

const MIN = 60 * 1000;

function setup() {
  let clock = 0;
  const sent = [];
  const users = new Map([['a@example.com', { password: 'old', sessions: new Set(['s1', 's2']) }]]);
  const reset = createReset({ users, mailer: { send: (to, token) => sent.push({ to, token }) }, now: () => clock });
  return { reset, users, sent, advance: (ms) => { clock += ms; } };
}

test('S-1 registered request shows accepted screen and mails the address', () => {
  const { reset, sent } = setup();
  assert.deepEqual(reset.request('a@example.com'), { screen: 'accepted' });
  assert.equal(sent.length, 1);
  assert.equal(sent[0].to, 'a@example.com');
});

test('S-2 unregistered request looks identical and mails nothing', () => {
  const { reset, sent } = setup();
  assert.deepEqual(reset.request('nobody@example.com'), reset.request('a@example.com'));
  assert.equal(sent.filter((m) => m.to === 'nobody@example.com').length, 0);
});

test('S-3 link works at 29:59', () => {
  const { reset, users, sent, advance } = setup();
  reset.request('a@example.com');
  advance(30 * MIN - 1000);
  assert.deepEqual(reset.consume(sent[0].token, 'new'), { screen: 'done' });
  assert.equal(users.get('a@example.com').password, 'new');
});

test('S-3 link expires at 30:01 without changing password', () => {
  const { reset, users, sent, advance } = setup();
  reset.request('a@example.com');
  advance(30 * MIN + 1000);
  assert.deepEqual(reset.consume(sent[0].token, 'new'), { screen: 'expired' });
  assert.equal(users.get('a@example.com').password, 'old');
});

test('S-4 first use changes password and keeps sessions', () => {
  const { reset, users, sent } = setup();
  reset.request('a@example.com');
  assert.deepEqual(reset.consume(sent[0].token, 'new'), { screen: 'done' });
  assert.equal(users.get('a@example.com').password, 'new');
  assert.deepEqual([...users.get('a@example.com').sessions], ['s1', 's2']);
});

test('S-5 reuse shows used and keeps password', () => {
  const { reset, users, sent } = setup();
  reset.request('a@example.com');
  reset.consume(sent[0].token, 'new');
  assert.deepEqual(reset.consume(sent[0].token, 'other'), { screen: 'used' });
  assert.equal(users.get('a@example.com').password, 'new');
});

test('S-6 resend mails a working link', () => {
  const { reset, users, sent } = setup();
  assert.deepEqual(reset.resend('a@example.com'), { screen: 'accepted' });
  assert.equal(sent.length, 1);
  assert.deepEqual(reset.consume(sent[0].token, 'new'), { screen: 'done' });
  assert.equal(users.get('a@example.com').password, 'new');
});
