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
      const actorRole = roles.get(actorId);
      if (!actorRole || !isAtLeast(actorRole, 'ADMIN')) return { status: 403 };
      if (!roles.has(targetId)) return { status: 404, error: 'not_found' };
      if (roles.get(targetId) === 'OWNER' && actorRole !== 'OWNER') return { status: 403 };
      roles.delete(targetId);
      audit.push({ event: 'membership_removed', actorId, targetId });
      return { status: 200 };
    },
    transfer(actorId, toId) {
      if (roles.get(actorId) !== 'OWNER') return { status: 403 };
      if (!roles.has(toId)) return { status: 404, error: 'not_found' };
      roles.set(toId, 'OWNER');
      roles.set(actorId, 'ADMIN');
      audit.push({ event: 'ownership_transferred', actorId, toId });
      return { status: 200 };
    },
  };
}
