export function createCompany({ ownerId }) {
  const roles = new Map([[ownerId, 'OWNER']]);
  return {
    join(userId, role) {
      roles.set(userId, role);
    },
    roleOf(userId) {
      return roles.get(userId) ?? null;
    },
    changeRole(actorId, targetId, role) {
      throw new Error('not implemented');
    },
    remove(actorId, targetId) {
      throw new Error('not implemented');
    },
  };
}
