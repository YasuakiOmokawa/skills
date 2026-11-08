import importlib.util
import io
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins" / "define-done" / "skills" / "define-done" / "scripts" / "check_seal.py"

spec = importlib.util.spec_from_file_location("check_seal", SCRIPT)
check_seal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_seal)

SEAL_MESSAGE = "test: plan.md の受け入れテスト\n\nDefine-Done-Seal: AC-001\nDefine-Done-Test-Command: node --test test/a.test.js\n"
FAILING_TEST = "import { test } from 'node:test';\nimport assert from 'node:assert/strict';\nimport { f } from '../src/a.js';\ntest('AC-001 f returns 1', () => assert.equal(f(), 1));\n"


class Repo:
    def __init__(self, root):
        self.root = root
        self.git("init", "-q", "--template=", "-b", "main", ".")
        self.git("config", "user.email", "dev@example.com")
        self.git("config", "user.name", "dev")
        self.git("config", "commit.gpgsign", "false")
        self.write("package.json", '{"type": "module"}\n')
        self.write("src/a.js", "export const f = () => 0;\n")
        self.commit("base")

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.root), "-c", "core.hooksPath=/dev/null", *args], check=True, capture_output=True)

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def commit(self, message, *paths):
        self.git("add", *(paths or ["-A"]))
        self.git("commit", "-q", "-m", message)

    def seal(self):
        self.write("test/a.test.js", FAILING_TEST)
        self.write("plan.md", "# plan\n")
        self.commit(SEAL_MESSAGE, "test/a.test.js", "plan.md")


def run(*argv):
    out = io.StringIO()
    with redirect_stdout(out):
        code = check_seal.main(list(argv))
    return code, out.getvalue()


class CheckSealTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Repo(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_seal_fails(self):
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 1)
        self.assertIn("seal:", out)

    def test_seal_reports_protected_files_and_command(self):
        self.repo.seal()
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 0, out)
        self.assertIn("acs: AC-001", out)
        self.assertIn("test-command: node --test test/a.test.js", out)
        self.assertIn("protected: plan.md, test/a.test.js", out)

    def test_implementation_commit_keeps_seal_valid(self):
        self.repo.seal()
        self.repo.write("src/a.js", "export const f = () => 1;\n")
        self.repo.commit("impl")
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 0, out)

    def test_committed_test_change_after_seal_is_tamper(self):
        self.repo.seal()
        self.repo.write("test/a.test.js", FAILING_TEST.replace("f(), 1", "f(), 0"))
        self.repo.commit("weaken")
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 1)
        self.assertIn("tamper:", out)
        self.assertIn("test/a.test.js", out)

    def test_uncommitted_plan_change_is_tamper(self):
        self.repo.seal()
        self.repo.write("plan.md", "# plan\nchanged\n")
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 1)
        self.assertIn("未 commit", out)

    def test_deleted_test_is_tamper(self):
        self.repo.seal()
        self.repo.git("rm", "-q", "test/a.test.js")
        self.repo.git("commit", "-q", "-m", "drop")
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 1)
        self.assertIn("tamper:", out)

    def test_reseal_by_define_done_is_accepted(self):
        self.repo.seal()
        self.repo.write("test/a.test.js", FAILING_TEST.replace("returns 1", "returns one"))
        self.repo.commit(SEAL_MESSAGE, "test/a.test.js")
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 0, out)

    def test_reseal_clears_tamper_before_it(self):
        self.repo.seal()
        self.repo.write("test/a.test.js", FAILING_TEST.replace("f(), 1", "f(), 0"))
        self.repo.commit("impl edits the sealed test")
        self.repo.write("test/a.test.js", FAILING_TEST.replace("returns 1", "returns one"))
        self.repo.commit(SEAL_MESSAGE, "test/a.test.js")
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 0, out)

    def test_reseal_of_one_file_keeps_tamper_on_another(self):
        self.repo.seal()
        self.repo.write("plan.md", "# plan changed\n")
        self.repo.commit("impl edits the sealed plan")
        self.repo.write("test/a.test.js", FAILING_TEST.replace("returns 1", "returns one"))
        self.repo.commit(SEAL_MESSAGE, "test/a.test.js")
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 1)
        self.assertIn("tamper:", out)

    def test_last_line_states_exit_code(self):
        code, out = run("check", self.tmp.name)
        self.assertEqual(out.strip().splitlines()[-1], f"exit: {code}")

    def test_supersede_seal_keeps_verify_on_the_behavior_seal(self):
        self.repo.seal()
        self.repo.write("src/a.js", "export const f = () => 1;\n")
        self.repo.commit("impl")
        self.repo.write("test/a.test.js", FAILING_TEST.replace("returns 1", "returns one"))
        self.repo.commit("test: plan.md の AC-001 を置き換える\n\nDefine-Done-Supersedes: AC-001\n", "test/a.test.js")
        code, out = run("verify", self.tmp.name)
        self.assertEqual(code, 0, out)
        self.assertIn("sealed-exit: 1", out)

    def test_supersede_seal_is_not_tamper(self):
        self.repo.seal()
        self.repo.write("test/a.test.js", FAILING_TEST.replace("returns 1", "returns one"))
        self.repo.commit("test: replace\n\nDefine-Done-Supersedes: AC-001\n", "test/a.test.js")
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 0, out)

    def test_supersede_seal_protects_the_files_it_rewrote(self):
        self.repo.seal()
        self.repo.write("test/a.test.js", FAILING_TEST.replace("returns 1", "returns one"))
        self.repo.commit("test: replace\n\nDefine-Done-Supersedes: AC-001\n", "test/a.test.js")
        self.repo.write("test/a.test.js", FAILING_TEST.replace("f(), 1", "f(), 0"))
        self.repo.commit("impl edits the test")
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 1)
        self.assertIn("tamper:", out)

    def test_seal_without_command_trailer_fails(self):
        self.repo.write("test/a.test.js", FAILING_TEST)
        self.repo.commit("test: x\n\nDefine-Done-Seal: AC-001\n", "test/a.test.js")
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 1)
        self.assertIn("Define-Done-Test-Command", out)

    def test_verify_passes_when_sealed_red_turns_green(self):
        self.repo.seal()
        self.repo.write("src/a.js", "export const f = () => 1;\n")
        self.repo.commit("impl")
        code, out = run("verify", self.tmp.name)
        self.assertEqual(code, 0, out)
        self.assertIn("sealed-exit: 1", out)
        self.assertIn("current-exit: 0", out)

    def test_verify_fails_while_acceptance_tests_are_red(self):
        self.repo.seal()
        code, out = run("verify", self.tmp.name)
        self.assertEqual(code, 1)
        self.assertIn("fail:", out)

    def test_verify_fails_on_tests_green_at_seal(self):
        self.repo.write("src/a.js", "export const f = () => 1;\n")
        self.repo.commit("already")
        self.repo.seal()
        code, out = run("verify", self.tmp.name)
        self.assertEqual(code, 1)
        self.assertIn("vacuous:", out)

    def test_verify_fails_on_tamper_without_running_tests(self):
        self.repo.seal()
        self.repo.write("test/a.test.js", FAILING_TEST.replace("f(), 1", "f(), 0"))
        code, out = run("verify", self.tmp.name)
        self.assertEqual(code, 1)
        self.assertIn("tamper:", out)
        self.assertNotIn("current-exit", out)

if __name__ == "__main__":
    unittest.main()
