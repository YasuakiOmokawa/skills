import importlib.util
import io
import json
import shutil
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


def run(*argv, stdin=""):
    out = io.StringIO()
    with redirect_stdout(out):
        code = check_seal.main(list(argv), stdin)
    return code, out.getvalue()


def plan_text(criteria, gate="ready", rows=None, ids=None, sources="R-1", requirements=("R-1",)):
    criteria = [(*criterion, sources)[:3] for criterion in criteria]
    listed = ", ".join(ac for ac, _, _ in criteria) if ids is None else ids
    table = rows if rows is not None else [f"| R-1 | {listed} |"]
    return "\n".join([
        "# plan",
        "",
        "## Requirements",
        "",
        *[f"- {requirement}: f は 1 を返す (「f は 1 を返す」 依頼)" for requirement in requirements],
        "",
        "## Ground Review",
        "",
        "無い",
        "",
        "## Acceptance Criteria",
        "",
        *[f"- {ac}: [{kind}] 振る舞い (出典: {cited})" for ac, kind, cited in criteria],
        "",
        "## MECE Review",
        "",
        f"- AC IDs: {listed}",
        f"- Gate: {gate}",
        "",
        "### 要求の表",
        "",
        "| 要求 | 対応 |",
        "|---|---|",
        *table,
        "",
    ])


PLAN = plan_text([("AC-001", "規則"), ("AC-002", "非影響")])


def seal_spec(command, rule=(), non_impact=(), tests=(), supersedes="", subject="", spike="", check_command="", plan=""):
    mapping = [{"ac": ac, "file": file, "name": name} for ac, file, name in tests]
    spec = {"test_command": command, "rule": list(rule), "non_impact": list(non_impact), "tests": mapping, "supersedes": supersedes}
    if subject:
        spec["subject"] = subject
    if plan:
        spec["plan"] = plan
    if spike:
        spec["spike"] = spike
    if check_command:
        spec["check_command"] = check_command
    return json.dumps(spec)


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

    def squash_merge_ending_with_seal_trailer(self):
        self.repo.write("src/a.js", "export const f = () => 1;\n")
        self.repo.write("test/a.test.js", FAILING_TEST.replace("returns 1", "returns one"))
        self.repo.commit("feat: f (#1)\n\n* impl\n\n* " + SEAL_MESSAGE)

    def test_squash_merge_ending_with_seal_trailer_does_not_protect_product_files(self):
        self.squash_merge_ending_with_seal_trailer()
        self.repo.seal()
        self.repo.write("src/a.js", "export const f = () => 2;\n")
        self.repo.commit("impl of the next issue")
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 0, out)
        self.assertIn("protected: plan.md, test/a.test.js\n", out)

    def test_squash_merge_alone_is_not_a_seal(self):
        self.squash_merge_ending_with_seal_trailer()
        code, out = run("check", self.tmp.name)
        self.assertEqual(code, 1)
        self.assertIn("seal:", out)

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

REPORT_COMMAND = "node --test --test-reporter=junit --test-reporter-destination={report} test/a.rule.test.js test/a.keep.test.js"
HARNESS = "export { f } from '../../src/a.js';\nexport { g } from '../../src/b.js';\nimport { readFileSync } from 'node:fs';\nexport const expected = (name) => readFileSync(new URL(`../golden/${name}`, import.meta.url), 'utf8');\n"
RULE_TEST = "import { test } from 'node:test';\nimport assert from 'node:assert/strict';\nimport { f } from './harness/app.js';\ntest('f returns 1', () => assert.equal(f(), 1));\n"
KEEP_TEST = "import { test } from 'node:test';\nimport assert from 'node:assert/strict';\nimport { g, expected } from './harness/app.js';\ntest('g keeps its text', () => assert.equal(g(), expected('g.txt')));\n"
RULE_FILES = ["test/a.rule.test.js"]
KEEP_FILES = ["test/a.keep.test.js", "test/golden/g.txt", "test/harness/app.js", "plan.md"]
TESTS = [("AC-001", "test/a.rule.test.js", "f returns 1"), ("AC-002", "test/a.keep.test.js", "g keeps its text")]


class SealCommandTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.repo = Repo(self.root)
        self.repo.write("src/b.js", "export const g = () => 'kept';\n")
        self.repo.commit("b")
        self.repo.write("test/harness/app.js", HARNESS)
        self.repo.write("test/golden/g.txt", "kept")
        self.repo.write("test/a.rule.test.js", RULE_TEST)
        self.repo.write("test/a.keep.test.js", KEEP_TEST)
        self.repo.write("plan.md", PLAN)

    def tearDown(self):
        self.tmp.cleanup()

    def seal(self, rule=RULE_FILES, keep=KEEP_FILES, tests=TESTS, command=REPORT_COMMAND, supersedes=""):
        return run("seal", str(self.root), stdin=seal_spec(command, rule, keep, tests, supersedes))

    def head(self):
        return subprocess.run(["git", "-C", str(self.root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

    def body(self):
        return subprocess.run(["git", "-C", str(self.root), "show", "-s", "--format=%B", "HEAD"], capture_output=True, text=True).stdout

    def implement(self):
        self.repo.write("src/a.js", "export const f = () => 1;\n")
        self.repo.commit("impl")

    def add_remote_and_push(self):
        remote = Path(self.tmp.name) / "remote.git"
        subprocess.run(["git", "init", "-q", "--bare", "--template=", str(remote)], check=True)
        self.repo.git("remote", "add", "origin", str(remote))
        self.repo.git("push", "-q", "origin", "main")

    def push(self):
        self.repo.git("push", "-q", "origin", "main")

    def test_seal_records_kinds_files_and_the_test_of_each_criterion(self):
        code, out = self.seal()
        self.assertEqual(code, 0, out)
        body = self.body()
        self.assertIn("Define-Done-Seal: AC-001, AC-002", body)
        self.assertIn("Define-Done-Rule: AC-001\n", body)
        self.assertIn("Define-Done-Rule-Files: test/a.rule.test.js\n", body)
        self.assertIn("Define-Done-Files: test/a.rule.test.js, test/a.keep.test.js, test/golden/g.txt, test/harness/app.js, plan.md", body)
        self.assertIn("Define-Done-Test: AC-001 = test/a.rule.test.js › f returns 1\n", body)
        self.assertIn("Define-Done-Test: AC-002 = test/a.keep.test.js › g keeps its text\n", body)
        code, out = run("check", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("rule: AC-001", out)

    def test_seal_leaves_no_report_file_in_the_repo(self):
        self.seal()
        self.assertEqual([path.name for path in self.root.iterdir() if path.name.startswith(".define-done-report")], [])

    def test_seal_refuses_ac_ids_in_test_code(self):
        self.repo.write("test/a.rule.test.js", RULE_TEST.replace("'f returns 1'", "'AC-001 f returns 1'"))
        code, out = self.seal(tests=[("AC-001", "test/a.rule.test.js", "AC-001 f returns 1"), TESTS[1]])
        self.assertEqual(code, 1)
        self.assertIn("AC-ID を書かない", out)

    def test_seal_refuses_a_test_without_a_criterion(self):
        self.repo.write("test/a.rule.test.js", RULE_TEST + "test('f is a function', () => assert.equal(typeof f, 'function'));\n")
        code, out = self.seal()
        self.assertEqual(code, 1)
        self.assertIn("対応する AC が無いテスト「f is a function」", out)

    def test_seal_refuses_a_criterion_whose_test_name_does_not_match(self):
        code, out = self.seal(tests=[("AC-001", "test/a.rule.test.js", "f returns one"), TESTS[1]])
        self.assertEqual(code, 1)
        self.assertIn("missing: AC-001", out)

    def test_seal_refuses_a_rule_test_that_already_passes(self):
        before = self.head()
        self.repo.write("plan.md", plan_text([("AC-001", "規則"), ("AC-002", "規則")]))
        code, out = self.seal(["test/a.rule.test.js", "test/a.keep.test.js"], ["test/golden/g.txt", "test/harness/app.js", "plan.md"])
        self.assertEqual(code, 1)
        self.assertIn("kind: AC-002", out)
        self.assertEqual(self.head(), before)

    def test_seal_refuses_a_non_impact_test_that_fails(self):
        before = self.head()
        self.repo.write("plan.md", plan_text([("AC-001", "非影響"), ("AC-002", "非影響")]))
        code, out = self.seal([], ["test/a.rule.test.js", *KEEP_FILES])
        self.assertEqual(code, 1)
        self.assertIn("kind: AC-001", out)
        self.assertEqual(self.head(), before)

    def test_seal_refuses_a_command_without_report_output(self):
        code, out = self.seal(command="node --test")
        self.assertEqual(code, 1)
        self.assertIn("{report}", out)

    def test_seal_refuses_a_test_that_imports_product_code(self):
        self.repo.write("test/a.rule.test.js", RULE_TEST.replace("./harness/app.js", "../src/a.js"))
        code, out = self.seal()
        self.assertEqual(code, 1)
        self.assertIn("boundary: test/a.rule.test.js", out)

    def test_seal_refuses_a_test_that_never_ran(self):
        self.repo.write("test/a.rule.test.js", RULE_TEST.replace("./harness/app.js", "./harness/missing.js"))
        code, out = self.seal()
        self.assertEqual(code, 1)
        self.assertIn("missing: AC-001", out)

    def test_results_of_tests_outside_the_seal_are_not_counted(self):
        self.repo.write("test/old.test.js", "import { test } from 'node:test';\ntest('f returns 1', () => {});\n")
        self.repo.commit("old acceptance test with the same name", "test/old.test.js")
        command = REPORT_COMMAND.replace("test/a.keep.test.js", "test/a.keep.test.js test/old.test.js")
        code, out = self.seal(command=command)
        self.assertEqual(code, 0, out)
        self.implement()
        self.repo.write("src/a.js", "export const f = () => 0;\n")
        self.repo.commit("break f again")
        code, out = run("verify", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("fail: AC-001", out)

    def test_golden_file_in_the_seal_is_protected(self):
        self.seal()
        self.repo.write("test/golden/g.txt", "changed")
        self.repo.commit("edit golden")
        code, out = run("check", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("tamper:", out)
        self.assertIn("test/golden/g.txt", out)

    def test_verify_passes_when_every_criterion_passes_now(self):
        self.seal()
        self.implement()
        code, out = run("verify", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("AC-001: rule current=pass", out)
        self.assertIn("AC-002: non-impact current=pass", out)

    def test_verify_fails_while_a_rule_is_red(self):
        self.seal()
        code, out = run("verify", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("fail: AC-001", out)

    def test_verify_runs_only_the_current_tree_so_a_runner_bound_to_the_repo_works(self):
        command = f"cd {self.root} && " + REPORT_COMMAND
        code, out = self.seal(command=command)
        self.assertEqual(code, 0, out)
        self.implement()
        code, out = run("verify", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertNotIn("sealed-exit", out)

    def test_plan_with_only_non_impact_criteria_completes_without_red(self):
        command = REPORT_COMMAND.replace("test/a.rule.test.js ", "")
        code, out = self.seal([], KEEP_FILES, [TESTS[1]], command)
        self.assertEqual(code, 0, out)
        code, out = run("verify", str(self.root))
        self.assertEqual(code, 0, out)

    def test_commit_whose_files_differ_from_the_recorded_list_is_not_a_seal(self):
        self.seal()
        self.repo.write("src/a.js", "export const f = () => 1;\n")
        self.repo.write("test/a.rule.test.js", RULE_TEST.replace("returns 1", "returns one"))
        self.repo.commit(f"feat: f (#1)\n\n* impl\n\n{self.body()}")
        code, out = run("check", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("tamper:", out)
        self.assertNotIn("src/a.js", out.split("protected:")[1].splitlines()[0])

    def test_resealing_after_fixing_only_the_harness_keeps_check_green(self):
        self.seal()
        self.repo.write("test/harness/app.js", HARNESS + "export const fixed = true;\n")
        code, out = self.seal()
        self.assertEqual(code, 0, out)
        self.assertIn("Define-Done-Files: test/harness/app.js\n", self.body())
        code, out = run("check", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertNotIn("tamper:", out)

    def stash_list(self):
        return subprocess.run(["git", "-C", str(self.root), "stash", "list", "--format=%H"], capture_output=True, text=True).stdout.split()

    def write_implementation_in_tree(self):
        self.repo.write("src/a.js", "import { one } from './one.js';\nexport const f = () => one;\n")
        self.repo.write("src/one.js", "export const one = 1;\n")

    def test_seal_sets_aside_changes_outside_the_seal_and_restores_them(self):
        self.write_implementation_in_tree()
        code, out = self.seal()
        self.assertEqual(code, 0, out)
        self.assertIn("AC-001: rule now=fail", out)
        self.assertEqual((self.root / "src/a.js").read_text(), "import { one } from './one.js';\nexport const f = () => one;\n")
        self.assertEqual((self.root / "src/one.js").read_text(), "export const one = 1;\n")
        self.assertNotIn("src/", self.body().split("Define-Done-Files:")[1].splitlines()[0])
        self.assertEqual(self.stash_list(), [])

    def test_seal_with_nothing_outside_the_seal_leaves_an_existing_stash_alone(self):
        self.repo.write("notes.txt", "draft\n")
        self.repo.git("stash", "push", "-q", "--include-untracked", "--", "notes.txt")
        before = self.stash_list()
        code, out = self.seal()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.stash_list(), before)
        self.assertFalse((self.root / "notes.txt").exists())

    def test_seal_that_sets_aside_changes_keeps_an_existing_stash(self):
        self.repo.write("notes.txt", "draft\n")
        self.repo.git("stash", "push", "-q", "--include-untracked", "--", "notes.txt")
        before = self.stash_list()
        self.write_implementation_in_tree()
        code, out = self.seal()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.stash_list(), before)
        self.assertTrue((self.root / "src/one.js").exists())

    def test_refused_seal_restores_changes_outside_the_seal(self):
        self.write_implementation_in_tree()
        before = self.head()
        code, out = self.seal(tests=[("AC-001", "test/a.rule.test.js", "f returns one"), TESTS[1]])
        self.assertEqual(code, 1)
        self.assertEqual(self.head(), before)
        self.assertTrue((self.root / "src/one.js").exists())
        self.assertEqual(self.stash_list(), [])

    def test_seal_keeps_the_set_aside_changes_in_the_stash_when_it_cannot_restore_them(self):
        self.write_implementation_in_tree()
        original = check_seal.run_tests

        def locking_run_tests(cwd, command):
            result = original(cwd, command)
            (self.root / ".git" / "index.lock").write_text("")
            return result

        check_seal.run_tests = locking_run_tests
        try:
            code, out = self.seal()
        finally:
            check_seal.run_tests = original
            (self.root / ".git" / "index.lock").unlink(missing_ok=True)
        self.assertEqual(code, 1)
        self.assertIn("git stash apply", out)
        self.assertEqual(len(self.stash_list()), 1)
        self.repo.git("stash", "pop", "-q")
        self.assertTrue((self.root / "src/one.js").exists())

    def spike_patch(self, body="import { one } from './one.js';\nexport const f = () => one;\n"):
        self.repo.write("src/a.js", body)
        self.repo.write("src/one.js", "export const one = 1;\n")
        self.repo.git("add", "-N", "src/one.js")
        diff = subprocess.run(["git", "-C", str(self.root), "diff", "--", "src"], capture_output=True, text=True, check=True).stdout
        self.repo.git("reset", "-q", "--", "src/one.js")
        (self.root / "src/one.js").unlink()
        self.repo.git("checkout", "--", "src/a.js")
        path = Path(self.tmp.name) / "spike.patch"
        path.write_text(diff, encoding="utf-8")
        return str(path)

    def test_spike_confirms_that_the_rule_tests_pass_with_the_trial_implementation(self):
        patch = self.spike_patch()
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=patch))
        self.assertEqual(code, 0, out)
        self.assertIn("AC-001: rule spike=pass now=fail", out)
        self.assertIn("AC-002: non-impact spike=pass now=pass", out)
        self.assertEqual((self.root / "src/a.js").read_text(), "export const f = () => 0;\n")
        self.assertFalse((self.root / "src/one.js").exists())

    def test_spike_keeps_an_implementation_in_progress(self):
        patch = self.spike_patch()
        self.repo.write("src/a.js", "export const f = () => 0; // wip\n")
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=patch))
        self.assertEqual(code, 0, out)
        self.assertEqual((self.root / "src/a.js").read_text(), "export const f = () => 0; // wip\n")
        self.assertEqual(self.stash_list(), [])

    def test_spike_that_does_not_pass_the_rule_tests_refuses_the_seal(self):
        patch = self.spike_patch(body="export const f = () => 2;\n")
        before = self.head()
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=patch))
        self.assertEqual(code, 1)
        self.assertIn("spike: AC-001", out)
        self.assertEqual(self.head(), before)
        self.assertEqual((self.root / "src/a.js").read_text(), "export const f = () => 0;\n")

    def test_spike_patch_that_touches_a_sealed_file_is_refused(self):
        self.repo.write("test/harness/app.js", HARNESS + "export const extra = 1;\n")
        self.repo.git("add", "-N", "test/harness/app.js")
        diff = subprocess.run(["git", "-C", str(self.root), "diff", "--", "test/harness/app.js"], capture_output=True, text=True, check=True).stdout
        self.repo.git("reset", "-q", "--", "test/harness/app.js")
        self.repo.write("test/harness/app.js", HARNESS)
        path = Path(self.tmp.name) / "bad.patch"
        path.write_text(diff, encoding="utf-8")
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=str(path)))
        self.assertEqual(code, 1)
        self.assertIn("spike:", out)

    def test_spike_without_a_patch_file_is_refused(self):
        missing = str(Path(self.tmp.name) / "none.patch")
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=missing))
        self.assertEqual(code, 1)
        self.assertIn("spike:", out)

    def test_failing_check_command_refuses_the_seal(self):
        before = self.head()
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, check_command="node -e \"process.exit(3)\""))
        self.assertEqual(code, 1)
        self.assertIn("check:", out)
        self.assertEqual(self.head(), before)

    def test_check_command_runs_on_the_tree_with_the_trial_implementation(self):
        patch = self.spike_patch()
        check = "node -e \"import('./src/a.js').then((m) => process.exit(m.f() === 1 ? 0 : 1))\""
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=patch, check_command=check))
        self.assertEqual(code, 0, out)
        self.assertIn("check: pass", out)

    def test_unmatched_test_name_lists_the_tests_that_ran_in_that_file(self):
        code, out = self.seal(tests=[("AC-001", "test/a.rule.test.js", "suite > f returns 1"), TESTS[1]])
        self.assertEqual(code, 1)
        self.assertIn("missing: AC-001", out)
        self.assertIn("f returns 1", out.split("missing: AC-001")[1].splitlines()[0])

    def test_reseal_rebuilds_the_spec_from_the_last_seal(self):
        self.seal()
        self.repo.write("test/harness/app.js", HARNESS + "export const fixed = true;\n")
        code, out = run("reseal", str(self.root), stdin=json.dumps({"subject": "test: 土台を直す"}))
        self.assertEqual(code, 0, out)
        body = self.body()
        self.assertTrue(body.startswith("test: 土台を直す"))
        self.assertIn("Define-Done-Files: test/harness/app.js\n", body)
        self.assertIn("Define-Done-Test: AC-002 = test/a.keep.test.js › g keeps its text\n", body)
        code, out = run("check", str(self.root))
        self.assertEqual(code, 0, out)

    def test_reseal_adds_a_criterion_and_its_test(self):
        self.seal()
        self.repo.write("test/a.rule.test.js", RULE_TEST + "test('f is not 0', () => assert.notEqual(f(), 0));\n")
        self.repo.write("plan.md", plan_text([("AC-001", "規則"), ("AC-002", "非影響"), ("AC-003", "規則")]))
        extra = {"tests": [{"ac": "AC-003", "file": "test/a.rule.test.js", "name": "f is not 0"}]}
        code, out = run("reseal", str(self.root), stdin=json.dumps(extra))
        self.assertEqual(code, 0, out)
        self.assertIn("Define-Done-Seal: AC-001, AC-002, AC-003", self.body())

    def test_reseal_without_a_seal_is_refused(self):
        code, out = run("reseal", str(self.root), stdin="")
        self.assertEqual(code, 1)
        self.assertIn("reseal:", out)

    def test_seal_records_a_file_whose_name_is_not_ascii(self):
        self.repo.write("test/harness/日本語.js", "export const name = 'ja';\n")
        code, out = self.seal(keep=KEEP_FILES + ["test/harness/日本語.js"])
        self.assertEqual(code, 0, out)
        self.assertIn("test/harness/日本語.js", self.body().split("Define-Done-Files:")[1].splitlines()[0])

    def refused_plan(self, text):
        self.repo.write("plan.md", text)
        before = self.head()
        code, out = self.seal()
        self.assertEqual(code, 1, out)
        self.assertEqual(self.head(), before)
        return out

    def test_seal_refuses_a_plan_whose_gate_is_not_ready(self):
        out = self.refused_plan(plan_text([("AC-001", "規則"), ("AC-002", "非影響")], gate="blocked (D1 が R-1 と矛盾する)"))
        self.assertIn("plan: Gate が ready でない", out)

    def test_seal_refuses_ac_ids_that_differ_from_the_criteria(self):
        out = self.refused_plan(plan_text([("AC-001", "規則"), ("AC-002", "非影響")], ids="AC-001", rows=["| R-1 | AC-001 |"]))
        self.assertIn("plan: `- AC IDs:`", out)
        self.assertIn("AC-002", out)

    def test_seal_refuses_a_test_whose_criterion_is_not_in_the_plan(self):
        out = self.refused_plan(plan_text([("AC-001", "規則")]))
        self.assertIn("plan: テストを対応させた AC-002", out)

    def test_seal_refuses_a_criterion_whose_kind_differs_from_its_test_file(self):
        out = self.refused_plan(plan_text([("AC-001", "非影響"), ("AC-002", "非影響")]))
        self.assertIn("plan: AC-001 は計画で [非影響]", out)

    def test_seal_refuses_a_source_that_is_not_a_requirement(self):
        out = self.refused_plan(plan_text([("AC-001", "規則", "R-1, R-9"), ("AC-002", "非影響")]))
        self.assertIn("plan: AC-001 の出典 R-9", out)

    def test_seal_refuses_a_requirement_row_whose_criteria_do_not_cite_it(self):
        rows = ["| R-1 | AC-001 |", "| R-2 | AC-002 (推奨の帰結を観測する) |"]
        out = self.refused_plan(plan_text([("AC-001", "規則"), ("AC-002", "非影響")], rows=rows, requirements=("R-1", "R-2")))
        self.assertIn("plan: 要求の表は R-2 を AC-002 に対応させているが", out)
        self.assertNotIn("R-1 を", out)

    def test_seal_refuses_a_requirement_missing_from_the_table(self):
        out = self.refused_plan(plan_text([("AC-001", "規則"), ("AC-002", "非影響")], requirements=("R-1", "R-2")))
        self.assertIn("plan: R-2 が `## MECE Review` の要求の表に無い", out)

    def test_seal_refuses_a_requirement_row_without_a_criterion_or_a_label(self):
        rows = ["| R-1 | AC-001, AC-002 |", "| R-2 | 実装で確かめる |"]
        out = self.refused_plan(plan_text([("AC-001", "規則"), ("AC-002", "非影響")], rows=rows, requirements=("R-1", "R-2")))
        self.assertIn("plan: 要求の表の R-2 の行", out)

    def test_seal_accepts_unverified_and_out_of_scope_rows_and_a_row_naming_a_related_criterion(self):
        rows = [
            "| R-1 | AC-001 (値が user の id であることは AC-002 の観測に現れる) |",
            "| R-2 | 未検証: 外から観測する手段が無い |",
            "| R-3 | 範囲外: 規約として enforce-conventions で担保する (描画の結果は AC-002 で守る) |",
            "| R-4 | 不足情報: 上限の値を資料が決めていない (既定: 決めない、行き先: 要求の持ち主) |",
        ]
        criteria = [("AC-001", "規則"), ("AC-002", "非影響", "test/b.test.js")]
        self.repo.write("plan.md", plan_text(criteria, rows=rows, requirements=("R-1", "R-2", "R-3", "R-4")))
        code, out = self.seal()
        self.assertEqual(code, 0, out)

    def test_seal_reads_a_plan_outside_the_repo_and_names_it_in_the_subject(self):
        (self.root / "plan.md").unlink()
        outside = Path(self.tmp.name) / "489-registration" / "design.md"
        outside.parent.mkdir()
        outside.write_text(PLAN, encoding="utf-8")
        keep = [path for path in KEEP_FILES if path != "plan.md"]
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, keep, TESTS))
        self.assertEqual(code, 1)
        self.assertIn("plan: 計画が凍結するファイルに無い", out)
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, keep, TESTS, plan=str(outside)))
        self.assertEqual(code, 0, out)
        self.assertTrue(self.body().startswith("test: 489-registration/design.md の受け入れテスト\n"))

    def test_subject_names_the_plan_and_a_reseal_says_it_fixes_the_tests(self):
        self.seal()
        self.assertTrue(self.body().startswith("test: plan.md の受け入れテスト\n"))
        self.repo.write("test/harness/app.js", HARNESS + "export const fixed = true;\n")
        code, out = run("reseal", str(self.root), stdin="")
        self.assertEqual(code, 0, out)
        self.assertTrue(self.body().startswith("test: plan.md の受け入れテストを直す\n"))

    def test_seal_refuses_before_running_when_a_frozen_file_outside_it_is_dirty(self):
        self.seal()
        self.repo.write("test/a.keep.test.js", KEEP_TEST.replace("keeps", "still keeps"))
        before = self.head()
        original = check_seal.run_tests
        calls = []
        check_seal.run_tests = lambda cwd, command: calls.append(command) or original(cwd, command)
        try:
            code, out = self.start_next_plan()
        finally:
            check_seal.run_tests = original
        self.assertEqual(code, 1)
        self.assertIn("tamper: 凍結したファイルに未 commit の変更がある (M test/a.keep.test.js)", out)
        self.assertEqual(calls, [])
        self.assertEqual(self.head(), before)

    def open_spike(self, *files):
        code, out = run("spike-open", str(self.root), *files)
        self.assertEqual(code, 0, out)
        return Path(out.split("worktree: ")[1].splitlines()[0])

    def test_spike_worktree_links_dependencies_and_copies_the_given_files(self):
        self.repo.write(".gitignore", "node_modules/\n")
        self.repo.commit("ignore", ".gitignore")
        self.repo.write("node_modules/dep/index.js", "export const dep = 1;\n")
        self.repo.write("packages/web/node_modules/dep/index.js", "export const dep = 2;\n")
        work = self.open_spike("test/a.rule.test.js", "test/harness/app.js")
        self.addCleanup(shutil.rmtree, work.parent, True)
        self.assertNotIn(self.root.resolve(), work.resolve().parents)
        self.assertTrue((work / "node_modules").is_symlink())
        self.assertEqual((work / "packages/web/node_modules/dep/index.js").read_text(), "export const dep = 2;\n")
        self.assertEqual((work / "test/a.rule.test.js").read_text(), RULE_TEST)
        self.assertEqual((work / "src/a.js").read_text(), "export const f = () => 0;\n")
        self.assertFalse((work / "test/a.keep.test.js").exists())

    def test_spike_close_writes_a_patch_of_the_trial_implementation_only_and_seal_accepts_it(self):
        self.repo.write(".gitignore", "node_modules/\n")
        self.repo.commit("ignore", ".gitignore")
        self.repo.write("node_modules/dep/index.js", "export const dep = 1;\n")
        files = [path for path in RULE_FILES + KEEP_FILES if path != "plan.md"]
        work = self.open_spike(*files)
        self.addCleanup(shutil.rmtree, work.parent, True)
        (work / "src/a.js").write_text("import { one } from './one.js';\nexport const f = () => one;\n")
        (work / "src/one.js").write_text("export const one = 1;\n")
        code, out = run("spike-close", str(self.root), str(work))
        self.assertEqual(code, 0, out)
        patch = Path(out.split("spike: ")[1].splitlines()[0])
        self.assertFalse(work.exists())
        self.assertNotIn(self.root.resolve(), patch.resolve().parents)
        text = patch.read_text()
        self.assertIn("src/a.js", text)
        self.assertIn("src/one.js", text)
        self.assertNotIn("node_modules", text)
        self.assertNotIn("test/", text)
        self.assertTrue((self.root / "node_modules/dep/index.js").exists())
        self.assertEqual((self.root / "src/a.js").read_text(), "export const f = () => 0;\n")
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=str(patch)))
        self.assertEqual(code, 0, out)
        self.assertIn("AC-001: rule spike=pass now=fail", out)

    def test_spike_close_refuses_a_copied_file_edited_only_in_the_worktree(self):
        work = self.open_spike("test/a.rule.test.js", "test/harness/app.js")
        self.addCleanup(shutil.rmtree, work.parent, True)
        (work / "src/a.js").write_text("export const f = () => 1;\n")
        (work / "test/a.rule.test.js").write_text(RULE_TEST.replace("f(), 1", "f(), 2"))
        code, out = run("spike-close", str(self.root), str(work))
        self.assertEqual(code, 1)
        self.assertIn("spike: 複製の test/a.rule.test.js が repo と食い違う", out)
        self.assertTrue(work.exists())
        self.repo.git("worktree", "remove", "--force", str(work))

    DECIDED_PLAN = PLAN.replace("# plan\n", "# plan\n\n## 決定\n\n- D1: f が 1 を返す\n", 1)
    REJECTED_DECISION = "\n### 検査が拒んだ決定\n\n| 決定 | 拒んだ検査 | 試作が取った形 |\n|---|---|---|\n| D1 | lint の no-magic が 1 を拒んだ | 定数 ONE を返す |\n"

    def spike_patch_with_plan(self, edit_plan):
        self.repo.write("plan.md", self.DECIDED_PLAN)
        files = [path for path in RULE_FILES + KEEP_FILES if path != "plan.md"]
        code, out = run("spike-open", str(self.root), "plan.md", *files)
        self.assertEqual(code, 0, out)
        work = Path(out.split("worktree: ")[1].splitlines()[0])
        self.addCleanup(shutil.rmtree, work.parent, True)
        (work / "src/a.js").write_text("export const f = () => 1;\n")
        self.repo.write("plan.md", edit_plan(self.DECIDED_PLAN))
        code, out = run("spike-close", str(self.root), str(work))
        self.assertEqual(code, 0, out)
        return out.split("spike: ")[1].splitlines()[0]

    def test_seal_refuses_a_plan_whose_decisions_changed_after_spike_open(self):
        patch = self.spike_patch_with_plan(lambda plan: plan.replace("- D1: f が 1 を返す", "- D1: f が定数 ONE を返す"))
        before = self.head()
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=patch))
        self.assertEqual(code, 1)
        self.assertIn("plan: 計画の 4 節の外が `spike-open` の後に変わっている", out)
        self.assertIn("検査が拒んだ決定", out)
        self.assertEqual(self.head(), before)

    def test_seal_accepts_a_plan_that_records_the_rejected_decision_in_the_review(self):
        patch = self.spike_patch_with_plan(lambda plan: plan + self.REJECTED_DECISION)
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=patch))
        self.assertEqual(code, 0, out)
        code, out = run("report", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("検査が拒んだ決定:\n| D1 | lint の no-magic が 1 を拒んだ | 定数 ONE を返す |", out)

    def test_patch_with_the_plan_baseline_still_applies_as_a_starting_point(self):
        patch = self.spike_patch_with_plan(lambda plan: plan)
        self.assertTrue(Path(patch).read_text().startswith("Define-Done-Plan-Outside: "))
        self.repo.git("apply", patch)
        self.assertEqual((self.root / "src/a.js").read_text(), "export const f = () => 1;\n")

    def test_reseal_does_not_compare_the_plan_with_the_baseline_of_the_spike(self):
        patch = self.spike_patch_with_plan(lambda plan: plan)
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=patch))
        self.assertEqual(code, 0, out)
        self.repo.write("plan.md", self.DECIDED_PLAN.replace("- D1: f が 1 を返す", "- D1: f が定数 ONE を返す"))
        code, out = run("reseal", str(self.root), stdin=json.dumps({"spike": patch}))
        self.assertEqual(code, 0, out)

    def test_spike_open_reads_a_plan_outside_the_repo_and_does_not_copy_it(self):
        outside = Path(self.tmp.name) / "plans" / "design.md"
        outside.parent.mkdir()
        outside.write_text(self.DECIDED_PLAN, encoding="utf-8")
        code, out = run("spike-open", str(self.root), str(outside), "test/a.rule.test.js", "test/harness/app.js")
        self.assertEqual(code, 0, out)
        work = Path(out.split("worktree: ")[1].splitlines()[0])
        self.addCleanup(shutil.rmtree, work.parent, True)
        (work / "src/a.js").write_text("export const f = () => 1;\n")
        self.assertEqual(outside.read_text(encoding="utf-8"), self.DECIDED_PLAN)
        code, out = run("spike-close", str(self.root), str(work))
        self.assertEqual(code, 0, out)
        patch = Path(out.split("spike: ")[1].splitlines()[0])
        self.assertTrue(patch.read_text().startswith("Define-Done-Plan-Outside: "))
        self.assertNotIn("design.md", patch.read_text())

    def test_spike_open_refuses_two_plans(self):
        self.repo.write("plans/other.md", PLAN)
        code, out = run("spike-open", str(self.root), "plan.md", "plans/other.md", "test/a.rule.test.js")
        self.assertEqual(code, 1)
        self.assertIn("plan: 計画の候補が複数ある", out)

    REPORTED_PLAN = plan_text(
        [("AC-001", "規則"), ("AC-002", "非影響")],
        rows=["| R-1 | AC-001, AC-002 |", "| R-2 | 範囲外: 規約として enforce-conventions で担保する |"],
        requirements=("R-1", "R-2"),
    ) + "\n### 残ったリスクの表\n\n| リスク | 守る先 |\n|---|---|\n| f が負の数を返す | AC-001 |\n| 空の入力で落ちる | 実装のテスト: 空の入力で 0 を返す |\n| 本番の時計がずれる | 未検証: staging の log |\n"

    def test_report_extracts_the_final_answer_from_the_plan(self):
        self.repo.write("plan.md", self.REPORTED_PLAN)
        self.seal()
        sha = self.head()
        code, answer = run("report", str(self.root))
        self.assertEqual(code, 0, answer)
        self.assertIn("要求:\n- R-1: f は 1 を返す (「f は 1 を返す」 依頼)\n- R-2: f は 1 を返す (「f は 1 を返す」 依頼)\n", answer)
        self.assertIn("Gate: ready\n", answer)
        self.assertIn("AC: 規則 1 件、非影響 1 件\n", answer)
        self.assertIn(f"凍結: {sha}\n", answer)
        self.assertIn("基準の無い要求:\n| R-2 | 範囲外: 規約として enforce-conventions で担保する |\n", answer)
        self.assertIn("実装が足すテスト:\n| 空の入力で落ちる | 実装のテスト: 空の入力で 0 を返す |\n", answer)
        self.assertIn("未検証:\n| 本番の時計がずれる | 未検証: staging の log |\n", answer)
        self.assertNotIn("f が負の数を返す", answer)
        self.assertNotIn("検査が拒んだ決定", answer)

    def test_report_still_answers_after_the_implementation_is_committed(self):
        self.repo.write("plan.md", self.REPORTED_PLAN)
        self.seal()
        sha = self.head()
        self.implement()
        code, out = run("report", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("要求:\n- R-1: f は 1 を返す (「f は 1 を返す」 依頼)\n", out)
        self.assertIn("AC: 規則 1 件、非影響 1 件\n", out)
        self.assertIn(f"凍結: {sha}\n", out)
        self.assertIn("実装が足すテスト:\n| 空の入力で落ちる | 実装のテスト: 空の入力で 0 を返す |\n", out)

    def test_report_reads_a_plan_outside_the_repo_from_the_given_path(self):
        outside = Path(self.tmp.name) / "plans" / "design.md"
        outside.parent.mkdir()
        outside.write_text(self.REPORTED_PLAN, encoding="utf-8")
        (self.root / "plan.md").unlink()
        keep = [path for path in KEEP_FILES if path != "plan.md"]
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, RULE_FILES, keep, TESTS, plan=str(outside)))
        self.assertEqual(code, 0, out)
        code, out = run("report", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("plan: ", out)
        code, out = run("report", str(self.root), str(outside))
        self.assertEqual(code, 0, out)
        self.assertIn("要求:\n- R-1: ", out)

    def test_check_names_the_protection_of_each_given_file(self):
        self.add_remote_and_push()
        self.seal()
        code, out = run("check", str(self.root), "test/a.rule.test.js", "src/a.js")
        self.assertEqual(code, 0, out)
        self.assertIn("protection: test/a.rule.test.js = in-progress", out)
        self.assertIn("protection: src/a.js = unsealed", out)
        self.push()
        code, out = run("check", str(self.root), "test/a.rule.test.js", "test/a.keep.test.js")
        self.assertIn("protection: test/a.rule.test.js = permanent", out)
        self.assertIn("protection: test/a.keep.test.js = released", out)

    def test_spike_close_refuses_a_directory_that_spike_open_did_not_make(self):
        code, out = run("spike-close", str(self.root), str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("spike:", out)
        self.assertTrue((self.root / "src/a.js").exists())

    def test_reseal_with_nothing_changed_is_refused(self):
        self.seal()
        code, out = self.seal()
        self.assertEqual(code, 1)
        self.assertIn("HEAD から変わっていない", out)

    def test_unpushed_seal_on_main_is_in_progress(self):
        self.add_remote_and_push()
        self.seal()
        self.repo.write("test/a.keep.test.js", KEEP_TEST.replace("keeps", "still keeps"))
        self.repo.commit("edit non-impact test")
        code, out = run("check", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("tamper:", out)

    def start_next_plan(self):
        self.repo.write("test/c.rule.test.js", RULE_TEST.replace("assert.equal(f(), 1)", "assert.equal(f(), 2)").replace("f returns 1", "f returns 2"))
        self.repo.write("plans/next.md", plan_text([("AC-101", "規則")]))
        command = "node --test --test-reporter=junit --test-reporter-destination={report} test/c.rule.test.js"
        return run("seal", str(self.root), stdin=seal_spec(command, ["test/c.rule.test.js"], ["plans/next.md"], [("AC-101", "test/c.rule.test.js", "f returns 2")]))

    def test_completed_seal_keeps_only_rule_files(self):
        self.add_remote_and_push()
        self.seal()
        self.implement()
        self.push()
        code, out = self.start_next_plan()
        self.assertEqual(code, 0, out)
        code, out = run("check", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("permanent: test/a.rule.test.js", out)
        self.repo.write("test/a.keep.test.js", KEEP_TEST.replace("keeps", "still keeps"))
        self.repo.write("test/golden/g.txt", "kept")
        self.repo.commit("later plan edits a completed non-impact test")
        code, out = run("check", str(self.root))
        self.assertEqual(code, 0, out)
        self.repo.write("test/a.rule.test.js", RULE_TEST.replace("f(), 1", "f(), 0"))
        self.repo.commit("later plan edits a completed rule test")
        code, out = run("check", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("tamper:", out)

    def test_rewriting_a_permanent_rule_needs_supersedes(self):
        self.add_remote_and_push()
        self.seal()
        self.implement()
        self.push()
        self.repo.write("test/a.rule.test.js", RULE_TEST.replace("returns 1", "returns one"))
        self.repo.write("src/a.js", "export const f = () => 0;\n")
        self.repo.commit("revert f", "src/a.js")
        rewrite = "node --test --test-reporter=junit --test-reporter-destination={report} test/a.rule.test.js"
        tests = [("AC-003", "test/a.rule.test.js", "f returns one")]
        self.repo.write("plan.md", plan_text([("AC-002", "非影響"), ("AC-003", "規則")]))
        code, out = run("seal", str(self.root), stdin=seal_spec(rewrite, ["test/a.rule.test.js"], ["plan.md"], tests))
        self.assertEqual(code, 1)
        self.assertIn("supersedes:", out)
        code, out = run("seal", str(self.root), stdin=seal_spec(rewrite, ["test/a.rule.test.js"], ["plan.md"], tests, supersedes="AC-001 (R-1)"))
        self.assertEqual(code, 0, out)
        self.assertIn("Define-Done-Supersedes: AC-001 (R-1)", self.body())

    def test_standalone_supersedes_keeps_a_rule_file_permanent(self):
        self.add_remote_and_push()
        self.seal()
        self.implement()
        self.repo.write("test/a.rule.test.js", RULE_TEST.replace("returns 1", "returns one"))
        self.repo.commit("test: 記録の無い変更を記録する\n\nDefine-Done-Supersedes: AC-001\n", "test/a.rule.test.js")
        self.push()
        self.start_next_plan()
        self.repo.write("test/a.rule.test.js", RULE_TEST.replace("f(), 1", "f(), 0"))
        self.repo.commit("weaken")
        code, out = run("check", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("tamper:", out)
        self.assertIn("test/a.rule.test.js", out)


RSPEC_HARNESS = "require_relative '../../../lib/a'\n"
RSPEC_RULE = "require 'rspec'\nrequire_relative 'harness/app'\nRSpec.describe 'f' do\n  it 'returns 1' do\n    expect(F.call).to eq(1)\n  end\nend\n"
RSPEC_KEEP = "require 'rspec'\nrequire_relative 'harness/app'\nRSpec.describe 'g' do\n  it 'keeps its text' do\n    expect(G.call).to eq('kept')\n  end\nend\n"


class ReportTest(unittest.TestCase):
    def test_require_of_rails_helper_and_the_harness_is_allowed(self):
        text = "require 'rails_helper'\nrequire_relative 'harness/sign_in'\nrequire_relative './harness'\n"
        self.assertEqual(check_seal.import_findings("spec/acceptance/a_spec.rb", text), [])

    def test_require_of_product_code_is_a_boundary_finding(self):
        text = "require 'rails_helper'\nrequire_relative '../../app/models/user'\nrequire 'net/http'\n"
        self.assertEqual(check_seal.import_findings("spec/acceptance/a_spec.rb", text), ["../../app/models/user", "net/http"])

    def mapped(self, report, file, name):
        test = {"ac": "AC-001", "file": file, "name": name}
        return check_seal.states_by_ac(check_seal.parse_report(report), [test])

    def test_rspec_json_matches_file_and_full_description(self):
        report = '{"examples": [{"file_path": "./spec/acceptance/a_rule_spec.rb", "full_description": "f returns 1", "description": "returns 1", "status": "failed"}, {"file_path": "./spec/old_spec.rb", "full_description": "f returns 1", "status": "passed"}]}'
        self.assertEqual(self.mapped(report, "spec/acceptance/a_rule_spec.rb", "returns 1"), {"AC-001": ["fail"]})

    def test_rspec_junit_formatter_matches_dotted_classname(self):
        report = '<testsuite><testcase classname="spec.acceptance.a_rule_spec" name="f returns 1"><failure message="x"/></testcase></testsuite>'
        self.assertEqual(self.mapped(report, "spec/acceptance/a_rule_spec.rb", "returns 1"), {"AC-001": ["fail"]})

    def test_bun_junit_matches_relative_file_and_test_name(self):
        report = '<testsuites><testcase name="空のまま送ると誤りを示す" classname="送らせて誤りを示す" file="acceptance/a.test.ts"/></testsuites>'
        self.assertEqual(self.mapped(report, "acceptance/a.test.ts", "空のまま送ると誤りを示す"), {"AC-001": ["pass"]})

    def test_vitest_junit_matches_file_classname_and_describe_path(self):
        report = '<testsuites><testcase classname="web/acceptance/a.test.ts" name="送らせて誤りを示す &gt; 空のまま送ると誤りを示す"/></testsuites>'
        self.assertEqual(self.mapped(report, "web/acceptance/a.test.ts", "空のまま送ると誤りを示す"), {"AC-001": ["pass"]})

    def test_playwright_junit_matches_classname_relative_to_test_dir(self):
        report = '<testsuites><testcase name="送らせて誤りを示す › 空のまま送ると誤りを示す" classname="x.browser.ts"><failure/></testcase></testsuites>'
        self.assertEqual(self.mapped(report, "acceptance-browser/x.browser.ts", "空のまま送ると誤りを示す"), {"AC-001": ["fail"]})

    def test_node_junit_matches_absolute_file(self):
        report = '<testsuites><testcase name="f returns 1" classname="test" file="/tmp/x/repo/test/a.rule.test.js"><failure/></testcase></testsuites>'
        self.assertEqual(self.mapped(report, "test/a.rule.test.js", "f returns 1"), {"AC-001": ["fail"]})

    def test_unmatched_test_is_missing(self):
        report = '<testsuites><testcase name="other" file="test/a.rule.test.js"/></testsuites>'
        self.assertEqual(self.mapped(report, "test/a.rule.test.js", "f returns 1"), {"AC-001": ["missing"]})

    @unittest.skipUnless(shutil.which("rspec"), "rspec is not installed")
    def test_seal_and_verify_with_rspec(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = Repo(root)
            repo.write("lib/a.rb", "F = -> { 0 }\nG = -> { 'kept' }\n")
            repo.commit("lib")
            repo.write("spec/acceptance/harness/app.rb", RSPEC_HARNESS)
            repo.write("spec/acceptance/a_rule_spec.rb", RSPEC_RULE)
            repo.write("spec/acceptance/a_keep_spec.rb", RSPEC_KEEP)
            repo.write("plan.md", PLAN)
            command = "rspec spec/acceptance/a_rule_spec.rb spec/acceptance/a_keep_spec.rb --format json --out {report}"
            tests = [("AC-001", "spec/acceptance/a_rule_spec.rb", "returns 1"), ("AC-002", "spec/acceptance/a_keep_spec.rb", "keeps its text")]
            code, out = run("seal", str(root), stdin=seal_spec(command, ["spec/acceptance/a_rule_spec.rb"], ["spec/acceptance/a_keep_spec.rb", "spec/acceptance/harness/app.rb", "plan.md"], tests))
            self.assertEqual(code, 0, out)
            repo.write("lib/a.rb", "F = -> { 1 }\nG = -> { 'kept' }\n")
            repo.commit("impl")
            code, out = run("verify", str(root))
            self.assertEqual(code, 0, out)
            self.assertIn("AC-001: rule current=pass", out)


if __name__ == "__main__":
    unittest.main()
