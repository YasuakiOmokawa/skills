const ROLE_LEVEL = { MEMBER: 0, ADMIN: 1, OWNER: 2 };

function isAtLeast(role, minRole) {
  return Object.hasOwn(ROLE_LEVEL, role) && ROLE_LEVEL[role] >= ROLE_LEVEL[minRole];
}

export function createCompany({ ownerId }) {
  const roles = new Map([[ownerId, 'OWNER']]);
  const audit = [];
  return {
    join(userId, role) {
      roles.set(userId, role);
    },
    roleOf(userId) {
      return roles.get(userId) ?? null;
    },
    auditLog() {
      return [...audit];
    },
    remove(actorId, targetId) {
      throw new Error('not implemented');
    },
    transfer(actorId, toId) {
      throw new Error('not implemented');
    },
  };
}
