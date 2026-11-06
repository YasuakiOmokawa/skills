export function createAccounts() {
  const users = new Map();
  const memberships = new Map();
  const invitations = new Map();
  let seq = 0;
  return {
    register(userId) {
      users.set(userId, { lastUsedCompanyId: null });
    },
    createCompany(userId, companyId) {
      memberships.set(`${userId}:${companyId}`, 'OWNER');
      users.get(userId).lastUsedCompanyId = companyId;
    },
    companiesOf(userId) {
      return [...memberships.keys()].filter((key) => key.startsWith(`${userId}:`)).map((key) => key.split(':')[1]);
    },
    signIn(userId) {
      return { currentCompanyId: users.get(userId).lastUsedCompanyId };
    },
    invite(companyId, role) {
      seq += 1;
      const invitationId = `inv${seq}`;
      invitations.set(invitationId, { companyId, role });
      return invitationId;
    },
    accept(invitationId, userId) {
      throw new Error('not implemented');
    },
  };
}
