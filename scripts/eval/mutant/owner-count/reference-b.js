export function createCompany({ ownerId }) {
  const roles = new Map([[ownerId, 'OWNER']]);
  const owners = () => [...roles.values()].filter((role) => role === 'OWNER').length;
  return {
    join(userId, role) {
      roles.set(userId, role);
    },
    roleOf(userId) {
      return roles.get(userId) ?? null;
    },
    changeRole(actorId, targetId, role) {
      if (roles.get(targetId) === 'OWNER' && role !== 'OWNER' && owners() === 1) return { status: 409, error: 'last_owner' };
      if (roles.get(actorId) !== 'OWNER') return { status: 403 };
      if (!roles.has(targetId)) return { status: 400 };
      roles.set(targetId, role);
      return { status: 200 };
    },
    remove(actorId, targetId) {
      if (roles.get(targetId) === 'OWNER' && owners() === 1) return { status: 409, error: 'last_owner' };
      if (roles.get(actorId) !== 'OWNER') return { status: 403 };
      if (!roles.has(targetId)) return { status: 400 };
      roles.delete(targetId);
      return { status: 200 };
    },
  };
}
