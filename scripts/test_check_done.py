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
SCRIPT = ROOT / "plugins" / "define-done" / "skills" / "define-done" / "scripts" / "check_done.py"

spec = importlib.util.spec_from_file_location("check_done", SCRIPT)
check_done = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_done)


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


def run(*argv, stdin=""):
    out = io.StringIO()
    with redirect_stdout(out):
        code = check_done.main(list(argv), stdin)
    return code, out.getvalue()


def plan_text(criteria, gate="ready", rows=None, ids=None, sources="R-1", requirements=("R-1",), bodies=None, requirement_texts=None):
    criteria = [(*criterion, sources)[:3] for criterion in criteria]
    bodies, requirement_texts = bodies or {}, requirement_texts or {}
    listed = ", ".join(ac for ac, _, _ in criteria) if ids is None else ids
    table = rows if rows is not None else [f"| R-1 | {listed} |"]
    return "\n".join([
        "# plan",
        "",
        "## Requirements",
        "",
        *[f"- {requirement}: {requirement_texts.get(requirement, 'f は 1 を返す')} (「f は 1 を返す」 依頼)" for requirement in requirements],
        "",
        "## Ground Review",
        "",
        "無い",
        "",
        "## Acceptance Criteria",
        "",
        *[f"- {ac}: [{kind}] {bodies.get(ac, '振る舞い')} (出典: {cited})" for ac, kind, cited in criteria],
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


def check_spec(command, rule=(), non_impact=(), tests=(), spike="", check_command="", plan="", rewrites=(), new_dirs=(), implemented=()):
    mapping = [{"ac": ac, "file": file, "name": name} for ac, file, name in tests]
    spec = {"test_command": command, "files": [*rule, *non_impact], "tests": mapping}
    for key, value in (("plan", plan), ("spike", spike), ("check_command", check_command), ("rewrites", list(rewrites)), ("new_dirs", list(new_dirs)), ("implemented", list(implemented))):
        if value:
            spec[key] = value
    return json.dumps(spec)


REPORT_COMMAND = "node --test --test-reporter=junit --test-reporter-destination={report} test/a.rule.test.js test/a.keep.test.js"
HARNESS = "export { f } from '../../src/a.js';\nexport { g } from '../../src/b.js';\nimport { readFileSync } from 'node:fs';\nexport const expected = (name) => readFileSync(new URL(`../golden/${name}`, import.meta.url), 'utf8');\n"
RULE_TEST = "import { test } from 'node:test';\nimport assert from 'node:assert/strict';\nimport { f } from './harness/app.js';\ntest('f returns 1', () => assert.equal(f(), 1));\n"
KEEP_TEST = "import { test } from 'node:test';\nimport assert from 'node:assert/strict';\nimport { g, expected } from './harness/app.js';\ntest('g keeps its text', () => assert.equal(g(), expected('g.txt')));\n"
RULE_FILES = ["test/a.rule.test.js"]
KEEP_FILES = ["test/a.keep.test.js", "test/golden/g.txt", "test/harness/app.js", "plan.md"]
TESTS = [("AC-001", "test/a.rule.test.js", "f returns 1"), ("AC-002", "test/a.keep.test.js", "g keeps its text")]


class CheckCommandTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.repo = Repo(self.root)
        self.repo.write("src/b.js", "export const g = () => 'kept';\n")
        self.repo.write("test/harness/existing.js", "export const existing = true;\n")
        self.repo.write("test/golden/existing.txt", "existing")
        self.repo.commit("b")
        self.repo.write("test/harness/app.js", HARNESS)
        self.repo.write("test/golden/g.txt", "kept")
        self.repo.write("test/a.rule.test.js", RULE_TEST)
        self.repo.write("test/a.keep.test.js", KEEP_TEST)
        self.repo.write("plan.md", PLAN)

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, rule=RULE_FILES, keep=KEEP_FILES, tests=TESTS, command=REPORT_COMMAND, **given):
        return run("check", str(self.root), stdin=check_spec(command, rule, keep, tests, **given))

    def head(self):
        return subprocess.run(["git", "-C", str(self.root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


    def implement(self):
        self.repo.write("src/a.js", "export const f = () => 1;\n")
        self.repo.commit("impl")


    OLD_TEST = "import { test } from 'node:test';\nimport assert from 'node:assert/strict';\nimport { existing } from './harness/existing.js';\ntest('AC-009 old stays', () => {\n  assert.equal(existing, true);\n});\n"
    APPENDED_RULE = "import { f } from './harness/app.js';\ntest('f returns 1', () => assert.equal(f(), 1));\n"
    OLD_COMMAND = REPORT_COMMAND.replace("test/a.rule.test.js", "test/old.test.js")

    def commit_old_test(self):
        (self.root / "test/a.rule.test.js").unlink()
        self.repo.write("test/old.test.js", self.OLD_TEST)
        self.repo.commit("old test", "test/old.test.js")

    def check_old_test(self, **given):
        tests = [("AC-001", "test/old.test.js", "f returns 1"), TESTS[1]]
        return self.check(rule=["test/old.test.js"], tests=tests, command=self.OLD_COMMAND, **given)

    def test_check_makes_no_commit_and_leaves_the_files_uncommitted(self):
        before = self.head()
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("AC-001: rule now=fail", out)
        self.assertIn("AC-002: non-impact now=pass", out)
        self.assertIn("checked: AC-001, AC-002\n", out)
        self.assertEqual(self.head(), before)
        status = subprocess.run(["git", "-C", str(self.root), "status", "--porcelain", "--untracked-files=all"], capture_output=True, text=True).stdout
        self.assertEqual(sorted(line[3:] for line in status.splitlines()), sorted(RULE_FILES + KEEP_FILES))

    def test_check_accepts_tests_appended_to_an_existing_test_file(self):
        self.commit_old_test()
        self.repo.write("test/old.test.js", self.OLD_TEST + self.APPENDED_RULE)
        code, out = self.check_old_test()
        self.assertEqual(code, 0, out)
        self.assertIn("AC-001: rule now=fail", out)
        self.assertNotIn("対応する AC が無い", out)
        self.assertNotIn("AC-ID を書かない", out)

    def test_check_accepts_a_name_added_to_an_existing_import_line(self):
        self.commit_old_test()
        widened = self.OLD_TEST.replace("import { existing } from './harness/existing.js';", "import { existing, more } from './harness/existing.js';")
        self.repo.write("test/old.test.js", widened + self.APPENDED_RULE)
        code, out = self.check_old_test()
        self.assertNotIn("existing:", out)

    def test_check_accepts_tests_appended_to_a_file_that_ends_without_a_newline(self):
        (self.root / "test/a.rule.test.js").unlink()
        self.repo.write("test/old.test.js", self.OLD_TEST.rstrip("\n"))
        self.repo.commit("old test", "test/old.test.js")
        self.repo.write("test/old.test.js", self.OLD_TEST + self.APPENDED_RULE)
        code, out = self.check_old_test()
        self.assertEqual(code, 0, out)

    def test_check_refuses_a_changed_line_of_an_existing_test_file(self):
        self.commit_old_test()
        self.repo.write("test/old.test.js", self.OLD_TEST.replace("existing, true", "existing, !false") + self.APPENDED_RULE)
        code, out = self.check_old_test()
        self.assertEqual(code, 1)
        self.assertIn("existing: test/old.test.js の既存の行を 1 行、変えるか消している (最初の行: assert.equal(existing, true);)", out)

    def test_check_accepts_a_rewritten_existing_test_that_is_declared_with_a_reason_and_the_report_lists_it(self):
        self.commit_old_test()
        self.repo.write("test/old.test.js", self.OLD_TEST.replace("existing, true", "existing, !false") + self.APPENDED_RULE)
        code, out = self.check_old_test(rewrites=[{"file": "test/old.test.js", "reason": "R-1 が古い期待を変える"}])
        self.assertEqual(code, 0, out)
        code, answer = run("report", str(self.root))
        self.assertIn("書き直した既存のテスト:\ntest/old.test.js: R-1 が古い期待を変える\n", answer)

    def test_check_refuses_a_file_in_a_directory_that_is_not_at_head(self):
        self.repo.write("test/fresh/extra.txt", "extra")
        code, out = self.check(keep=[*KEEP_FILES, "test/fresh/extra.txt"])
        self.assertEqual(code, 1)
        self.assertIn("place: test/fresh/ は HEAD に無い", out)

    def test_check_accepts_a_new_directory_that_is_declared_with_a_reason_and_the_report_lists_it(self):
        self.repo.write("test/fresh/extra.txt", "extra")
        code, out = self.check(keep=[*KEEP_FILES, "test/fresh/extra.txt"], new_dirs=[{"path": "test/fresh/", "reason": "src/fresh/ を写す"}])
        self.assertEqual(code, 0, out)
        code, answer = run("report", str(self.root))
        self.assertIn("新しく作ったディレクトリ:\ntest/fresh: src/fresh/ を写す\n", answer)

    def test_check_refuses_a_new_directory_declared_without_a_reason(self):
        self.repo.write("test/fresh/extra.txt", "extra")
        code, out = self.check(keep=[*KEEP_FILES, "test/fresh/extra.txt"], new_dirs=[{"path": "test/fresh"}])
        self.assertEqual(code, 1)
        self.assertIn("new_dirs: test/fresh の理由が無い", out)

    def test_check_refuses_a_criterion_without_a_kind_mark(self):
        self.repo.write("plan.md", PLAN.replace("- AC-001: [規則] ", "- AC-001: "))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("plan: AC-001 の行に種類の印", out)

    def test_report_with_a_plan_path_answers_before_any_check(self):
        code, answer = run("report", str(self.root), "plan.md")
        self.assertEqual(code, 0, answer)
        self.assertIn("テストを確かめた AC: 無い", answer)

    def test_report_without_a_checked_plan_fails_and_the_last_line_states_the_exit_code(self):
        code, out = run("report", str(self.root))
        self.assertEqual(code, 1)
        self.assertTrue(out.endswith("exit: 1\n"))

    def test_check_accepts_a_rule_whose_implementation_is_at_head_when_it_is_declared_and_the_report_lists_it(self):
        self.repo.write("src/a.js", "export const f = () => 1;\n")
        self.repo.commit("impl", "src/a.js")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn('"implemented" に挙げる', out)
        code, out = self.check(implemented=["AC-001"])
        self.assertEqual(code, 0, out)
        self.assertIn("AC-001: rule implemented now=pass", out)
        code, answer = run("report", str(self.root))
        self.assertIn("実装の後に確かめた基準 (実装の前に落ちることは確かめていない):\nAC-001\n", answer)

    def test_check_refuses_a_non_impact_criterion_declared_as_implemented(self):
        code, out = self.check(implemented=["AC-002"])
        self.assertEqual(code, 1)
        self.assertIn("implemented: AC-002", out)

    def test_check_leaves_no_report_file_in_the_repo(self):
        self.check()
        self.assertEqual([path.name for path in self.root.iterdir() if path.name.startswith(".define-done-report")], [])

    def test_check_refuses_ac_ids_in_test_code(self):
        self.repo.write("test/a.rule.test.js", RULE_TEST.replace("'f returns 1'", "'AC-001 f returns 1'"))
        code, out = self.check(tests=[("AC-001", "test/a.rule.test.js", "AC-001 f returns 1"), TESTS[1]])
        self.assertEqual(code, 1)
        self.assertIn("AC-ID を書かない", out)

    def test_check_refuses_a_test_without_a_criterion(self):
        self.repo.write("test/a.rule.test.js", RULE_TEST + "test('f is a function', () => assert.equal(typeof f, 'function'));\n")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("対応する AC が無いテスト「f is a function」", out)

    def test_check_refuses_a_criterion_whose_test_name_does_not_match(self):
        code, out = self.check(tests=[("AC-001", "test/a.rule.test.js", "f returns one"), TESTS[1]])
        self.assertEqual(code, 1)
        self.assertIn("missing: AC-001", out)

    def test_check_refuses_a_rule_test_that_already_passes(self):
        before = self.head()
        self.repo.write("plan.md", plan_text([("AC-001", "規則"), ("AC-002", "規則")]))
        code, out = self.check(["test/a.rule.test.js", "test/a.keep.test.js"], ["test/golden/g.txt", "test/harness/app.js", "plan.md"])
        self.assertEqual(code, 1)
        self.assertIn("kind: AC-002", out)
        self.assertEqual(self.head(), before)

    def test_check_refuses_a_non_impact_test_that_fails(self):
        before = self.head()
        self.repo.write("plan.md", plan_text([("AC-001", "非影響"), ("AC-002", "非影響")]))
        code, out = self.check([], ["test/a.rule.test.js", *KEEP_FILES])
        self.assertEqual(code, 1)
        self.assertIn("kind: AC-001", out)
        self.assertEqual(self.head(), before)

    def test_check_refuses_a_command_without_report_output(self):
        code, out = self.check(command="node --test")
        self.assertEqual(code, 1)
        self.assertIn("{report}", out)


    def test_check_refuses_a_test_that_never_ran(self):
        self.repo.write("test/a.rule.test.js", RULE_TEST.replace("./harness/app.js", "./harness/missing.js"))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("missing: AC-001", out)

    def test_a_passing_test_of_the_same_name_in_another_file_is_not_counted(self):
        self.repo.write("test/old.test.js", "import { test } from 'node:test';\ntest('f returns 1', () => {});\n")
        self.repo.commit("old test with the same name", "test/old.test.js")
        command = REPORT_COMMAND.replace("test/a.keep.test.js", "test/a.keep.test.js test/old.test.js")
        code, out = self.check(command=command)
        self.assertEqual(code, 0, out)
        self.assertIn("AC-001: rule now=fail", out)


    def stash_list(self):
        return subprocess.run(["git", "-C", str(self.root), "stash", "list", "--format=%H"], capture_output=True, text=True).stdout.split()

    def write_implementation_in_tree(self):
        self.repo.write("src/a.js", "import { one } from './one.js';\nexport const f = () => one;\n")
        self.repo.write("src/one.js", "export const one = 1;\n")

    def test_check_sets_aside_changes_outside_the_given_files_and_restores_them(self):
        self.write_implementation_in_tree()
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("AC-001: rule now=fail", out)
        self.assertEqual((self.root / "src/a.js").read_text(), "import { one } from './one.js';\nexport const f = () => one;\n")
        self.assertEqual((self.root / "src/one.js").read_text(), "export const one = 1;\n")
        self.assertEqual(self.stash_list(), [])

    def test_check_with_nothing_outside_the_given_files_leaves_an_existing_stash_alone(self):
        self.repo.write("notes.txt", "draft\n")
        self.repo.git("stash", "push", "-q", "--include-untracked", "--", "notes.txt")
        before = self.stash_list()
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.stash_list(), before)
        self.assertFalse((self.root / "notes.txt").exists())

    def test_check_that_sets_aside_changes_keeps_an_existing_stash(self):
        self.repo.write("notes.txt", "draft\n")
        self.repo.git("stash", "push", "-q", "--include-untracked", "--", "notes.txt")
        before = self.stash_list()
        self.write_implementation_in_tree()
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.stash_list(), before)
        self.assertTrue((self.root / "src/one.js").exists())

    def test_refused_check_restores_changes_outside_the_given_files(self):
        self.write_implementation_in_tree()
        before = self.head()
        code, out = self.check(tests=[("AC-001", "test/a.rule.test.js", "f returns one"), TESTS[1]])
        self.assertEqual(code, 1)
        self.assertEqual(self.head(), before)
        self.assertTrue((self.root / "src/one.js").exists())
        self.assertEqual(self.stash_list(), [])

    def test_check_keeps_the_set_aside_changes_in_the_stash_when_it_cannot_restore_them(self):
        self.write_implementation_in_tree()
        original = check_done.run_tests

        def locking_run_tests(cwd, command):
            result = original(cwd, command)
            if self.stash_list():
                (self.root / ".git" / "index.lock").write_text("")
            return result

        check_done.run_tests = locking_run_tests
        try:
            code, out = self.check()
        finally:
            check_done.run_tests = original
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
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=patch))
        self.assertEqual(code, 0, out)
        self.assertIn("AC-001: rule spike=pass now=fail", out)
        self.assertIn("AC-002: non-impact spike=pass now=pass", out)
        self.assertEqual((self.root / "src/a.js").read_text(), "export const f = () => 0;\n")
        self.assertFalse((self.root / "src/one.js").exists())

    def test_spike_keeps_an_implementation_in_progress(self):
        patch = self.spike_patch()
        self.repo.write("src/a.js", "export const f = () => 0; // wip\n")
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=patch))
        self.assertEqual(code, 0, out)
        self.assertEqual((self.root / "src/a.js").read_text(), "export const f = () => 0; // wip\n")
        self.assertEqual(self.stash_list(), [])

    def test_spike_that_does_not_pass_the_rule_tests_refuses_the_check(self):
        patch = self.spike_patch(body="export const f = () => 2;\n")
        before = self.head()
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=patch))
        self.assertEqual(code, 1)
        self.assertIn("spike: AC-001", out)
        self.assertEqual(self.head(), before)
        self.assertEqual((self.root / "src/a.js").read_text(), "export const f = () => 0;\n")

    def test_spike_patch_that_touches_a_given_file_is_refused(self):
        self.repo.write("test/harness/app.js", HARNESS + "export const extra = 1;\n")
        self.repo.git("add", "-N", "test/harness/app.js")
        diff = subprocess.run(["git", "-C", str(self.root), "diff", "--", "test/harness/app.js"], capture_output=True, text=True, check=True).stdout
        self.repo.git("reset", "-q", "--", "test/harness/app.js")
        self.repo.write("test/harness/app.js", HARNESS)
        path = Path(self.tmp.name) / "bad.patch"
        path.write_text(diff, encoding="utf-8")
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=str(path)))
        self.assertEqual(code, 1)
        self.assertIn("spike:", out)

    def test_spike_without_a_patch_file_is_refused(self):
        missing = str(Path(self.tmp.name) / "none.patch")
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=missing))
        self.assertEqual(code, 1)
        self.assertIn("spike:", out)

    def test_failing_check_command_refuses_the_check(self):
        before = self.head()
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, check_command="node -e \"process.exit(3)\""))
        self.assertEqual(code, 1)
        self.assertIn("check:", out)
        self.assertEqual(self.head(), before)

    def test_check_command_runs_on_the_tree_with_the_trial_implementation(self):
        patch = self.spike_patch()
        check = "node -e \"import('./src/a.js').then((m) => process.exit(m.f() === 1 ? 0 : 1))\""
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=patch, check_command=check))
        self.assertEqual(code, 0, out)
        self.assertIn("check: pass", out)

    def test_unmatched_test_name_lists_the_tests_that_ran_in_that_file(self):
        code, out = self.check(tests=[("AC-001", "test/a.rule.test.js", "suite > f returns 1"), TESTS[1]])
        self.assertEqual(code, 1)
        self.assertIn("missing: AC-001", out)
        self.assertIn("f returns 1", out.split("missing: AC-001")[1].splitlines()[0])


    def refused_plan(self, text):
        self.repo.write("plan.md", text)
        before = self.head()
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertEqual(self.head(), before)
        return out

    def test_check_refuses_a_plan_whose_gate_is_not_ready(self):
        out = self.refused_plan(plan_text([("AC-001", "規則"), ("AC-002", "非影響")], gate="blocked (D1 が R-1 と矛盾する)"))
        self.assertIn("plan: Gate が ready でない", out)

    def test_check_refuses_ac_ids_that_differ_from_the_criteria(self):
        out = self.refused_plan(plan_text([("AC-001", "規則"), ("AC-002", "非影響")], ids="AC-001", rows=["| R-1 | AC-001 |"]))
        self.assertIn("plan: `- AC IDs:`", out)
        self.assertIn("AC-002", out)

    def test_check_refuses_a_test_whose_criterion_is_not_in_the_plan(self):
        out = self.refused_plan(plan_text([("AC-001", "規則")]))
        self.assertIn("plan: テストを対応させた AC-002", out)


    def test_check_refuses_a_source_that_is_not_a_requirement(self):
        out = self.refused_plan(plan_text([("AC-001", "規則", "R-1, R-9"), ("AC-002", "非影響")]))
        self.assertIn("plan: AC-001 の出典 R-9", out)

    def test_check_refuses_a_requirement_row_whose_criteria_do_not_cite_it(self):
        rows = ["| R-1 | AC-001 |", "| R-2 | AC-002 (推奨の帰結を観測する) |"]
        out = self.refused_plan(plan_text([("AC-001", "規則"), ("AC-002", "非影響")], rows=rows, requirements=("R-1", "R-2")))
        self.assertIn("plan: 要求の表は R-2 を AC-002 に対応させているが", out)
        self.assertNotIn("R-1 を", out)

    def test_check_refuses_a_requirement_missing_from_the_table(self):
        out = self.refused_plan(plan_text([("AC-001", "規則"), ("AC-002", "非影響")], requirements=("R-1", "R-2")))
        self.assertIn("plan: R-2 が `## MECE Review` の要求の表に無い", out)

    def test_check_refuses_a_requirement_row_without_a_criterion_or_a_label(self):
        rows = ["| R-1 | AC-001, AC-002 |", "| R-2 | 実装で確かめる |"]
        out = self.refused_plan(plan_text([("AC-001", "規則"), ("AC-002", "非影響")], rows=rows, requirements=("R-1", "R-2")))
        self.assertIn("plan: 要求の表の R-2 の行", out)

    def test_check_accepts_unverified_and_out_of_scope_rows_and_a_row_naming_a_related_criterion(self):
        rows = [
            "| R-1 | AC-001 (値が user の id であることは AC-002 の観測に現れる) |",
            "| R-2 | 未検証: 外から観測する手段が無い |",
            "| R-3 | 範囲外: 規約として enforce-conventions で担保する (描画の結果は AC-002 で守る) |",
            "| R-4 | 不足情報: 上限の値を資料が決めていない (既定: 決めない、行き先: 要求の持ち主) |",
        ]
        criteria = [("AC-001", "規則"), ("AC-002", "非影響", "test/b.test.js")]
        self.repo.write("plan.md", plan_text(criteria, rows=rows, requirements=("R-1", "R-2", "R-3", "R-4")))
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_check_reads_a_plan_outside_the_repo(self):
        (self.root / "plan.md").unlink()
        outside = Path(self.tmp.name) / "489-registration" / "design.md"
        outside.parent.mkdir()
        outside.write_text(PLAN, encoding="utf-8")
        keep = [path for path in KEEP_FILES if path != "plan.md"]
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, keep, TESTS))
        self.assertEqual(code, 1)
        self.assertIn("plan: 計画が渡したファイルに無い", out)
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, keep, TESTS, plan=str(outside)))
        self.assertEqual(code, 0, out)


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

    def test_spike_close_writes_a_patch_of_the_trial_implementation_only_and_check_accepts_it(self):
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
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=str(patch)))
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

    def test_check_refuses_a_plan_whose_decisions_changed_after_spike_open(self):
        patch = self.spike_patch_with_plan(lambda plan: plan.replace("- D1: f が 1 を返す", "- D1: f が定数 ONE を返す"))
        before = self.head()
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=patch))
        self.assertEqual(code, 1)
        self.assertIn("plan: 計画の 4 節の外が `spike-open` の後に変わっている", out)
        self.assertIn("検査が拒んだ決定", out)
        self.assertEqual(self.head(), before)

    def test_check_accepts_a_plan_that_records_the_rejected_decision_in_the_review(self):
        patch = self.spike_patch_with_plan(lambda plan: plan + self.REJECTED_DECISION)
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, KEEP_FILES, TESTS, spike=patch))
        self.assertEqual(code, 0, out)
        code, out = run("report", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("検査が拒んだ決定:\n| D1 | lint の no-magic が 1 を拒んだ | 定数 ONE を返す |", out)

    def test_patch_with_the_plan_baseline_still_applies_as_a_starting_point(self):
        patch = self.spike_patch_with_plan(lambda plan: plan)
        self.assertTrue(Path(patch).read_text().startswith("Define-Done-Plan-Outside: "))
        self.repo.git("apply", patch)
        self.assertEqual((self.root / "src/a.js").read_text(), "export const f = () => 1;\n")


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
        self.check()
        code, answer = run("report", str(self.root))
        self.assertEqual(code, 0, answer)
        self.assertIn("要求:\n- R-1: f は 1 を返す (「f は 1 を返す」 依頼)\n- R-2: f は 1 を返す (「f は 1 を返す」 依頼)\n", answer)
        self.assertIn("Gate: ready\n", answer)
        self.assertIn("AC: 規則 1 件、非影響 1 件\n", answer)
        self.assertIn("テストを確かめた AC: AC-001, AC-002\n", answer)
        self.assertIn("ファイル: test/a.rule.test.js, test/a.keep.test.js, test/golden/g.txt, test/harness/app.js\n", answer)
        self.assertIn("基準の無い要求:\n| R-2 | 範囲外: 規約として enforce-conventions で担保する |\n", answer)
        self.assertIn("実装が足すテスト:\n| 空の入力で落ちる | 実装のテスト: 空の入力で 0 を返す |\n", answer)
        self.assertIn("未検証:\n| 本番の時計がずれる | 未検証: staging の log |\n", answer)
        self.assertNotIn("f が負の数を返す", answer)
        self.assertNotIn("検査が拒んだ決定", answer)

    def test_report_still_answers_after_the_implementation_is_committed(self):
        self.repo.write("plan.md", self.REPORTED_PLAN)
        self.check()
        self.implement()
        code, out = run("report", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("要求:\n- R-1: f は 1 を返す (「f は 1 を返す」 依頼)\n", out)
        self.assertIn("AC: 規則 1 件、非影響 1 件\n", out)
        self.assertIn("テストを確かめた AC: AC-001, AC-002\n", out)
        self.assertIn("実装が足すテスト:\n| 空の入力で落ちる | 実装のテスト: 空の入力で 0 を返す |\n", out)

    def test_report_reads_a_plan_outside_the_repo_from_the_given_path(self):
        outside = Path(self.tmp.name) / "plans" / "design.md"
        outside.parent.mkdir()
        outside.write_text(self.REPORTED_PLAN, encoding="utf-8")
        (self.root / "plan.md").unlink()
        keep = [path for path in KEEP_FILES if path != "plan.md"]
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, keep, TESTS, plan=str(outside)))
        self.assertEqual(code, 0, out)
        code, out = run("report", str(self.root), str(outside))
        self.assertEqual(code, 0, out)
        self.assertIn("要求:\n- R-1: ", out)


    GROUND_REVIEWED_PLAN = REPORTED_PLAN.replace(
        "## Ground Review\n\n無い\n",
        "## Ground Review\n\n### 重要なリスクと影響\n\n- f が負の数を返す\n\n### 未決の判断\n\n- 上限の値。既定は決めない。行き先は仕様の持ち主\n\n### 未検証の結論\n\n- 実 browser の応答の形\n  - endpoint ができてから確かめる\n",
    ) + "\n### 指摘\n\n- 確認済み: 全 R-n が基準に対応する\n- 未検証: staging の設定\n"

    def test_report_lists_the_open_decisions_and_unverified_conclusions_of_the_ground_review(self):
        self.repo.write("plan.md", self.GROUND_REVIEWED_PLAN)
        self.check()
        code, out = run("report", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("未決の判断:\n- 上限の値。既定は決めない。行き先は仕様の持ち主\n", out)
        self.assertIn("未検証:\n- 実 browser の応答の形\n  - endpoint ができてから確かめる\n- 未検証: staging の設定\n| 本番の時計がずれる | 未検証: staging の log |\n", out)
        self.assertNotIn("確認済み", out)
        self.assertNotIn("重要なリスク", out)

    def test_report_omits_ground_review_subsections_that_say_there_is_nothing(self):
        plan = self.GROUND_REVIEWED_PLAN.replace("- 上限の値。既定は決めない。行き先は仕様の持ち主", "- 無い").replace("- 実 browser の応答の形\n  - endpoint ができてから確かめる", "なし (grilling で確定済み)")
        self.repo.write("plan.md", plan)
        self.check()
        code, out = run("report", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertNotIn("未決の判断", out)
        self.assertIn("未検証:\n- 未検証: staging の設定\n", out)
        self.assertNotIn("grilling", out)


    def residual_risk_plan(self, destination):
        return PLAN + f"\n### 残ったリスクの表\n\n| リスク | 守る先 |\n|---|---|\n| f が負の数を返す | AC-001, AC-002 |\n| 設定の名前がずれる | 規約 |\n| g の文が変わる | {destination} |\n"

    def test_check_refuses_a_residual_risk_whose_destination_is_not_a_known_form(self):
        before = self.head()
        self.repo.write("plan.md", self.residual_risk_plan("`test/a.keep.test.js` の恒久の規則"))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("plan: 残ったリスクの表の「g の文が変わる」の守る先", out)
        self.assertIn("既存のテスト:", out)
        self.assertNotIn("f が負の数を返す", out)
        self.assertNotIn("設定の名前がずれる", out)
        self.assertEqual(self.head(), before)

    def test_check_accepts_a_residual_risk_guarded_by_an_existing_test(self):
        self.repo.write("plan.md", self.residual_risk_plan("既存のテスト: test/a.keep.test.js"))
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_check_refuses_a_residual_risk_guarded_by_a_criterion_that_is_not_in_the_plan(self):
        self.repo.write("plan.md", self.residual_risk_plan("AC-009"))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("plan: 残ったリスクの表の「g の文が変わる」の守る先 AC-009 が", out)

    def test_spike_close_refuses_a_directory_that_spike_open_did_not_make(self):
        code, out = run("spike-close", str(self.root), str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("spike:", out)
        self.assertTrue((self.root / "src/a.js").exists())


    TWO_TESTS = RULE_TEST + "test('f is not 0', () => assert.notEqual(f(), 0));\n"


    def outside_state(self):
        return [
            subprocess.run(["git", "-C", str(self.root), *args, "--", "src"], capture_output=True, text=True, check=True).stdout
            for args in (["status", "--porcelain", "--untracked-files=all"], ["diff", "--cached"], ["diff"])
        ]

    def stage_every_kind_of_change(self):
        for name in ("c", "d", "e"):
            self.repo.write(f"src/{name}.js", f"export const {name} = 0;\n")
        self.repo.commit("more", "src")
        self.repo.git("mv", "src/b.js", "src/renamed.js")
        self.repo.git("rm", "-q", "src/c.js")
        self.repo.git("rm", "-q", "--cached", "src/d.js")
        self.repo.write("src/e.js", "export const e = 1;\n")
        self.repo.git("add", "src/e.js")
        self.repo.write("src/e.js", "export const e = 2;\n")
        self.repo.write("src/added.js", "export const added = 1;\n")
        self.repo.git("add", "src/added.js")

    def test_check_sets_aside_staged_renames_and_deletions_and_restores_the_index(self):
        self.stage_every_kind_of_change()
        before = self.outside_state()
        self.assertIn("R  src/b.js -> src/renamed.js", before[0])
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("AC-002: non-impact now=pass", out)
        self.assertEqual(self.outside_state(), before)
        self.assertEqual(self.stash_list(), [])

    def test_refused_check_restores_staged_renames_and_deletions(self):
        self.stage_every_kind_of_change()
        before = self.outside_state()
        code, out = self.check(tests=[("AC-001", "test/a.rule.test.js", "f returns one"), TESTS[1]])
        self.assertEqual(code, 1)
        self.assertIn("missing: AC-001", out)
        self.assertEqual(self.outside_state(), before)
        self.assertEqual(self.stash_list(), [])

    def test_check_restores_a_change_that_is_only_in_the_index(self):
        self.repo.write("src/b.js", "export const g = () => 'staged';\n")
        self.repo.git("add", "src/b.js")
        self.repo.write("src/b.js", "export const g = () => 'kept';\n")
        before = self.outside_state()
        self.assertIn("MM src/b.js", before[0])
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.outside_state(), before)
        self.assertEqual(self.stash_list(), [])

    def test_check_with_only_an_index_deletion_outside_it_runs_on_the_head_tree(self):
        self.repo.git("rm", "-q", "--cached", "src/b.js")
        before = self.outside_state()
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.outside_state(), before)
        self.assertEqual(self.stash_list(), [])

    def test_check_drops_the_stash_that_a_failed_set_aside_left_with_the_tree_untouched(self):
        self.write_implementation_in_tree()
        before = self.outside_state()
        original = check_done.git

        def failing_after_storing(repo, *args):
            if args[:2] == ("stash", "push"):
                original(repo, "stash", "store", "-q", "-m", "left behind", original(repo, "stash", "create").strip())
                raise RuntimeError("fatal: pathspec did not match any files")
            return original(repo, *args)

        check_done.git = failing_after_storing
        try:
            code, out = self.check()
        finally:
            check_done.git = original
        self.assertEqual(code, 1)
        self.assertIn("git: fatal: pathspec", out)
        self.assertEqual(self.outside_state(), before)
        self.assertEqual(self.stash_list(), [])

    def test_missing_test_with_changes_set_aside_points_to_what_the_given_files_rely_on(self):
        self.write_implementation_in_tree()
        code, out = self.check(tests=[("AC-001", "test/a.rule.test.js", "f returns one"), TESTS[1]])
        self.assertEqual(code, 1)
        self.assertIn("missing: 渡したファイルの外の変更 (2 件) は退避して流している", out)
        code, out = self.check(tests=[("AC-001", "test/a.rule.test.js", "f returns one"), TESTS[1]])
        self.assertEqual(code, 1)
        self.repo.git("checkout", "--", "src/a.js")
        (self.root / "src/one.js").unlink()
        code, out = self.check(tests=[("AC-001", "test/a.rule.test.js", "f returns one"), TESTS[1]])
        self.assertNotIn("退避して流している", out)

    def test_check_refuses_a_requirement_that_only_says_a_check_command_passes(self):
        plan = plan_text([("AC-001", "規則"), ("AC-002", "非影響")], rows=["| R-1 | AC-001, AC-002 |", "| R-2 | 範囲外: 規約として enforce-conventions で担保する |"], requirements=("R-1", "R-2"))
        self.repo.write("plan.md", plan.replace("- R-2: f は 1 を返す (「f は 1 を返す」 依頼)", "- R-2: `npm run check` が通る (「`npm run check` が通る」 issue#1)"))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("plan: R-2 は検査コマンドが通ることだけを述べている", out)
        self.assertNotIn("R-1 は", out)

    def test_check_refuses_a_requirement_that_says_what_is_not_built_yet(self):
        plan = plan_text([("AC-001", "規則"), ("AC-002", "非影響")], rows=["| R-1 | AC-001, AC-002 |", "| R-2 | 範囲外: 規約として enforce-conventions で担保する |"], requirements=("R-1", "R-2"))
        for text in ("画面はまだ作らない", "管理画面での一覧は今回は作らない"):
            self.repo.write("plan.md", plan.replace("- R-2: f は 1 を返す (「f は 1 を返す」 依頼)", f"- R-2: {text} (「{text} (#2)。」 issue#1)"))
            code, out = self.check()
            self.assertEqual(code, 1, text)
            self.assertIn("plan: R-2 は今回は作らないものを述べている", out)

    def test_check_accepts_requirements_that_state_outcomes_with_similar_words(self):
        plan = plan_text([("AC-001", "規則"), ("AC-002", "非影響")], sources="R-1, R-2, R-3", rows=["| R-1 | AC-001, AC-002 |", "| R-2 | AC-001 |", "| R-3 | AC-001 |"], requirements=("R-1", "R-2", "R-3"))
        plan = plan.replace("- R-2: f は 1 を返す (「f は 1 を返す」 依頼)", "- R-2: 許可した `https://app.example.com` は検査を通る (「許可した origin は通る」 依頼)")
        plan = plan.replace("- R-3: f は 1 を返す (「f は 1 を返す」 依頼)", "- R-3: まだ有効な招待があれば新しい招待を作らない (「有効な招待があれば作らない」 依頼)")
        self.repo.write("plan.md", plan)
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def check_with_plan_outside(self):
        outside = Path(self.tmp.name) / "plans" / "design.md"
        outside.parent.mkdir()
        outside.write_text(self.REPORTED_PLAN, encoding="utf-8")
        (self.root / "plan.md").unlink()
        keep = [path for path in KEEP_FILES if path != "plan.md"]
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, keep, TESTS, plan=str(outside)))
        self.assertEqual(code, 0, out)
        return outside

    def test_report_finds_the_plan_outside_the_repo_that_the_check_was_given(self):
        self.check_with_plan_outside()
        code, out = run("report", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("要求:\n- R-1: ", out)


    def test_report_without_a_path_fails_once_the_remembered_plan_is_gone(self):
        self.check_with_plan_outside().unlink()
        code, out = run("report", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("plan: ", out)

    def test_spike_open_names_the_ignored_env_files_that_the_worktree_lacks(self):
        self.repo.write(".gitignore", ".env*\n!.env.example\n")
        self.repo.write(".env.example", "DATABASE_URL=\n")
        self.repo.commit("ignore", ".gitignore", ".env.example")
        code, out = run("spike-open", str(self.root), "test/a.rule.test.js", "test/harness/app.js")
        self.assertEqual(code, 0, out)
        self.addCleanup(shutil.rmtree, Path(out.split("worktree: ")[1].splitlines()[0]).parent, True)
        self.assertNotIn("env:", out)
        self.repo.write(".env", "DATABASE_URL=postgres://localhost/test\n")
        self.repo.write(".env.test", "DATABASE_URL=postgres://localhost/test\n")
        code, out = run("spike-open", str(self.root), "test/a.rule.test.js", "test/harness/app.js")
        self.assertEqual(code, 0, out)
        self.addCleanup(shutil.rmtree, Path(out.split("worktree: ")[1].splitlines()[0]).parent, True)
        self.assertIn("env: .env, .env.test は複製に無い", out)


    BODIES = {"AC-001": "f は 1 を返す", "AC-002": "g は変わらない"}
    NAMED_PLAN = plan_text([("AC-001", "規則"), ("AC-002", "非影響")], bodies=BODIES)


    NEW_HARNESS = "export { one } from '../../src/one.js';\n"
    RULE_TEST_ON_NEW_MODULE = "import { test } from 'node:test';\nimport assert from 'node:assert/strict';\nimport { f } from './harness/app.js';\nimport { one } from './harness/new.js';\ntest('f returns 1', () => assert.equal(f(), one));\n"

    def write_rule_test_on_a_module_that_head_lacks(self):
        self.repo.write("test/harness/new.js", self.NEW_HARNESS)
        self.repo.write("test/a.rule.test.js", self.RULE_TEST_ON_NEW_MODULE)


    def test_check_counts_a_rule_test_that_cannot_load_before_the_change_as_failing_when_it_passes_with_the_trial_implementation(self):
        patch = self.spike_patch()
        self.write_rule_test_on_a_module_that_head_lacks()
        keep = [*KEEP_FILES, "test/harness/new.js"]
        code, out = run("check", str(self.root), stdin=check_spec(REPORT_COMMAND, RULE_FILES, keep, TESTS, spike=patch))
        self.assertEqual(code, 0, out)
        self.assertIn("unloaded: AC-001", out)
        self.assertIn("AC-001: rule spike=pass now=fail", out)
        self.assertFalse((self.root / "src/one.js").exists())

    def test_check_refuses_a_rule_test_that_cannot_load_when_no_tree_shows_it_passing(self):
        self.write_rule_test_on_a_module_that_head_lacks()
        code, out = self.check(keep=[*KEEP_FILES, "test/harness/new.js"])
        self.assertEqual(code, 1)
        line = next(line for line in out.splitlines() if line.startswith("missing: AC-001"))
        self.assertIn("spike", line)


RSPEC_HARNESS = "require_relative '../../../lib/a'\n"
RSPEC_RULE = "require 'rspec'\nrequire_relative 'harness/app'\nRSpec.describe 'f' do\n  it 'returns 1' do\n    expect(F.call).to eq(1)\n  end\nend\n"
RSPEC_KEEP = "require 'rspec'\nrequire_relative 'harness/app'\nRSpec.describe 'g' do\n  it 'keeps its text' do\n    expect(G.call).to eq('kept')\n  end\nend\n"


class ReportTest(unittest.TestCase):


    def mapped(self, report, file, name):
        test = {"ac": "AC-001", "file": file, "name": name}
        return check_done.states_by_ac(check_done.parse_report(report), [test])

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
    def test_check_with_rspec(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = Repo(root)
            repo.write("lib/a.rb", "F = -> { 0 }\nG = -> { 'kept' }\n")
            repo.write("spec/acceptance/harness/existing.rb", "")
            repo.commit("lib")
            repo.write("spec/acceptance/harness/app.rb", RSPEC_HARNESS)
            repo.write("spec/acceptance/a_rule_spec.rb", RSPEC_RULE)
            repo.write("spec/acceptance/a_keep_spec.rb", RSPEC_KEEP)
            repo.write("plan.md", PLAN)
            command = "rspec spec/acceptance/a_rule_spec.rb spec/acceptance/a_keep_spec.rb --format json --out {report}"
            tests = [("AC-001", "spec/acceptance/a_rule_spec.rb", "returns 1"), ("AC-002", "spec/acceptance/a_keep_spec.rb", "keeps its text")]
            code, out = run("check", str(root), stdin=check_spec(command, ["spec/acceptance/a_rule_spec.rb"], ["spec/acceptance/a_keep_spec.rb", "spec/acceptance/harness/app.rb", "plan.md"], tests))
            self.assertEqual(code, 0, out)
            self.assertIn("AC-001: rule now=fail", out)
            self.assertIn("AC-002: non-impact now=pass", out)


if __name__ == "__main__":
    unittest.main()
