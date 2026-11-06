import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createCompany } from '../src/membership.js';

function companyWithAdmin() {
  const company = createCompany({ ownerId: 'owner' });
  const { invitationId } = company.invite('owner', 'ADMIN');
  company.accept(invitationId, 'admin');
  return company;
}

test('S-1: owner and admin can invite members', () => {
  const company = companyWithAdmin();
  assert.equal(company.invite('owner', 'MEMBER').status, 201);
  assert.equal(company.invite('admin', 'MEMBER').status, 201);
});

test('S-1: member and outsider cannot invite', () => {
  const company = companyWithAdmin();
  const { invitationId } = company.invite('owner', 'MEMBER');
  company.accept(invitationId, 'member');
  assert.equal(company.invite('member', 'MEMBER').status, 403);
  assert.equal(company.invite('stranger', 'MEMBER').status, 403);
});

test('S-2: accepting joins with the invited role', () => {
  const company = companyWithAdmin();
  assert.equal(company.roleOf('admin'), 'ADMIN');
});

test('S-3: an invitation cannot be accepted twice', () => {
  const company = createCompany({ ownerId: 'owner' });
  const { invitationId } = company.invite('owner', 'MEMBER');
  assert.equal(company.accept(invitationId, 'a').status, 200);
  assert.equal(company.accept(invitationId, 'b').status, 410);
  assert.equal(company.roleOf('b'), null);
});

test('用語集 role: admin cannot create an owner through an invitation', () => {
  const company = companyWithAdmin();
  const { status, invitationId } = company.invite('admin', 'OWNER');
  assert.notEqual(status, 201);
  if (invitationId) company.accept(invitationId, 'climber');
  assert.notEqual(company.roleOf('climber'), 'OWNER');
});

test('用語集 role: owner can invite another owner', () => {
  const company = createCompany({ ownerId: 'owner' });
  const { status, invitationId } = company.invite('owner', 'OWNER');
  assert.equal(status, 201);
  company.accept(invitationId, 'second');
  assert.equal(company.roleOf('second'), 'OWNER');
});
