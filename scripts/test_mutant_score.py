import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("mutant_score", ROOT / "scripts" / "eval" / "mutant_score.py")
mutant_score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mutant_score)


class AutoMutantsTest(unittest.TestCase):
    def ids(self, source):
        return [mutant_id.split("-")[0] for mutant_id, _ in mutant_score.auto_mutants(source)]

    def test_strings_and_comments_are_not_mutated(self):
        self.assertEqual(self.ids("const s = 'a < b' + `x ${1}`; // c > d\n/* e && f */\n"), ["arith"])

    def test_arrow_is_not_a_comparison(self):
        self.assertNotIn("swap", self.ids("const f = (a) => a;\n"))

    def test_each_operator_family_is_generated(self):
        source = "export function f(a, b) {\n  if (!a && b <= 10) return true;\n  total += a * 2;\n  log(a);\n  return a - b;\n}\n"
        self.assertEqual(
            sorted(set(self.ids(source))),
            ["arith", "bool", "dec", "delete", "inc", "not", "swap"],
        )

    def test_mutants_differ_from_source(self):
        source = "const x = a < 3 ? 1 : 0;\n"
        for _, mutated in mutant_score.auto_mutants(source):
            self.assertNotEqual(mutated, source)


class MutateTest(unittest.TestCase):
    def test_edits_apply_in_order_and_require_one_match(self):
        source = "a\nb\n"
        self.assertEqual(mutant_score.mutate(source, {"edits": [{"find": "a\n", "replace": "x\n"}, {"find": "b\n", "replace": "y\n"}]}), "x\ny\n")
        with self.assertRaises(ValueError):
            mutant_score.mutate(source, {"find": "z", "replace": "q"})


@unittest.skipUnless(shutil.which("node"), "node is required")
class ScoreTest(unittest.TestCase):
    def test_bulk_discount_hidden_tests_kill_every_requirement_mutant(self):
        subject = ROOT / "scripts" / "eval" / "mutant" / "bulk-discount"
        report = mutant_score.score(subject, subject, ["test/hidden.test.js"])
        self.assertEqual(report["reference_pass"], report["tests"])
        self.assertTrue(report["reference_repeatable"])
        self.assertEqual(report["killed"], report["mutant_total"])
        self.assertEqual(report["auto"]["killed"], report["auto"]["killable"])


@unittest.skipUnless(shutil.which("node"), "node is required")
class ScoreRunTest(unittest.TestCase):
    def trace(self, directory, events):
        path = Path(directory) / "trace.jsonl"
        path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n", encoding="utf-8")
        return {"tracePath": str(path)}

    def test_written_test_is_scored_and_gate_halt_is_classified(self):
        from scripts.eval import score_results
        hidden = (ROOT / "scripts/eval/mutant/bulk-discount/test/hidden.test.js").read_text(encoding="utf-8")
        mapping = {"subject": "scripts/eval/mutant/bulk-discount", "test": "test/bulk.acceptance.test.js"}
        with tempfile.TemporaryDirectory() as work:
            write = {"type": "tool_use", "id": "w1", "name": "Write", "input": {"file_path": "/x/repo/test/bulk.acceptance.test.js", "content": hidden}}
            run = self.trace(work, [{"type": "assistant", "message": {"content": [write]}}])
            scored = score_results.score_run(run, mapping, Path(work) / "restored")
            self.assertEqual((scored["outcome"], scored["valid"], scored["requirement_killed"]), ("tests", 7, 9))
            halted = self.trace(work, [{"type": "result", "result": "Gate は not ready なので止めました"}])
            self.assertEqual(score_results.score_run(halted, mapping, Path(work) / "r2")["outcome"], "gate")


if __name__ == "__main__":
    unittest.main()
