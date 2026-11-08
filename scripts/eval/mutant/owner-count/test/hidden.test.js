import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createCompany } from '../src/membership.js';

function company() {
  const c = createCompany({ ownerId: 'owner' });
  c.join('admin', 'ADMIN');
  c.join('member', 'MEMBER');
  return c;
}

test('S-1: owner changes a member to admin', () => {
  const c = company();
  assert.equal(c.changeRole('owner', 'member', 'ADMIN').status, 200);
  assert.equal(c.roleOf('member'), 'ADMIN');
});

test('S-1: admin cannot change a role', () => {
  const c = company();
  assert.equal(c.changeRole('admin', 'member', 'ADMIN').status, 403);
  assert.equal(c.roleOf('member'), 'MEMBER');
});

test('S-2: owner removes a member', () => {
  const c = company();
  assert.equal(c.remove('owner', 'member').status, 200);
  assert.equal(c.roleOf('member'), null);
});

test('S-2: admin cannot remove', () => {
  const c = company();
  assert.equal(c.remove('admin', 'member').status, 403);
  assert.equal(c.roleOf('member'), 'MEMBER');
});

test('glossary OWNER: the last owner cannot demote themself', () => {
  const c = company();
  assert.deepEqual(c.changeRole('owner', 'owner', 'ADMIN'), { status: 409, error: 'last_owner' });
  assert.equal(c.roleOf('owner'), 'OWNER');
});

test('glossary OWNER: the last owner cannot remove themself', () => {
  const c = company();
  assert.deepEqual(c.remove('owner', 'owner'), { status: 409, error: 'last_owner' });
  assert.equal(c.roleOf('owner'), 'OWNER');
});

test('S-1: one of two owners can demote themself', () => {
  const c = company();
  c.join('second', 'OWNER');
  assert.equal(c.changeRole('owner', 'owner', 'ADMIN').status, 200);
  assert.equal(c.roleOf('second'), 'OWNER');
});

test('glossary OWNER: after removing the other owner, the remaining owner is the last', () => {
  const c = company();
  c.join('second', 'OWNER');
  assert.equal(c.remove('owner', 'second').status, 200);
  assert.deepEqual(c.changeRole('owner', 'owner', 'ADMIN'), { status: 409, error: 'last_owner' });
  assert.equal(c.roleOf('owner'), 'OWNER');
});

test('glossary OWNER: after demoting the other owner, the remaining owner is the last', () => {
  const c = company();
  c.join('second', 'OWNER');
  assert.equal(c.changeRole('owner', 'second', 'ADMIN').status, 200);
  assert.deepEqual(c.remove('owner', 'owner'), { status: 409, error: 'last_owner' });
  assert.equal(c.roleOf('owner'), 'OWNER');
});

test('S-1: after promoting a member, the original owner can demote themself', () => {
  const c = company();
  assert.equal(c.changeRole('owner', 'member', 'OWNER').status, 200);
  assert.equal(c.changeRole('owner', 'owner', 'ADMIN').status, 200);
  assert.equal(c.roleOf('member'), 'OWNER');
});

test('glossary OWNER: setting the last owner to OWNER again keeps them the last owner', () => {
  const c = company();
  c.changeRole('owner', 'owner', 'OWNER');
  assert.deepEqual(c.changeRole('owner', 'owner', 'ADMIN'), { status: 409, error: 'last_owner' });
  assert.equal(c.roleOf('owner'), 'OWNER');
});
