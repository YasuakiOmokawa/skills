---
type: regex
target: last_message
match: contains
flags: i
weight: 0.5
---
destination existed:\s*\**\s*(yes|no|unverified)[\s\S]*requested update applied:\s*\**\s*(yes|no|unverified)[\s\S]*resulting content verified:\s*\**\s*(yes|no|unverified)
