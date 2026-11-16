import argparse
import json
import posixpath
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
from pathlib import Path

SEAL_TRAILER = "Define-Done-Seal"
RULE_TRAILER = "Define-Done-Rule"
RULE_FILES_TRAILER = "Define-Done-Rule-Files"
FILES_TRAILER = "Define-Done-Files"
COMMAND_TRAILER = "Define-Done-Test-Command"
SUPERSEDES_TRAILER = "Define-Done-Supersedes"
REPORT_PLACEHOLDER = "{report}"
COMPLETION_REFS = ("refs/remotes/origin/HEAD", "refs/remotes/origin/main", "refs/remotes/origin/master")
AC_ID = re.compile(r"AC-\d{3}")
CODE_SUFFIXES = (".js", ".mjs", ".cjs", ".jsx", ".ts", ".mts", ".cts", ".tsx", ".py", ".rb")
HARNESS_DIR = "harness"
RUNNER_MODULES = {
    "bun:test",
    "vitest",
    "@playwright/test",
    "@jest/globals",
    "node:test",
    "node:assert",
    "node:assert/strict",
    "pytest",
    "unittest",
    "rspec",
    "spec_helper",
    "rails_helper",
}
JS_IMPORT = re.compile(
    r"""(?:^|[\n;])\s*(?:import|export)\s+(?:[^'";]*?\sfrom\s+)?['"]([^'"]+)['"]|\bimport\(\s*['"]([^'"]+)['"]\s*\)|\brequire\(\s*['"]([^'"]+)['"]\s*\)"""
)
PY_IMPORT = re.compile(r"^\s*(?:from\s+(\.*[\w.]*)\s+import|import\s+([\w.]+))", re.M)
RB_REQUIRE = re.compile(r"""^\s*(require|require_relative)\s*\(?\s*['"]([^'"]+)['"]""", re.M)
LEGACY_TEST_OR_PLAN = re.compile(r"\.md$|(^|/)(tests?|__tests__|specs?|e2e)/|(^|/)test_[^/]*$|[._-](test|spec)\.[^/]+$")


def git(repo, *args):
    completed = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout


def git_stdin(repo, text, *args):
    completed = subprocess.run(["git", "-C", str(repo), *args], input=text, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip())
    return completed.stdout


def trailers(repo, sha):
    parsed = git_stdin(repo, git(repo, "show", "-s", "--format=%B", sha), "interpret-trailers", "--parse")
    values = {}
    for line in parsed.splitlines():
        key, _, value = line.partition(":")
        values[key.strip()] = value.strip()
    return values


def listed(value):
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def files_in(repo, sha):
    return [path for path in git(repo, "show", "--name-only", "--format=", sha).splitlines() if path]


def completion_ref(repo):
    for ref in COMPLETION_REFS:
        if subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", ref], capture_output=True).returncode == 0:
            return ref
    return None


def is_completed(repo, ref, sha):
    return ref is not None and subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", sha, ref]).returncode == 0


def seals(repo):
    out = git(repo, "log", "-E", f"--grep=^({SEAL_TRAILER}|{SUPERSEDES_TRAILER}): ", "--format=%H", "HEAD")
    ref = completion_ref(repo)
    found = []
    for sha in out.split():
        values = trailers(repo, sha)
        if not {SEAL_TRAILER, SUPERSEDES_TRAILER} & set(values):
            continue
        files = files_in(repo, sha)
        recorded = FILES_TRAILER in values
        if recorded and set(listed(values[FILES_TRAILER])) != set(files):
            continue
        if not recorded and not all(LEGACY_TEST_OR_PLAN.search(path) for path in files):
            continue
        found.append({
            "sha": sha,
            "values": values,
            "files": files,
            "behavior": SEAL_TRAILER in values and (recorded or SUPERSEDES_TRAILER not in values),
            "recorded": recorded,
            "rule_files": set(listed(values.get(RULE_FILES_TRAILER))),
            "completed": is_completed(repo, ref, sha),
        })
    return found


