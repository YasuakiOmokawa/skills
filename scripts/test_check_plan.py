import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_COPIES = [
    ROOT / "plugins" / name / "skills" / name / "scripts" / "check_plan.py"
    for name in ("define-done", "implement-plan", "verify-plan")
]
SCRIPT = SCRIPT_COPIES[0]
FORBIDDEN_ORACLE = "check_plan.py の禁止の検査が通り、Violation sample を入れると落ち、除くと通る"


def behavior(ac_id, text, sources="R-1"):
    return {"id": ac_id, "kind": "振る舞い", "text": text, "sources": sources}


def forbidden(ac_id, text, pattern, pathspec, sample, sources="R-1", oracle=FORBIDDEN_ORACLE):
    return {
        "id": ac_id,
        "kind": "禁止",
        "text": text,
        "sources": sources,
        "row": json.dumps({"pattern": pattern, "pathspec": pathspec}, ensure_ascii=False),
        "sample": sample,
        "oracle": oracle,
    }


def build_plan(acs, requirements=None, preamble="", mece_rows=()):
    requirements = requirements or [
        "- R-1: runbook に secret を回した時の扱いを書く (「secret を回した時の扱いを runbook に書いてほしい」 依頼)"
    ]
    ids = ", ".join(sorted(ac["id"] for ac in acs))
    lines = ["# 計画", "", "## 目的", "secret を回した時の扱いを決める。", "", preamble, "", "## Requirements"]
    lines += requirements
    lines += ["", "## Ground Review", "- 境界の適合: 無い", "", "## Acceptance Criteria"]
    lines += [f"- {ac['id']}: [{ac['kind']}] {ac['text']} (出典: {ac['sources']})" for ac in acs]
    lines += ["", "## MECE Review", f"- AC IDs: {ids}", "- Gate: ready", ""]
    lines += list(mece_rows)
    lines += ["", "## Verification Plan", f"- AC IDs: {ids}", ""]
    for ac in acs:
        lines += [f"### {ac['id']}"]
        if ac["kind"] == "禁止":
            lines += [
                f"- Oracle: {ac['oracle']}",
                "- Evidence anchors: 無い",
                "- Prerequisites: 無い",
                "- Required effects: 無い",
                f"- Violation sample: {ac['sample']}",
                f"- Forbidden row: {ac['row']}",
            ]
        else:
            lines += [
                "- Oracle: docs/runbook.md に AUTH_SERVICE_KEY の節がある",
                "- Evidence anchors: docs/runbook.md",
                "- Prerequisites: 無い",
                "- Required effects: 無い",
            ]
        lines += [""]
    return "\n".join(lines)


RUNBOOK_AC = behavior(
    "AC-025",
    "docs/runbook/staging.md が Secrets Store の AUTH_SERVICE_KEY を回す時の扱いを書く",
)


