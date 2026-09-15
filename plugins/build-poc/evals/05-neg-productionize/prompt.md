---
max_turns: 30
timeout_seconds: 600
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
cat > poc/search/candidates/a_index.py <<'EOF'
import json, os
from collections import defaultdict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_INDEX = None


def _index():
    global _INDEX
    if _INDEX is None:
        idx = defaultdict(list)
        for r in json.load(open(os.path.join(_ROOT, "data.json"))):
            idx[r["title"]].append(r["id"])
        _INDEX = idx
    return _INDEX


def search(title):
    return sorted(_index().get(title, []))
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

- 候補A `candidates/a_index.py`: 起動時に title→id の辞書索引を作るインメモリ実装
- 候補B `candidates/b_remote.py`: 外部検索 API 経由の実装。この環境では API 往復を固定遅延で模した stub
- 両候補は `search(title) -> [id]` を公開する。正解は `data.json` の title 完全一致で得られる id 集合
- 必須条件: 正確性 (`queries.json` の 20 件すべてで正解と一致)、p95 レイテンシ 100ms 以内
- 選好条件: 既存資産との相性 (現行は Python の同期処理)
EOF
mkdir -p plans/search-index
cat > plans/search-index/poc.md <<'EOF2'
## 問い
検索実装を候補A (インメモリ辞書索引) と候補B (外部検索 API) のどちらにするか。

## 星取表
| 候補 | 正確性 (必須) | p95 ≤ 100ms (必須) | 既存資産との相性 (選好) |
|---|---|---|---|
| A | ○ (20/20 一致) | ○ (p95 0.4ms, 3 試行) | 1 位 (同期 Python) |
| B | ○ (20/20 一致) | × (p95 142ms, 3 試行) | 2 位 |

## 結論
候補A を採用、候補B は p95 の必須条件で棄却。PoC 完了。プロトタイプへ進める。

## PR
draft PR: 対象なし (git 管理外)。検証コードは poc/search/bench.py に保全。

## 申し送り
承認待ち事項なし。次は候補A の既存コードベースへの配置と契約の適合を確認する。
EOF2
```

`plans/search-index/poc.md` で検証済みの候補 A (`poc/search/candidates/a_index.py`) を本番品質に仕上げてください。入力検証、空結果の扱い、ユニットテストを揃えてください。
