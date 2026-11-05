import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.eval_coverage import coverage_errors, shipped_digest, tally

CASES = {"01-a", "02-b"}


class CoverageErrorsTest(unittest.TestCase):
    def test_skill_change_without_a_record_fails(self):
        errors = coverage_errors("sample", None, "d1", CASES)
        self.assertEqual(1, len(errors))
        self.assertIn("record an eval run", errors[0])

    def test_record_for_other_shipped_content_fails(self):
        record = {"shipped_sha256": "old", "cases": {"01-a": {}, "02-b": {}}, "waived": None}
        self.assertEqual(1, len(coverage_errors("sample", record, "new", CASES)))

    def test_record_missing_a_case_fails_and_names_it(self):
        record = {"shipped_sha256": "d1", "cases": {"01-a": {}}, "waived": None}
        errors = coverage_errors("sample", record, "d1", CASES)
        self.assertEqual(1, len(errors))
        self.assertIn("02-b", errors[0])

    def test_record_covering_every_case_passes(self):
        record = {"shipped_sha256": "d1", "cases": {"01-a": {}, "02-b": {}}, "waived": None}
        self.assertEqual([], coverage_errors("sample", record, "d1", CASES))

    def test_waiver_with_a_reason_passes_without_cases(self):
        record = {"shipped_sha256": "d1", "cases": {}, "waived": "typo の修正だけで振る舞いが変わらない"}
        self.assertEqual([], coverage_errors("sample", record, "d1", CASES))

    def test_empty_waiver_does_not_excuse_missing_cases(self):
        record = {"shipped_sha256": "d1", "cases": {}, "waived": "  "}
        self.assertEqual(1, len(coverage_errors("sample", record, "d1", CASES)))

    def test_waiver_for_other_shipped_content_fails(self):
        record = {"shipped_sha256": "old", "cases": {}, "waived": "理由"}
        self.assertEqual(1, len(coverage_errors("sample", record, "d1", CASES)))


class TallyTest(unittest.TestCase):
    def test_counts_with_arm_graders_per_case_and_later_results_win(self):
        first = {"cases": [{"name": "01-a", "arms": {"with": [{"graders": [{"passed": True}, {"passed": False}]}]}}]}
        second = {"cases": [{"name": "01-a", "arms": {"with": [{"graders": [{"passed": True}]}], "without": [{"graders": [{"passed": False}]}]}}]}
        self.assertEqual({"01-a": {"passed": 1, "total": 1}}, tally([first, second]))


class ShippedDigestTest(unittest.TestCase):
    def test_digest_follows_tracked_shipped_files_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", "--template=", "-b", "main", str(root)], check=True)
            (root / "skills" / "s").mkdir(parents=True)
            (root / "skills" / "s" / "SKILL.md").write_text("a\n")
            (root / "evals").mkdir()
            (root / "evals" / "outcomes.md").write_text("x\n")
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            before = shipped_digest(root)
            (root / "evals" / "outcomes.md").write_text("y\n")
            (root / "skills" / "s" / "untracked.md").write_text("z\n")
            self.assertEqual(before, shipped_digest(root))
            (root / "skills" / "s" / "SKILL.md").write_text("b\n")
            self.assertNotEqual(before, shipped_digest(root))


if __name__ == "__main__":
    unittest.main()
