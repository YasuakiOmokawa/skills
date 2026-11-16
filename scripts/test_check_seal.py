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


def seal_spec(command, rule=(), non_impact=(), supersedes="", subject="test: plan.md の受け入れテスト"):
    return json.dumps({"test_command": command, "rule": list(rule), "non_impact": list(non_impact), "supersedes": supersedes, "subject": subject})


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
RULE_TEST = "import { test } from 'node:test';\nimport assert from 'node:assert/strict';\nimport { f } from './harness/app.js';\ntest('AC-001 f returns 1', () => assert.equal(f(), 1));\n"
KEEP_TEST = "import { test } from 'node:test';\nimport assert from 'node:assert/strict';\nimport { g, expected } from './harness/app.js';\ntest('AC-002 g keeps its text', () => assert.equal(g(), expected('g.txt')));\n"
RULE_FILES = ["test/a.rule.test.js"]
KEEP_FILES = ["test/a.keep.test.js", "test/golden/g.txt", "test/harness/app.js", "plan.md"]


class SealCommandTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.repo = Repo(self.root)
        self.repo.write("src/b.js", "export const g = () => 'kept';\n")
        self.repo.commit("b")
        self.write_plan_files()

    def tearDown(self):
        self.tmp.cleanup()

    def write_plan_files(self, rule=RULE_TEST, keep=KEEP_TEST):
        self.repo.write("test/harness/app.js", HARNESS)
        self.repo.write("test/golden/g.txt", "kept")
        self.repo.write("test/a.rule.test.js", rule)
        self.repo.write("test/a.keep.test.js", keep)
        self.repo.write("plan.md", "# plan\n")

    def seal(self, rule=RULE_FILES, keep=KEEP_FILES):
        return run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND, rule, keep))

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

    def test_seal_commits_kinds_and_files_as_trailers(self):
        code, out = self.seal()
        self.assertEqual(code, 0, out)
        body = self.body()
        self.assertIn("Define-Done-Seal: AC-001, AC-002", body)
        self.assertIn("Define-Done-Rule: AC-001\n", body)
        self.assertIn("Define-Done-Rule-Files: test/a.rule.test.js\n", body)
        self.assertIn("Define-Done-Files: test/a.rule.test.js, test/a.keep.test.js, test/golden/g.txt, test/harness/app.js, plan.md", body)
        code, out = run("check", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("rule: AC-001", out)

    def test_seal_refuses_a_rule_test_that_already_passes(self):
        before = self.head()
        code, out = self.seal(["test/a.rule.test.js", "test/a.keep.test.js"], ["test/golden/g.txt", "test/harness/app.js", "plan.md"])
        self.assertEqual(code, 1)
        self.assertIn("kind: AC-002", out)
        self.assertEqual(self.head(), before)

    def test_seal_refuses_a_non_impact_test_that_fails(self):
        before = self.head()
        code, out = self.seal([], ["test/a.rule.test.js", *KEEP_FILES])
        self.assertEqual(code, 1)
        self.assertIn("kind: AC-001", out)
        self.assertEqual(self.head(), before)

    def test_seal_refuses_a_command_without_junit_output(self):
        code, out = run("seal", str(self.root), stdin=seal_spec("node --test", RULE_FILES, KEEP_FILES))
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

    def test_golden_file_in_the_seal_is_protected(self):
        self.seal()
        self.repo.write("test/golden/g.txt", "changed")
        self.repo.commit("edit golden")
        code, out = run("check", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("tamper:", out)
        self.assertIn("test/golden/g.txt", out)

    def test_verify_passes_when_rule_turns_green_and_non_impact_stays_green(self):
        self.seal()
        self.implement()
        code, out = run("verify", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("AC-001: rule sealed=fail current=pass", out)
        self.assertIn("AC-002: non-impact sealed=pass current=pass", out)

    def test_verify_fails_while_a_rule_is_red(self):
        self.seal()
        code, out = run("verify", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("fail: AC-001", out)

    def test_verify_fails_on_a_hand_made_seal_declaring_a_passing_test_as_rule(self):
        files = [*RULE_FILES, *KEEP_FILES]
        message = (
            "test: plan.md の受け入れテスト\n\n"
            "Define-Done-Seal: AC-001, AC-002\nDefine-Done-Rule: AC-001, AC-002\n"
            f"Define-Done-Rule-Files: test/a.rule.test.js, test/a.keep.test.js\nDefine-Done-Files: {', '.join(files)}\n"
            f"Define-Done-Test-Command: {REPORT_COMMAND}\n"
        )
        self.repo.commit(message, *files)
        self.implement()
        code, out = run("verify", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("vacuous: AC-002", out)

    def test_plan_with_only_non_impact_criteria_completes_without_red(self):
        self.repo.write("test/a.keep.test.js", KEEP_TEST)
        code, out = run("seal", str(self.root), stdin=seal_spec(REPORT_COMMAND.replace("test/a.rule.test.js ", ""), (), KEEP_FILES))
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

    def test_unpushed_seal_on_main_is_in_progress(self):
        self.add_remote_and_push()
        self.seal()
        self.repo.write("test/a.keep.test.js", KEEP_TEST.replace("keeps", "still keeps"))
        self.repo.commit("edit non-impact test")
        code, out = run("check", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("tamper:", out)

    def start_next_plan(self):
        self.repo.write("test/c.rule.test.js", RULE_TEST.replace("AC-001", "AC-101").replace("assert.equal(f(), 1)", "assert.equal(f(), 2)"))
        command = "node --test --test-reporter=junit --test-reporter-destination={report} test/c.rule.test.js"
        return run("seal", str(self.root), stdin=seal_spec(command, ["test/c.rule.test.js"]))

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
        rewrite = "node --test --test-reporter=junit --test-reporter-destination={report} test/a.rule.test.js"
        self.repo.write("src/a.js", "export const f = () => 0;\n")
        code, out = run("seal", str(self.root), stdin=seal_spec(rewrite, ["test/a.rule.test.js"]))
        self.assertEqual(code, 1)
        self.assertIn("supersedes:", out)
        code, out = run("seal", str(self.root), stdin=seal_spec(rewrite, ["test/a.rule.test.js"], supersedes="AC-001 (R-1)"))
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
RSPEC_RULE = "require 'rspec'\nrequire_relative 'harness/app'\nRSpec.describe 'f' do\n  it 'AC-001 returns 1' do\n    expect(F.call).to eq(1)\n  end\nend\n"
RSPEC_KEEP = "require 'rspec'\nrequire_relative 'harness/app'\nRSpec.describe 'g' do\n  it 'AC-002 keeps its text' do\n    expect(G.call).to eq('kept')\n  end\nend\n"


class RubyTest(unittest.TestCase):
    def test_require_of_rails_helper_and_the_harness_is_allowed(self):
        text = "require 'rails_helper'\nrequire_relative 'harness/sign_in'\nrequire_relative './harness'\n"
        self.assertEqual(check_seal.import_findings("spec/acceptance/a_spec.rb", text), [])

    def test_require_of_product_code_is_a_boundary_finding(self):
        text = "require 'rails_helper'\nrequire_relative '../../app/models/user'\nrequire 'net/http'\n"
        self.assertEqual(check_seal.import_findings("spec/acceptance/a_spec.rb", text), ["../../app/models/user", "net/http"])

    def test_rspec_json_report_maps_examples_to_criteria(self):
        report = '{"examples": [{"full_description": "f AC-001 returns 1", "status": "failed"}, {"full_description": "g AC-002 keeps", "status": "passed"}, {"full_description": "h AC-003 later", "status": "pending"}]}'
        self.assertEqual(check_seal.parse_report(report), {"AC-001": ["fail"], "AC-002": ["pass"], "AC-003": ["skipped"]})

    def test_rspec_junit_formatter_report_maps_testcases_to_criteria(self):
        report = '<?xml version="1.0"?><testsuite><testcase classname="spec.a_spec" name="f AC-001 returns 1"><failure message="x"/></testcase><testcase classname="spec.a_spec" name="g AC-002 keeps"/></testsuite>'
        self.assertEqual(check_seal.parse_report(report), {"AC-001": ["fail"], "AC-002": ["pass"]})

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
            command = "rspec spec/acceptance/a_rule_spec.rb spec/acceptance/a_keep_spec.rb --format json --out {report}"
            code, out = run("seal", str(root), stdin=seal_spec(command, ["spec/acceptance/a_rule_spec.rb"], ["spec/acceptance/a_keep_spec.rb", "spec/acceptance/harness/app.rb"]))
            self.assertEqual(code, 0, out)
            repo.write("lib/a.rb", "F = -> { 1 }\nG = -> { 'kept' }\n")
            repo.commit("impl")
            code, out = run("verify", str(root))
            self.assertEqual(code, 0, out)
            self.assertIn("AC-001: rule sealed=fail current=pass", out)


if __name__ == "__main__":
    unittest.main()
