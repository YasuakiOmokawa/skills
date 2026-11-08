export function createCompany({ ownerId }) {
  const roles = new Map([[ownerId, 'OWNER']]);
  let ownerCount = 1;
  return {
    join(userId, role) {
      roles.set(userId, role);
      if (role === 'OWNER') ownerCount += 1;
    },
    roleOf(userId) {
      return roles.get(userId) ?? null;
    },
    changeRole(actorId, targetId, role) {
      if (roles.get(actorId) !== 'OWNER') return { status: 403 };
      if (!roles.has(targetId)) return { status: 404 };
      const before = roles.get(targetId);
      if (before === 'OWNER' && role !== 'OWNER' && ownerCount === 1) return { status: 409, error: 'last_owner' };
      roles.set(targetId, role);
      if (before !== 'OWNER' && role === 'OWNER') ownerCount += 1;
      if (before === 'OWNER' && role !== 'OWNER') ownerCount -= 1;
      return { status: 200 };
    },
    remove(actorId, targetId) {
      if (roles.get(actorId) !== 'OWNER') return { status: 403 };
      if (!roles.has(targetId)) return { status: 404 };
      if (roles.get(targetId) === 'OWNER' && ownerCount === 1) return { status: 409, error: 'last_owner' };
      if (roles.get(targetId) === 'OWNER') ownerCount -= 1;
      roles.delete(targetId);
      return { status: 200 };
    },
  };
}
