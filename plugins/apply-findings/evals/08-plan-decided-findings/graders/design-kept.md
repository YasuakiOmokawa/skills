---
type: regex
target: {source: file, path: src/export.js}
match: contains
---
return toCsv\(await fetchInvoices\(\)\);
