const ROLE_LEVEL = { MEMBER: 0, ADMIN: 1, OWNER: 2 };

function isAtLeast(role, minRole) {
  return Object.hasOwn(ROLE_LEVEL, role) && ROLE_LEVEL[role] >= ROLE_LEVEL[minRole];
}

export function canChangeRole(actorRole, beforeRole, nextRole) {
  const touchesOwner = beforeRole === 'OWNER' || nextRole === 'OWNER';
  return touchesOwner ? actorRole === 'OWNER' : true;
}

export function createCompany({ ownerId }) {
  const roles = new Map([[ownerId, 'OWNER']]);
  return {
    roleOf(userId) {
      return roles.get(userId) ?? null;
    },
    changeRole(actorId, targetId, nextRole) {
      const actorRole = roles.get(actorId);
      if (!actorRole || !isAtLeast(actorRole, 'ADMIN')) return { status: 403 };
      if (!canChangeRole(actorRole, roles.get(targetId), nextRole)) return { status: 403 };
      roles.set(targetId, nextRole);
      return { status: 200 };
    },
    invite(actorId, role) {
      throw new Error('not implemented');
    },
    accept(invitationId, userId) {
      throw new Error('not implemented');
    },
  };
}
