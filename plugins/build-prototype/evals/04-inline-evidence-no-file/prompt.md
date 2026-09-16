---
max_turns: 50
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。
```bash
mkdir -p app/search/tests app/common poc/search_prefix plans/search-prefix
touch app/__init__.py app/search/__init__.py app/search/tests/__init__.py app/common/__init__.py poc/__init__.py poc/search_prefix/__init__.py
python3 - <<'PY'
import json, random
random.seed(7)
words = ["alpha","bravo","charlie","delta","echo","foxtrot","golf","hotel","india","juliet","kilo","lima","mike","november","oscar","papa"]
recs = [{"id": i, "title": " ".join(random.choice(words) for _ in range(3))} for i in range(10000)]
json.dump(recs, open("app/search/data.json", "w"))
PY
cat > app/README.md <<'EOF'
# app

層は handlers → service → store の一方向。永続化 (`store.py`) を呼ぶのは service だけで、handlers は service の戻り値を整形して返す。
文字列の正規化は `app/common/text.py` を使う。テストは `python3 -m unittest discover -s app -t .` で実行する。
EOF
cat > app/common/text.py <<'EOF'
def normalize(s):
    return s.strip().lower()
EOF
cat > app/search/store.py <<'EOF'
import json
import os

_DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")


class RecordStore:
    def __init__(self, path=_DATA_PATH):
        self._path = path
        self._records = None

    def all(self):
        if self._records is None:
            with open(self._path) as f:
                self._records = json.load(f)
        return self._records

    def find_by_title(self, title):
        return [r for r in self.all() if r["title"] == title]
EOF
cat > app/search/service.py <<'EOF'
from app.common.text import normalize
from app.search.store import RecordStore


class SearchService:
    def __init__(self, store=None):
        self._store = store or RecordStore()

    def search(self, query):
        q = normalize(query)
        if not q:
            return []
        return sorted(self._store.find_by_title(q), key=lambda r: r["id"])
EOF
cat > app/search/handlers.py <<'EOF'
from app.search.service import SearchService

_service = SearchService()


def handle_search(params):
    items = _service.search(params.get("q", ""))
    return {"items": items, "count": len(items)}
EOF
cat > app/search/tests/test_service.py <<'EOF'
import unittest

from app.search.service import SearchService


class StubStore:
    def __init__(self, records):
        self._records = records

    def all(self):
        return self._records

    def find_by_title(self, title):
        return [r for r in self._records if r["title"] == title]


RECORDS = [
    {"id": 3, "title": "alpha bravo"},
    {"id": 1, "title": "alpha bravo"},
    {"id": 2, "title": "alpha charlie"},
]


class SearchServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = SearchService(StubStore(RECORDS))

    def test_exact_match_sorted_by_id(self):
        self.assertEqual([1, 3], [r["id"] for r in self.service.search("alpha bravo")])

    def test_query_is_normalized(self):
        self.assertEqual([2], [r["id"] for r in self.service.search("  Alpha Charlie ")])

    def test_empty_query_returns_empty(self):
        self.assertEqual([], self.service.search("   "))

    def test_no_match_returns_empty(self):
        self.assertEqual([], self.service.search("zulu"))


if __name__ == "__main__":
    unittest.main()
EOF
cat > poc/search_prefix/prefix_index.py <<'EOF'
import bisect


class PrefixIndex:
    def __init__(self, records, limit=10):
        self._rows = sorted(((r["title"], r["id"]), r) for r in records)
        self._keys = [k[0] for k, _ in self._rows]
        self._limit = limit

    def search(self, query):
        q = query.strip().casefold()
        if not q:
            return []
        out = []
        for _, r in self._rows[bisect.bisect_left(self._keys, q):]:
            if not r["title"].startswith(q) or len(out) >= self._limit:
                break
            out.append(r)
        return out
EOF
```

`app/search` に前方一致検索を足すプロトタイプを書いてください。PoC 結果ファイルはありませんが、`poc/search_prefix/prefix_index.py` で次の振る舞いを実証済みで承認されています: (1) 入力は strip + casefold してから照合する (2) 前方一致した候補を title 昇順、同 title は id 昇順で返し、上限 10 件 (3) 一致なし・空入力は空リスト。編集してよいのは `app/search` 配下とそのテストです。この作業ディレクトリの外は変更しないでください。
