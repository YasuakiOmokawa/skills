---
type: regex
target: trace
match: contains
flags: s
---
(?:"name":"(?:Write|Edit)","input":\{"file_path":"[^"]*/test/[^"]*","(?:content|old_string|new_string)":"|"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?(?:cat|tee) [^"\\]*?>(?:[^"\\]|\\.)*?test/)(?:[^"\\]|\\.)*?(?:resetRateLimits\(|\b(?!203\.0\.113\.9\b|198\.51\.100\.7\b)\d{1,3}\.\d{1,3}\.\d{1,3}\.(?:\d{1,3}\b|\$\{))
