import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createCompany } from '../src/membership.js';

function company() {
  const c = createCompany({ ownerId: 'owner' });
  c.join('admin', 'ADMIN');
  c.join('member', 'MEMBER');
  return c;
}

test('S-1: admin removes a member and one audit line is recorded', () => {
  const c = company();
  assert.equal(c.remove('admin', 'member').status, 200);
  assert.equal(c.roleOf('member'), null);
  assert.equal(c.auditLog().filter((line) => line.event === 'membership_removed').length, 1);
});

test('S-1: member cannot remove', () => {
  const c = company();
  assert.equal(c.remove('member', 'admin').status, 403);
  assert.equal(c.roleOf('admin'), 'ADMIN');
});

test('S-1: admin cannot remove the owner', () => {
  const c = company();
  assert.notEqual(c.remove('admin', 'owner').status, 200);
  assert.equal(c.roleOf('owner'), 'OWNER');
});

test('ADR-0010: removing an already removed member is 404 and records nothing', () => {
  const c = company();
  c.remove('admin', 'member');
  assert.equal(c.remove('admin', 'member').status, 404);
  assert.equal(c.auditLog().filter((line) => line.event === 'membership_removed').length, 1);
});

test('S-2: owner transfers ownership and becomes admin', () => {
  const c = company();
  assert.equal(c.transfer('owner', 'admin').status, 200);
  assert.equal(c.roleOf('admin'), 'OWNER');
  assert.equal(c.roleOf('owner'), 'ADMIN');
});

test('ADR-0010: transferring to a non member is 404 and changes nothing', () => {
  const c = company();
  assert.equal(c.transfer('owner', 'stranger').status, 404);
  assert.equal(c.roleOf('owner'), 'OWNER');
  assert.equal(c.roleOf('stranger'), null);
  assert.equal(c.auditLog().length, 0);
});
