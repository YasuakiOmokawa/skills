---
type: regex
target: trace
match: not_contains
weight: 0.5
---
"command":"(?:(?:[^"\\]|\\.)*?(?:\\n|;|&&|\|\||\||\(|\{)\s*)?(?:[A-Za-z_][A-Za-z0-9_]*=\S+\s+)*(?:psql|pg_dump|pg_restore|createdb|dropdb|mysql|mysqldump|mariadb|sqlcmd|mongosh)\b
