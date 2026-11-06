const TTL_MS = 30 * 60 * 1000;

export function createReset({ users, mailer, now }) {
  const tokens = new Map();
  let seq = 0;
  const resends = new Map();
  function issue(email) {
    if (users.has(email)) {
      seq += 1;
      const token = `t${seq}`;
      tokens.set(token, { email, issuedAt: now(), used: false });
      mailer.send(email, token);
    }
    return { screen: 'accepted' };
  }
  return {
    request: issue,
    resend(email) {
      const count = (resends.get(email) ?? 0) + 1;
      resends.set(email, count);
      if (count > 3) return { screen: 'accepted' };
      return issue(email);
    },
    consume(token, newPassword) {
      const entry = tokens.get(token);
      if (!entry) return { screen: 'expired' };
      if (entry.used) return { screen: 'used' };
      if (now() - entry.issuedAt >= TTL_MS) return { screen: 'expired' };
      entry.used = true;
      users.get(entry.email).password = newPassword;
      return { screen: 'done' };
    },
  };
}
