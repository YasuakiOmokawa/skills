export function createReset() {
  return {
    request() { throw new Error('not implemented'); },
    resend() { throw new Error('not implemented'); },
    consume() { throw new Error('not implemented'); },
  };
}