def protected_paths(found):
    protected = {}
    for path in sorted({path for seal in found for path in seal["files"]}):
        reference = next(seal for seal in found if path in seal["files"])
        classifier = next((seal for seal in found if seal["behavior"] and path in seal["files"]), None)
        permanent = classifier is not None and classifier["completed"] and path in classifier["rule_files"]
        in_progress = not reference["completed"] or (classifier is not None and not classifier["completed"])
        if permanent or in_progress:
            protected[path] = {"reference": reference["sha"], "permanent": permanent}
    return protected


def is_test_file(path, text):
    return path.endswith(CODE_SUFFIXES) and HARNESS_DIR not in path.split("/")[:-1] and AC_ID.search(text) is not None


def import_findings(path, text):
    harness = posixpath.join(posixpath.dirname(path), HARNESS_DIR)
    findings = []
    if path.endswith(".rb"):
        for method, specifier in RB_REQUIRE.findall(text):
            if method == "require" and specifier in RUNNER_MODULES:
                continue
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(path), specifier))
            if method == "require_relative" and (resolved == harness or resolved.startswith(harness + "/")):
                continue
            findings.append(specifier)
        return findings
    if path.endswith(".py"):
        specifiers = [a or b for a, b in PY_IMPORT.findall(text)]
        for specifier in specifiers:
            head = specifier.lstrip(".").split(".")[0]
            if head not in RUNNER_MODULES and head != HARNESS_DIR:
                findings.append(specifier)
        return findings
    for groups in JS_IMPORT.findall(text):
        specifier = next(group for group in groups if group)
        if specifier in RUNNER_MODULES:
            continue
        if specifier.startswith("."):
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(path), specifier))
            if resolved == harness or resolved.startswith(harness + "/"):
                continue
        findings.append(specifier)
    return findings


def read_at(repo, sha, path):
    try:
        return git(repo, "show", f"{sha}:{path}")
    except RuntimeError:
        return ""


def inspect(repo):
    found = seals(repo)
    behavior = [seal for seal in found if seal["behavior"] and not seal["completed"]]
    if not behavior:
        return None, ["seal: 進行中の `Define-Done-Seal:` の封が HEAD から辿れない"]
    latest = behavior[0]
    values = latest["values"]
    findings = []
    command = values.get(COMMAND_TRAILER, "")
    if not command:
        findings.append(f"seal: {latest['sha'][:12]} に `{COMMAND_TRAILER}:` の trailer が無い")
    elif latest["recorded"] and REPORT_PLACEHOLDER not in command:
        findings.append(f"seal: {latest['sha'][:12]} の `{COMMAND_TRAILER}:` に {REPORT_PLACEHOLDER} が無い")
    protected = protected_paths(found)
    seal_set = {seal["sha"] for seal in found}
    touched_after_seal = {}
    for path, entry in protected.items():
        for sha in git(repo, "log", "--format=%H", f"{entry['reference']}..HEAD", "--", path).split():
            if sha not in seal_set:
                touched_after_seal.setdefault(sha, []).append(path)
    for sha, paths in touched_after_seal.items():
        findings.append(f"tamper: {sha[:12]} が封の後に {', '.join(paths)} を変えた")
    if protected:
        dirty = git(repo, "status", "--porcelain", "--", *protected).splitlines()
        if dirty:
            findings.append(f"tamper: 封をしたファイルに未 commit の変更がある ({'; '.join(line.strip() for line in dirty)})")
    for seal in behavior:
        if not seal["recorded"]:
            continue
        for path in seal["files"]:
            text = read_at(repo, seal["sha"], path)
            if is_test_file(path, text):
                for specifier in import_findings(path, text):
                    findings.append(f"boundary: {path} が土台とテストランナーの外の {specifier} を import している")
    info = {
        "seal": latest["sha"],
        "acs": values.get(SEAL_TRAILER, ""),
        "rule": values.get(RULE_TRAILER, ""),
        "test-command": command,
        "protected": ", ".join(protected),
        "permanent": ", ".join(path for path, entry in protected.items() if entry["permanent"]),
        "seals": ", ".join(seal["sha"][:12] for seal in found),
    }
    return {**info, "recorded": latest["recorded"]}, findings


