const ROLE_LEVEL = { MEMBER: 0, ADMIN: 1, OWNER: 2 };

function isAtLeast(role, minRole) {
  return Object.hasOwn(ROLE_LEVEL, role) && ROLE_LEVEL[role] >= ROLE_LEVEL[minRole];
}

export function canChangeRole(actorRole, beforeRole, nextRole) {
  const touchesOwner = beforeRole === 'OWNER' || nextRole === 'OWNER';
  return touchesOwner ? actorRole === 'OWNER' : true;
}

function canInviteRole(actorRole, invitedRole) {
  return invitedRole === 'OWNER' ? actorRole === 'OWNER' : true;
}

export function createCompany({ ownerId }) {
  const roles = new Map([[ownerId, 'OWNER']]);
  const invitations = new Map();
  let seq = 0;
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
      const actorRole = roles.get(actorId);
      if (!actorRole || !isAtLeast(actorRole, 'ADMIN')) return { status: 403 };
      if (!canInviteRole(actorRole, role)) return { status: 403 };
      seq += 1;
      const invitationId = `inv${seq}`;
      invitations.set(invitationId, { role, used: false });
      return { status: 201, invitationId };
    },
    accept(invitationId, userId) {
      const invitation = invitations.get(invitationId);
      if (!invitation || invitation.used) return { status: 410 };
      invitation.used = true;
      roles.set(userId, invitation.role);
      return { status: 200 };
    },
  };
}