class Workspace:
    def __init__(self, files=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "--template=", "-b", "main")
        for path, content in {"README.md": "repo\n", **(files or {})}.items():
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        self.git("add", "-A")
        self.git("-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "init")
        self.plan = Path(self.tmp.name) / "plan.md"

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

    def write_plan(self, text, inside_repo=False):
        if inside_repo:
            self.plan = self.repo / "plans" / "plan.md"
            self.plan.parent.mkdir(exist_ok=True)
        self.plan.write_text(text)

    def run(self, command, *extra, script=SCRIPT):
        result = subprocess.run(
            [sys.executable, str(script), command, str(self.plan), str(self.repo), *extra],
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout

    def close(self):
        self.tmp.cleanup()


class CheckPlanTest(unittest.TestCase):
    def workspace(self, files=None):
        ws = Workspace(files)
        self.addCleanup(ws.close)
        return ws

    def sealed(self, text, files=None, inside_repo=False):
        ws = self.workspace(files)
        ws.write_plan(text, inside_repo)
        code, out = ws.run("seal")
        self.assertEqual(0, code, out)
        return ws

    def assertFailsWith(self, check_name, result):
        code, out = result
        self.assertEqual(1, code, out)
        self.assertTrue(any(line.startswith(f"{check_name}: ") for line in out.splitlines()), out)

    def test_決定の_ID_を出典にした_AC_を落とす(self):
        ws = self.workspace()
        ws.write_plan(build_plan([behavior("AC-025", RUNBOOK_AC["text"], sources="D4")]))
        self.assertFailsWith("source", ws.run("seal"))

    def test_要求を出典にした文書の_AC_を通す(self):
        ws = self.sealed(build_plan([RUNBOOK_AC]))
        self.assertEqual((0, ""), ws.run("check"))

    def test_出典の無い_AC_を落とす(self):
        ws = self.workspace()
        text = build_plan([RUNBOOK_AC]).replace(" (出典: R-1)", "")
        ws.write_plan(text)
        code, out = ws.run("seal")
        self.assertEqual(1, code)
        self.assertRegex(out, r"^(format|source): ")

    def test_base_の_tree_に無い_path_の出典を落とす(self):
        ws = self.workspace()
        ws.write_plan(build_plan([behavior("AC-001", "テスト", sources="infra/__tests__/iac-boundaries.test.ts")]))
        self.assertFailsWith("source", ws.run("seal"))

    def test_base_の_tree_にある既存の保証を出典にした_AC_を通す(self):
        self.sealed(
            build_plan([RUNBOOK_AC, behavior("AC-026", "境界の試験が通る", sources="test/boundary.test.ts")]),
            files={"test/boundary.test.ts": "test\n"},
        )

    def test_原文に無い引用の要求を落とす(self):
        ws = self.workspace({"docs/spec.md": "回した secret は staging に反映される。\n"})
        ws.write_plan(
            build_plan(
                [RUNBOOK_AC],
                requirements=["- R-1: 反映される (「回したら job を re-run する」 docs/spec.md)"],
            )
        )
        self.assertFailsWith("source", ws.run("seal"))

    def test_原文どおりの引用の要求を通す(self):
        self.sealed(
            build_plan(
                [RUNBOOK_AC],
                requirements=["- R-1: 反映される (「回した secret は staging に反映される。」 docs/spec.md)"],
            ),
            files={"docs/spec.md": "回した secret は\n  staging に反映される。\n"},
        )

    def test_計画の目的の節からの引用を通す(self):
        self.sealed(
            build_plan(
                [RUNBOOK_AC],
                requirements=["- R-1: 扱いを決める (「secret を回した時の扱いを決める。」 計画:目的)"],
            )
        )

    def test_計画が管理する節からの引用を落とす(self):
        ws = self.workspace()
        ws.write_plan(
            build_plan(
                [RUNBOOK_AC],
                requirements=["- R-1: 境界 (「境界の適合: 無い」 計画:Ground Review)"],
            )
        )
        self.assertFailsWith("source", ws.run("seal"))

    def test_どの_AC_も出典に挙げない要求を落とす(self):
        ws = self.workspace()
        reqs = [
            "- R-1: 扱いを書く (「扱いを書く」 依頼)",
            "- R-3: 速く軽く安全にする (「速く軽く安全に」 依頼)",
        ]
        ws.write_plan(build_plan([RUNBOOK_AC], requirements=reqs))
        self.assertFailsWith("coverage", ws.run("seal"))

    def test_範囲外にした要求を落とす(self):
        ws = self.workspace()
        reqs = [
            "- R-1: 扱いを書く (「扱いを書く」 依頼)",
            "- R-3: 速く軽く安全にする (「速く軽く安全に」 依頼)",
        ]
        ws.write_plan(build_plan([RUNBOOK_AC], requirements=reqs, mece_rows=["| R-3 | 範囲外: 計画が扱わない |"]))
        self.assertFailsWith("coverage", ws.run("seal"))
        self.assertFailsWith("coverage", ws.run("check"))

    def test_観測できない要求を表に書けば網羅を通す(self):
        reqs = [
            "- R-1: 扱いを書く (「扱いを書く」 依頼)",
            "- R-3: 速く軽く安全にする (「速く軽く安全に」 依頼)",
        ]
        ws = self.sealed(
            build_plan([RUNBOOK_AC], requirements=reqs, mece_rows=["| R-3 | 未検証: 観測できない |"])
        )
        code, out = ws.run("check")
        self.assertEqual(0, code, out)
        self.assertIn("coverage: R-3: 未検証: 観測できない", out)

    def test_決定から要求への表に無い決定を落とす(self):
        ws = self.workspace()
        ws.write_plan(build_plan([RUNBOOK_AC], preamble="| D12 | 値を回す |"))
        self.assertFailsWith("coverage", ws.run("seal"))

    def test_決定から要求への表にある決定を通す(self):
        ws = self.sealed(
            build_plan(
                [RUNBOOK_AC],
                preamble="| D12 | 値を回す |\n| D13 | 範囲を広げる |",
                mece_rows=["| D12 | R-1 |", "| D13 | 範囲外 |"],
            )
        )
        code, out = ws.run("check")
        self.assertEqual(0, code, out)
        self.assertIn("coverage: D13: 範囲外", out)

    def test_検索のコマンドを書いた禁止の_oracle_を落とす(self):
        ws = self.workspace()
        ac = forbidden(
            "AC-016",
            "旧名 staging-bundle を書かない",
            "staging-bundle",
            ["."],
            "`src/sample.ts` に `staging-bundle`",
            oracle="`git grep --untracked -n -E 'staging-bundle' -- .` が 0 行",
        )
        ws.write_plan(build_plan([ac]))
        self.assertFailsWith("format", ws.run("seal"))

    def test_読めない禁止の行を落とす(self):
        ws = self.workspace()
        ac = forbidden("AC-016", "旧名を書かない", "old", ["."], "`src/x.ts` に `old`")
        ac["row"] = json.dumps({"pattern": "old", "pathspec": ["."], "reason": "旧名"})
        ws.write_plan(build_plan([ac]))
        self.assertFailsWith("format", ws.run("seal"))
        ac["row"] = "{pattern: old}"
        ws.write_plan(build_plan([ac]))
        self.assertFailsWith("format", ws.run("seal"))

    def test_負の_pathspec_を持つ禁止の行を落とす(self):
        ws = self.workspace()
        for negative in (":!infra/__tests__", ":^infra", ":(exclude)infra"):
            ac = forbidden("AC-016", "旧名を書かない", "old", [".", negative], "`src/x.ts` に `old`")
            ws.write_plan(build_plan([ac]))
            self.assertFailsWith("format", ws.run("seal"))

    def test_見本に当たらない禁止の行を落とす(self):
        ws = self.workspace()
        ac = forbidden("AC-016", "旧名を書かない", "staging-bundle", ["."], "`src/x.ts` に `something-else`")
        ws.write_plan(build_plan([ac]))
        self.assertFailsWith("forbidden", ws.run("seal"))

    def test_範囲の外に置いた見本の禁止を落とす(self):
        ws = self.workspace()
        ac = forbidden("AC-016", "旧名を書かない", "staging-bundle", ["src"], "`docs/x.md` に `staging-bundle`")
        ws.write_plan(build_plan([ac]))
        self.assertFailsWith("forbidden", ws.run("seal"))

    def rename_plan(self):
        return build_plan(
            [forbidden("AC-016", "旧名 staging-bundle を書かない", "staging-bundle", ["."], "`src/sample.ts` に `import \"staging-bundle\"`")]
        )

    def test_変更前に旧名が残る_repo_で_seal_が通る(self):
        ws = self.sealed(self.rename_plan(), files={"src/app.ts": 'import "staging-bundle"\n'})
        self.assertEqual(0, ws.run("check")[0])
        self.assertEqual(1, ws.run("check-green")[0])

    def test_実装の後は見本なしで当たる禁止を落とす(self):
        ws = self.sealed(self.rename_plan(), files={"src/app.ts": 'import "staging-bundle"\n'})
        self.assertFailsWith("forbidden", ws.run("check-green"))

    def test_旧名を消した後は実装の後の確認が通る(self):
        ws = self.sealed(self.rename_plan(), files={"src/app.ts": 'import "staging-bundle"\n'})
        (ws.repo / "src" / "app.ts").write_text('import "bundle"\n')
        self.assertEqual((0, ""), ws.run("check-green"))

    def test_repo_の中の計画は走査から外れる(self):
        ws = self.sealed(self.rename_plan(), inside_repo=True)
        self.assertEqual((0, ""), ws.run("check-green"))

    def test_見本を入れた既存の_file_が元に戻る(self):
        content = "export const a = 1;"
        ws = self.workspace({"src/app.ts": content})
        before = hashlib.sha256((ws.repo / "src" / "app.ts").read_bytes()).hexdigest()
        ws.write_plan(
            build_plan([forbidden("AC-016", "旧名を書かない", "staging-bundle", ["src"], "`src/app.ts` に `staging-bundle`")])
        )
        self.assertEqual(0, ws.run("seal")[0])
        self.assertEqual(0, ws.run("check-green")[0])
        self.assertEqual(before, hashlib.sha256((ws.repo / "src" / "app.ts").read_bytes()).hexdigest())

    def test_見本で作った_file_と_dir_が残らない(self):
        ws = self.workspace()
        ws.write_plan(
            build_plan([forbidden("AC-016", "旧名を書かない", "staging-bundle", ["."], "`newdir/sub/x.ts` に `staging-bundle`")])
        )
        self.assertEqual(0, ws.run("seal")[0])
        self.assertFalse((ws.repo / "newdir").exists())

    def test_書いた後に変わった_AC_を封が拾う(self):
        ws = self.sealed(build_plan([RUNBOOK_AC]))
        ws.plan.write_text(ws.plan.read_text().replace("扱いを書く (出典", "扱いを書け (出典"))
        self.assertFailsWith("seal", ws.run("check"))

    def test_書いた後に緩めた禁止の行を封が拾う(self):
        ws = self.sealed(self.rename_plan())
        ws.plan.write_text(ws.plan.read_text().replace('"pattern": "staging-bundle"', '"pattern": "staging-bundle$"'))
        self.assertFailsWith("seal", ws.run("check"))

    def test_書いた後に変わった要求を封が拾う(self):
        ws = self.sealed(build_plan([RUNBOOK_AC]))
        ws.plan.write_text(ws.plan.read_text().replace("扱いを書く (「", "扱いを書き直す (「"))
        self.assertFailsWith("seal", ws.run("check"))

    def test_封の無い計画を落とす(self):
        ws = self.workspace()
        ws.write_plan(build_plan([RUNBOOK_AC]))
        self.assertFailsWith("seal", ws.run("check"))

    def test_封を書き直しても計画のほかの行は変わらない(self):
        ws = self.sealed(build_plan([RUNBOOK_AC]))
        first = ws.plan.read_text()
        self.assertEqual(0, ws.run("seal")[0])
        self.assertEqual(first, ws.plan.read_text())
        self.assertEqual(1, first.count("- Fingerprint: "))

    def test_Gate_が_ready_でない計画を落とす(self):
        ws = self.workspace()
        ws.write_plan(build_plan([RUNBOOK_AC]).replace("- Gate: ready", "- Gate: blocked (欠落あり)"))
        self.assertFailsWith("format", ws.run("seal"))

    def test_節が重複した計画を落とす(self):
        ws = self.workspace()
        ws.write_plan(build_plan([RUNBOOK_AC]) + "\n## Requirements\n")
        self.assertFailsWith("format", ws.run("seal"))

    def test_検証の対応付けに無い_AC_を落とす(self):
        ws = self.workspace()
        text = build_plan([RUNBOOK_AC, behavior("AC-026", "別の扱い")])
        text = text.split("### AC-026")[0]
        ws.write_plan(text)
        self.assertFailsWith("format", ws.run("seal"))

    def test_3_つの_plugin_の_script_が同じ(self):
        contents = {path.read_bytes() for path in SCRIPT_COPIES}
        self.assertEqual(1, len(contents))


PLAN_SECTIONS = frozenset({"Requirements", "Ground Review", "Acceptance Criteria", "MECE Review", "Verification Plan"})
SEALED_SECTIONS = frozenset({"Requirements", "Acceptance Criteria", "Verification Plan"})
PHASES = ("draft", "sealed", "implementing", "verifying", "done")

PROTOCOL = {
    "writable": {
        ("define-done", "draft"): PLAN_SECTIONS,
        ("implement-plan", "implementing"): frozenset({"product", "tests"}),
    },
    "moves": [
        {"actor": "define-done", "op": "seal", "from": {"draft"}, "to": "sealed"},
        {"actor": "define-done", "op": "redo", "from": {"sealed", "implementing", "verifying", "done"}, "to": "draft", "needs_user_request": True},
        {"actor": "implement-plan", "op": "start", "from": {"sealed"}, "to": "implementing", "needs_check": True},
        {"actor": "verify-plan", "op": "start", "from": {"implementing"}, "to": "verifying", "needs_check": True},
        {"actor": "verify-plan", "op": "pass", "from": {"verifying"}, "to": "done"},
    ],
}


def edges(protocol, state):
    phase, user_request, check_ok, sealed_once, by_redo = state
    if not user_request:
        yield "user", "request_redo", frozenset(), (phase, True, check_ok, sealed_once, by_redo)
    if check_ok and phase != "draft":
        yield "environment", "drift", frozenset(), (phase, user_request, False, sealed_once, by_redo)
    for (actor, writable_phase), targets in protocol["writable"].items():
        if writable_phase == phase:
            for target in targets:
                yield actor, "write", frozenset({target}), state
    for move in protocol["moves"]:
        if phase not in move["from"]:
            continue
        if move.get("needs_user_request") and not user_request:
            continue
        if move.get("needs_check") and not check_ok:
            continue
        if move["op"] == "seal":
            yield move["actor"], "seal", frozenset(), (move["to"], user_request, True, True, False)
        elif move["op"] == "redo":
            yield move["actor"], "redo", frozenset(), (move["to"], False, check_ok, sealed_once, user_request)
        else:
            yield move["actor"], move["op"], frozenset(), (move["to"], user_request, check_ok, sealed_once, by_redo)


def reachable_edges(protocol):
    start = ("draft", False, True, False, False)
    seen = {start}
    queue = deque([start])
    found = []
    while queue:
        state = queue.popleft()
        for actor, op, writes, nxt in edges(protocol, state):
            found.append((state, actor, op, writes, nxt))
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return found


def property_violations(protocol):
    violations = []
    for state, actor, op, writes, _ in reachable_edges(protocol):
        phase, _, check_ok, sealed_once, by_redo = state
        if writes & SEALED_SECTIONS and sealed_once and not (actor == "define-done" and phase == "draft" and by_redo):
            violations.append(("封の後の書き込みが user_request を経た redo の後でない", state, actor, op))
        if op == "start" and not check_ok:
            violations.append(("check が落ちた状態からの start", state, actor, op))
        if actor == "verify-plan" and writes & PLAN_SECTIONS:
            violations.append(("verify-plan が計画に書く", state, actor, op))
    return violations


class ProtocolTest(unittest.TestCase):
    def test_約束事の表から到達する全状態で_3_つの性質が成り立つ(self):
        self.assertTrue(reachable_edges(PROTOCOL))
        self.assertEqual([], property_violations(PROTOCOL))

    def test_全ての段階に到達する(self):
        reached = {edge[4][0] for edge in reachable_edges(PROTOCOL)}
        self.assertEqual(set(PHASES), reached)

    def test_verify_plan_に_AC_を書かせた表では性質が落ちる(self):
        broken = {
            "writable": {**PROTOCOL["writable"], ("verify-plan", "verifying"): frozenset({"Acceptance Criteria"})},
            "moves": PROTOCOL["moves"],
        }
        reasons = {violation[0] for violation in property_violations(broken)}
        self.assertIn("verify-plan が計画に書く", reasons)
        self.assertIn("封の後の書き込みが user_request を経た redo の後でない", reasons)

    def test_利用者の依頼なしに_redo_できる表では性質が落ちる(self):
        moves = [dict(move) for move in PROTOCOL["moves"]]
        for move in moves:
            move.pop("needs_user_request", None)
        broken = {"writable": PROTOCOL["writable"], "moves": moves}
        self.assertTrue(property_violations(broken))

    def test_check_を見ずに_start_できる表では性質が落ちる(self):
        moves = [dict(move) for move in PROTOCOL["moves"]]
        for move in moves:
            move.pop("needs_check", None)
        broken = {"writable": PROTOCOL["writable"], "moves": moves}
        reasons = {violation[0] for violation in property_violations(broken)}
        self.assertIn("check が落ちた状態からの start", reasons)


if __name__ == "__main__":
    unittest.main()