def run_tests(cwd, command):
    with tempfile.TemporaryDirectory() as scratch:
        report = Path(scratch) / "report"
        completed = subprocess.run(command.replace(REPORT_PLACEHOLDER, str(report)), shell=True, cwd=cwd, capture_output=True, text=True, timeout=1200)
        results = parse_report(report.read_text(encoding="utf-8")) if report.exists() else {}
    return completed.returncode, completed.stdout + completed.stderr, results


def parse_report(text):
    return parse_rspec_json(text) if text.lstrip().startswith("{") else parse_junit(text)


def parse_rspec_json(text):
    results = {}
    try:
        examples = json.loads(text).get("examples") or []
    except json.JSONDecodeError:
        return results
    states = {"passed": "pass", "failed": "fail"}
    for example in examples:
        match = AC_ID.search(example.get("full_description", "")) or AC_ID.search(example.get("description", ""))
        if match is not None:
            results.setdefault(match.group(0), []).append(states.get(example.get("status"), "skipped"))
    return results


def parse_junit(text):
    results = {}
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError:
        return results
    for case in root.iter("testcase"):
        match = AC_ID.search(case.get("name", "")) or AC_ID.search(case.get("classname", ""))
        if match is None:
            continue
        if case.find("skipped") is not None:
            state = "skipped"
        elif case.find("failure") is not None or case.find("error") is not None or case.get("failure"):
            state = "fail"
        else:
            state = "pass"
        results.setdefault(match.group(0), []).append(state)
    return results


def outcome(states):
    if not states or "skipped" in states:
        return "missing"
    if all(state == "fail" for state in states):
        return "fail"
    if all(state == "pass" for state in states):
        return "pass"
    return "mixed"


