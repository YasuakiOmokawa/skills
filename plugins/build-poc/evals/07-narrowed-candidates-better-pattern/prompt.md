---
max_turns: 50
timeout_seconds: 1200
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。
```bash
mkdir -p poc/search/candidates
python3 - <<'PY'
import json, random
random.seed(7)
words = ["alpha","bravo","charlie","delta","echo","foxtrot","golf","hotel","india","juliet","kilo","lima","mike","november","oscar","papa"]
recs = [{"id": i, "title": " ".join(random.choice(words) for _ in range(3))} for i in range(10000)]
json.dump(recs, open("poc/search/data.json", "w"))
json.dump([recs[i]["title"] for i in random.sample(range(10000), 20)], open("poc/search/queries.json", "w"))
PY
cat > poc/search/candidates/a_scan.py <<'EOF'
import json, os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def search(title):
    with open(os.path.join(_ROOT, "data.json")) as f:
        data = json.load(f)
    return sorted(r["id"] for r in data if r["title"] == title)
EOF
cat > poc/search/candidates/b_remote.py <<'EOF'
import json, os, time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = None
_API_ROUND_TRIP_SEC = 0.14


def search(title):
    global _DATA
    if _DATA is None:
        _DATA = json.load(open(os.path.join(_ROOT, "data.json")))
    time.sleep(_API_ROUND_TRIP_SEC)
    return sorted(r["id"] for r in _DATA if r["title"] == title)
EOF
cat > poc/search/README.md <<'EOF'
# 検索候補

- 候補A `candidates/a_scan.py`: 呼び出しごとに data.json を読み込んで線形走査する実装
- 候補B `candidates/b_remote.py`: 外部検索 API 経由の実装。この環境では API 往復を固定遅延で模した stub
- 両候補は `search(title) -> [id]` を公開する。正解は `data.json` の title 完全一致で得られる id 集合
- 必須条件: 正確性 (`queries.json` の 20 件すべてで正解と一致)、p95 レイテンシ 100ms 以内
- 選好条件 (優先順): 1. レイテンシ (低いほど良い)、2. 既存資産との相性 (現行は Python の同期処理)
EOF
```

検索の実装を A と B のどちらにするか決めたいので、技術選定の PoC をしてください。条件は `poc/search/README.md` にあります。結果の出力先は `plans`、案件 slug は `search-choice` にしてください。検証コードは `poc/search/` の下に置いてよいです。この作業ディレクトリの外は変更しないでください。
