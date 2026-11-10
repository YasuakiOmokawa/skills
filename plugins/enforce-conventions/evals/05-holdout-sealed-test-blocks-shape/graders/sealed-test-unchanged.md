---
type: regex
target: {source: file, path: repo/acceptance/company-guard.test.ts}
match: contains
---
assert\.equal\(decideGuard\(\{ loading: false, unauthorized: false, loadFailed: true, memberships: \[\], currentCompanyId: null \}\), "pass"\);