def run_at_seal(repo, sha, command):
    with tempfile.TemporaryDirectory() as work:
        archive = subprocess.run(["git", "-C", str(repo), "archive", sha], capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", work], input=archive.stdout, check=True)
        modules = Path(repo) / "node_modules"
        if modules.is_dir():
            (Path(work) / "node_modules").symlink_to(modules.resolve())
        return run_tests(work, command)


def verify(repo, info):
    command = info["test-command"]
    sealed_code, _, sealed = run_at_seal(repo, info["seal"], command)
    current_code, output, current = run_tests(repo, command)
    print(f"sealed-exit: {sealed_code}")
    print(f"current-exit: {current_code}")
    print(output[-4000:])
    if not info["recorded"]:
        findings = []
        if sealed_code == 0:
            findings.append("vacuous: 受け入れテストが封の時点で既に通っていた。振る舞いを観測していない")
        if current_code != 0:
            findings.append("fail: 受け入れテストが今の tree で落ちる")
        return findings
    rule = set(listed(info["rule"]))
    findings = []
    for ac in listed(info["acs"]):
        kind = "rule" if ac in rule else "non-impact"
        at_seal, now = outcome(sealed.get(ac)), outcome(current.get(ac))
        print(f"{ac}: {kind} sealed={at_seal} current={now}")
        if at_seal == "missing" or now == "missing":
            findings.append(f"missing: {ac} のテストが{'封の時点' if at_seal == 'missing' else '今の tree'}で実行されなかった")
            continue
        if kind == "rule" and at_seal != "fail":
            findings.append(f"vacuous: {ac} は規則の基準だが、封の時点で落ちなかった")
        if kind == "non-impact" and at_seal != "pass":
            findings.append(f"kind: {ac} は非影響の基準だが、封の時点で通らなかった")
        if now != "pass":
            findings.append(f"fail: {ac} が今の tree で通らない")
    return findings


def seal(repo, spec_text):
    try:
        spec = json.loads(spec_text)
    except json.JSONDecodeError as exc:
        return [f"spec: 標準入力の JSON を読めない ({exc})"]
    test_command, supersedes = str(spec.get("test_command") or ""), str(spec.get("supersedes") or "")
    subject = str(spec.get("subject") or "test: 受け入れテスト")
    rule_files = list(dict.fromkeys(spec.get("rule") or []))
    non_impact_files = list(dict.fromkeys(spec.get("non_impact") or []))
    files = rule_files + non_impact_files
    errors = []
    if set(rule_files) & set(non_impact_files):
        errors.append(f"files: {', '.join(sorted(set(rule_files) & set(non_impact_files)))} が両方の種類に挙がっている")
    if REPORT_PLACEHOLDER not in test_command:
        errors.append(f"command: test_command に結果の出力先 {REPORT_PLACEHOLDER} が無い")
    missing = [path for path in files if not (Path(repo) / path).is_file()]
    if missing:
        errors.append(f"files: {', '.join(missing)} が無い")
    if errors:
        return errors
    kinds = {}
    for kind, paths in (("rule", rule_files), ("non-impact", non_impact_files)):
        for path in paths:
            text = (Path(repo) / path).read_text(encoding="utf-8")
            if not is_test_file(path, text):
                continue
            for specifier in import_findings(path, text):
                errors.append(f"boundary: {path} が土台とテストランナーの外の {specifier} を import している")
            for ac in sorted(set(AC_ID.findall(text))):
                if kinds.setdefault(ac, kind) != kind:
                    errors.append(f"kind: {ac} が規則と非影響の両方のファイルにある")
    if not kinds:
        errors.append("files: AC-ID で始まる名前のテストを持つファイルが無い")
    found = seals(repo)
    permanent = {path for path, entry in protected_paths(found).items() if entry["permanent"]}
    rewritten = sorted(permanent & set(files))
    if rewritten and not supersedes:
        errors.append(f"supersedes: 恒久に守っている規則の基準 {', '.join(rewritten)} を書き直すには supersedes に置き換える AC-ID と根拠の要求が要る")
    if errors:
        return errors
    code, output, results = run_tests(repo, test_command)
    for ac, kind in sorted(kinds.items()):
        state = outcome(results.get(ac))
        expected = "fail" if kind == "rule" else "pass"
        print(f"{ac}: {kind} now={state}")
        if state == "missing":
            errors.append(f"missing: {ac} のテストが実行されなかった (import やセットアップの失敗を直す)")
        elif state != expected:
            errors.append(f"kind: {ac} は{'規則' if kind == 'rule' else '非影響'}の基準だが、今の tree で {state} だった")
    if errors:
        print(output[-4000:])
        return errors
    rule_acs = sorted(ac for ac, kind in kinds.items() if kind == "rule")
    lines = [
        f"{SEAL_TRAILER}: {', '.join(sorted(kinds))}",
        *([f"{RULE_TRAILER}: {', '.join(rule_acs)}"] if rule_acs else []),
        *([f"{RULE_FILES_TRAILER}: {', '.join(rule_files)}"] if rule_files else []),
        f"{FILES_TRAILER}: {', '.join(files)}",
        f"{COMMAND_TRAILER}: {test_command}",
        *([f"{SUPERSEDES_TRAILER}: {supersedes}"] if supersedes else []),
    ]
    message = f"{subject}\n\n" + "\n".join(lines) + "\n"
    git(repo, "add", "--", *files)
    git_stdin(repo, message, "commit", "-q", "-F", "-", "--", *files)
    print(f"seal: {git(repo, 'rev-parse', 'HEAD').strip()}")
    return []


def main(argv=None, stdin=None):
    parser = argparse.ArgumentParser(prog="check_seal.py")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check").add_argument("repo", type=Path)
    sub.add_parser("verify").add_argument("repo", type=Path)
    sub.add_parser("seal").add_argument("repo", type=Path)
    args = parser.parse_args(argv)
    code = run_command(args, stdin)
    print(f"exit: {code}")
    return code


def run_command(args, stdin):
    try:
        if args.command == "seal":
            errors = seal(args.repo, sys.stdin.read() if stdin is None else stdin)
            for error in errors:
                print(error)
            return 1 if errors else 0
        info, findings = inspect(args.repo)
    except RuntimeError as exc:
        print(f"git: {exc}")
        return 1
    if info:
        for key, value in info.items():
            if key != "recorded":
                print(f"{key}: {value}")
    for finding in findings:
        print(finding)
    if findings:
        return 1
    if args.command == "verify":
        failures = verify(args.repo, info)
        for failure in failures:
            print(failure)
        return 1 if failures else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
