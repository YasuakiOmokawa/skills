import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createAccounts } from '../src/account.js';

function accountsWithCompany() {
  const accounts = createAccounts();
  accounts.register('owner');
  accounts.register('guest');
  accounts.createCompany('owner', 'acme');
  return accounts;
}

test('S-1: accepting joins the company with the invited role', () => {
  const accounts = accountsWithCompany();
  assert.equal(accounts.accept(accounts.invite('acme', 'MEMBER'), 'guest').status, 200);
  assert.deepEqual(accounts.companiesOf('guest'), ['acme']);
});

test('S-2: an invitation cannot be accepted twice', () => {
  const accounts = accountsWithCompany();
  const invitationId = accounts.invite('acme', 'MEMBER');
  accounts.accept(invitationId, 'guest');
  accounts.register('other');
  assert.equal(accounts.accept(invitationId, 'other').status, 410);
  assert.deepEqual(accounts.companiesOf('other'), []);
});

test('用語集 currentCompanyId: a first membership by invitation is selected in the next session', () => {
  const accounts = accountsWithCompany();
  accounts.accept(accounts.invite('acme', 'MEMBER'), 'guest');
  assert.equal(accounts.signIn('guest').currentCompanyId, 'acme');
});
