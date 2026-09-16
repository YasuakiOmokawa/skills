---
max_turns: 10
timeout_seconds: 300
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
請求の再試行機能、PoC とプロトタイプは終わっていて再試行 3 回・冪等キー方式で行くことは決まってる。うーん、この規模なら、設計して design document つくって 2 日、実装して 3 日、QA で 5 日くらいかな。妥当だと思う?
