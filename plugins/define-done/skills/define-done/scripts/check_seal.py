import argparse
import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
from pathlib import Path

SEAL_TRAILER = "Define-Done-Seal"
RULE_TRAILER = "Define-Done-Rule"
RULE_FILES_TRAILER = "Define-Done-Rule-Files"
FILES_TRAILER = "Define-Done-Files"
TEST_TRAILER = "Define-Done-Test"
COMMAND_TRAILER = "Define-Done-Test-Command"
SUPERSEDES_TRAILER = "Define-Done-Supersedes"
PLAN_TRAILER = "Define-Done-Plan"
CRITERIA_TRAILER = "Define-Done-Criteria"
REQUIREMENTS_TRAILER = "Define-Done-Requirements"
REWORDED_TRAILER = "Define-Done-Reworded"
DIGEST_ENTRY = re.compile(r"(AC-\d{3}|R-\d+)=([0-9a-f]{10})")
TEST_SEPARATOR = " › "
REPORT_PLACEHOLDER = "{report}"
COMPLETION_REFS = ("refs/remotes/origin/HEAD", "refs/remotes/origin/main", "refs/remotes/origin/master")
AC_ID = re.compile(r"AC-\d{3}")
TEST_ENTRY = re.compile(r"^(AC-\d{3}) = (.+?)" + TEST_SEPARATOR + r"(.+)$")
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
PLAN_SECTIONS = ("Requirements", "Ground Review", "Acceptance Criteria", "MECE Review")
PLAN_HEADING = re.compile(r"^## Acceptance Criteria[ \t]*$", re.M)
REQUIREMENT_LINE = re.compile(r"^- (R-\d+):", re.M)
REQUIREMENT_ID = re.compile(r"R-\d+")
CRITERION_LINE = re.compile(r"^- (?:\[[ xX]\] )?(AC-\d{3}):[ \t]*(?:\[(規則|非影響)\])?(.*)$", re.M)
ROW_WITHOUT_CRITERION = re.compile(r"\s*(?:未検証|範囲外|不足情報)")
REQUIREMENT_ROW = re.compile(r"^\|[ \t]*(R-\d+)[ \t]*\|(.*)\|[ \t]*$", re.M)
GATE_LINE = re.compile(r"^- Gate:[ \t]*(.*)$", re.M)
GATE_READY = re.compile(r"ready(?:\s*[(（].*)?")
AC_IDS_LINE = re.compile(r"^- AC IDs:[ \t]*(.*)$", re.M)
SOURCE_NOTE = "(出典:"
KIND_LABELS = {"rule": "規則", "non-impact": "非影響"}
DEPENDENCY_DIRS = ("node_modules", ".venv", "vendor/bundle")
SPIKE_RECORD = "define-done-spike-paths"
PLAN_BASELINE = "Define-Done-Plan-Outside"
PLAN_BASELINE_LINE = re.compile(rf"^{PLAN_BASELINE}: ([0-9a-f]{{64}})$", re.M)
REJECTED_DECISIONS = "検査が拒んだ決定"
SPIKE_PATCHES = "define-done-spike-patches"
PLAN_PATHS = "define-done-plans"
CHECK_COMMAND_REQUIREMENT = re.compile(r"`[^`]+`\s*(?:が|も)\s*(?:すべて|全部)?\s*(?:通る|成功する)[。.]?")
NON_GOAL_REQUIREMENT = re.compile(r"(?:まだ|今回は|(?:この|本) ?(?:issue|PR|計画) ?では)\s*(?:作ら|実装し|扱わ|含め|入れ)ない")
REQUIREMENT_TEXT = re.compile(r"^- (R-\d+):[ \t]*(.*)$", re.M)
QUOTE_OPENING = "(「"
REPORT_REMINDER = "report: 最後の報告の先頭に、`check_seal.py report` が出す最終回答 (引用付きの要求の一覧) を置く"
RESIDUAL_RISKS = "残ったリスク"
RISK_DESTINATIONS = ("`AC-NNN`", "`実装のテスト:`", "`既存のテスト:`", "`規約`", "`未検証:`")
RISK_DESTINATION = re.compile(r"AC-\d{3}|(?:実装のテスト|既存のテスト|未検証)[:：]|規約")
NOTHING_NOTED = re.compile(r"-?\s*(?:無い|無し|なし|ない|該当なし|該当無し)(?:[\s。.、(（].*)?")
TABLE_RULE = re.compile(r"^\|[\s:|-]+\|$")
PROTECTION_NOTES = {
    "permanent": "恒久に守る規則の基準 (書き直すには凍結に含めて supersedes を渡す)",
    "in-progress": "計画の完了まで守る (直したら reseal)",
    "released": "保護は解けている (凍結に含めずに変えてよい)",
    "unsealed": "凍結したファイルでない",
}
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
    values, tests = {}, []
    for line in parsed.splitlines():
        key, _, value = line.partition(":")
        if key.strip() == TEST_TRAILER:
            tests.append(value.strip())
        else:
            values[key.strip()] = value.strip()
    if tests:
        values[TEST_TRAILER] = tests
    return values


def listed(value):
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def test_mapping(entries):
    mapping = []
    for entry in entries:
        match = TEST_ENTRY.match(entry)
        if match:
            mapping.append({"ac": match.group(1), "file": match.group(2), "name": match.group(3)})
    return mapping


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
            "mapping": test_mapping(values.get(TEST_TRAILER, [])),
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


def is_code(path):
    return path.endswith(CODE_SUFFIXES) and HARNESS_DIR not in path.split("/")[:-1]


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
        for a, b in PY_IMPORT.findall(text):
            specifier = a or b
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


def sealed_test_files(repo, seal):
    if seal["mapping"]:
        return sorted({test["file"] for test in seal["mapping"]})
    return [path for path in seal["files"] if is_code(path) and AC_ID.search(read_at(repo, seal["sha"], path))]


def inspect(repo):
    found = seals(repo)
    behavior = [seal for seal in found if seal["behavior"] and not seal["completed"]]
    if not behavior:
        return None, ["seal: 進行中の `Define-Done-Seal:` の凍結の commit が HEAD から辿れない"]
    latest = behavior[0]
    values = latest["values"]
    findings = []
    command = values.get(COMMAND_TRAILER, "")
    if not command:
        findings.append(f"seal: {latest['sha'][:12]} に `{COMMAND_TRAILER}:` の trailer が無い")
    elif latest["recorded"] and REPORT_PLACEHOLDER not in command:
        findings.append(f"seal: {latest['sha'][:12]} の `{COMMAND_TRAILER}:` に {REPORT_PLACEHOLDER} が無い")
    protected = protected_paths(found)
    completed = sum(seal["completed"] for seal in found)
    seal_set = {seal["sha"] for seal in found}
    touched_after_seal = {}
    for path, entry in protected.items():
        for sha in git(repo, "log", "--format=%H", f"{entry['reference']}..HEAD", "--", path).split():
            if sha not in seal_set:
                touched_after_seal.setdefault(sha, []).append(path)
    for sha, paths in touched_after_seal.items():
        findings.append(f"tamper: {sha[:12]} が凍結の後に {', '.join(paths)} を変えた")
    if protected:
        dirty = git(repo, "status", "--porcelain", "--", *protected).splitlines()
        if dirty:
            findings.append(f"tamper: 凍結したファイルに未 commit の変更がある ({'; '.join(line.strip() for line in dirty)})")
    for seal in behavior:
        if not seal["recorded"]:
            continue
        for path in sealed_test_files(repo, seal):
            for specifier in import_findings(path, read_at(repo, seal["sha"], path)):
                findings.append(f"boundary: {path} が土台とテストランナーの外の {specifier} を import している")
    info = {
        "seal": latest["sha"],
        "acs": values.get(SEAL_TRAILER, ""),
        "rule": values.get(RULE_TRAILER, ""),
        "test-command": command,
        "protected": ", ".join(protected),
        "permanent": ", ".join(path for path, entry in protected.items() if entry["permanent"]),
        "seals": ", ".join(seal["sha"][:12] for seal in found if not seal["completed"]) + (f" (ほか完了済み {completed} 件)" if completed else ""),
    }
    return {**info, "recorded": latest["recorded"], "mapping": latest["mapping"]}, findings


def run_tests(cwd, command):
    report = Path(cwd) / f".define-done-report-{os.getpid()}"
    try:
        completed = subprocess.run(command.replace(REPORT_PLACEHOLDER, report.name), shell=True, cwd=cwd, capture_output=True, text=True, timeout=1800)
        entries = parse_report(report.read_text(encoding="utf-8")) if report.exists() else []
    finally:
        report.unlink(missing_ok=True)
    return completed.returncode, completed.stdout + completed.stderr, entries


def parse_report(text):
    return parse_rspec_json(text) if text.lstrip().startswith("{") else parse_junit(text)


def parse_rspec_json(text):
    try:
        examples = json.loads(text).get("examples") or []
    except json.JSONDecodeError:
        return []
    states = {"passed": "pass", "failed": "fail"}
    return [
        {"files": [example.get("file_path", "")], "names": [example.get("full_description", ""), example.get("description", "")], "state": states.get(example.get("status"), "skipped")}
        for example in examples
    ]


def parse_junit(text):
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError:
        return []
    entries = []
    for case in root.iter("testcase"):
        if case.find("skipped") is not None:
            state = "skipped"
        elif case.find("failure") is not None or case.find("error") is not None or case.get("failure"):
            state = "fail"
        else:
            state = "pass"
        classname = case.get("classname", "")
        entries.append({
            "files": [case.get("file", ""), classname, classname.replace(".", "/")],
            "names": [case.get("name", ""), f"{classname} {case.get('name', '')}"],
            "state": state,
        })
    return entries


def same_file(candidate, path):
    candidate = candidate.replace("\\", "/").removeprefix("./")
    if not candidate:
        return False
    stem = posixpath.splitext(path)[0]
    return any(candidate == target or candidate.endswith("/" + target) or target.endswith("/" + candidate) for target in (path, stem))


def in_files(entry, paths):
    return any(same_file(candidate, path) for candidate in entry["files"] for path in paths)


def matches(entry, test):
    return in_files(entry, [test["file"]]) and any(name == test["name"] or name.endswith(test["name"]) for name in entry["names"] if name)


def states_by_ac(entries, mapping):
    states = {}
    for test in mapping:
        found = [entry["state"] for entry in entries if matches(entry, test)]
        states.setdefault(test["ac"], []).extend(found or ["missing"])
    return states


def legacy_states_by_ac(entries):
    states = {}
    for entry in entries:
        match = next((AC_ID.search(name) for name in entry["names"] if AC_ID.search(name)), None)
        if match:
            states.setdefault(match.group(0), []).append(entry["state"])
    return states


def outcome(states):
    if not states or "missing" in states or "skipped" in states:
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
    if not info["recorded"]:
        sealed_code, _, _ = run_at_seal(repo, info["seal"], command)
        current_code, output, _ = run_tests(repo, command)
        print(f"sealed-exit: {sealed_code}")
        print(f"current-exit: {current_code}")
        print(output[-4000:])
        findings = []
        if sealed_code == 0:
            findings.append("vacuous: 受け入れテストが凍結の時点で既に通っていた。振る舞いを観測していない")
        if current_code != 0:
            findings.append("fail: 受け入れテストが今の tree で落ちる")
        return findings
    current_code, output, entries = run_tests(repo, command)
    print(f"current-exit: {current_code}")
    print(output[-4000:])
    states = states_by_ac(entries, info["mapping"]) if info["mapping"] else legacy_states_by_ac(entries)
    rule = set(listed(info["rule"]))
    findings = []
    for ac in listed(info["acs"]):
        now = outcome(states.get(ac))
        print(f"{ac}: {'rule' if ac in rule else 'non-impact'} current={now}")
        if now == "missing":
            findings.append(f"missing: {ac} のテストが今の tree で実行されなかった")
        elif now != "pass":
            findings.append(f"fail: {ac} が今の tree で通らない")
    return findings


def changed_files(repo, files):
    entries = git(repo, "status", "--porcelain", "-z", "--untracked-files=all", "--", *files).split("\0")
    dirty = {entry[3:] for entry in entries if len(entry) > 3}
    return [path for path in files if path in dirty]


SET_ASIDE_MESSAGE = "define-done seal: 凍結の外の変更"


def outside_paths(repo, files):
    tracked = git(repo, "diff", "--name-only", "--no-renames", "-z", "HEAD").split("\0")
    untracked = git(repo, "ls-files", "--others", "--exclude-standard", "-z").split("\0")
    sealed = set(files)
    return sorted({path for path in tracked + untracked if path and path not in sealed})


def snapshot(repo, paths):
    state = {}
    for path in paths:
        full = Path(repo) / path
        state[path] = git(repo, "hash-object", "--", path).strip() if full.is_file() else None
    return state


def stash_shas(repo):
    return git(repo, "stash", "list", "--format=%H").split()


class SetAside:
    def __init__(self, repo, paths):
        self.repo, self.paths = repo, paths
        self.before = snapshot(repo, paths)
        self.sha = None
        self.applied = True
        self.staged_deletions = []

    def stash(self):
        if not self.paths:
            return
        existing = stash_shas(self.repo)
        deleted = set(git(self.repo, "diff", "--cached", "--name-only", "--no-renames", "--diff-filter=D", "-z", "HEAD").split("\0"))
        self.staged_deletions = [path for path in self.paths if path in deleted]
        if self.staged_deletions:
            git(self.repo, "reset", "-q", "--", *self.staged_deletions)
        pending = self.status()
        if not pending.strip():
            return
        try:
            git(self.repo, "stash", "push", "-q", "--include-untracked", "-m", SET_ASIDE_MESSAGE, "--", *self.paths)
        finally:
            shas = stash_shas(self.repo)
            if shas and shas[0] not in existing:
                self.sha, self.applied = shas[0], self.status() == pending
        if self.sha is None:
            raise RuntimeError("凍結の外の変更を退避できなかった")

    def status(self):
        return git(self.repo, "status", "--porcelain", "--untracked-files=all", "--", *self.paths)

    def apply(self):
        if self.sha and not self.applied:
            git(self.repo, "stash", "apply", "-q", "--index", self.sha)
            self.applied = True

    def restore(self):
        try:
            if self.sha:
                self.apply()
                if snapshot(self.repo, self.paths) != self.before:
                    raise RuntimeError("戻した変更が退避の前と一致しない")
                index = stash_shas(self.repo).index(self.sha)
                git(self.repo, "stash", "drop", "-q", f"stash@{{{index}}}")
            if self.staged_deletions:
                git(self.repo, "rm", "-q", "--cached", "--ignore-unmatch", "--", *self.staged_deletions)
                self.staged_deletions = []
        except (RuntimeError, ValueError) as exc:
            kept = f"退避は stash に残してある: `git stash apply {self.sha}` で戻す" if self.sha else "stage していた削除を `git rm --cached` で stage し直す"
            return [f"set-aside: 凍結の外の変更を戻せなかった ({exc})。{kept}"]
        return []


def run_check(repo, command):
    completed = subprocess.run(command, shell=True, cwd=repo, capture_output=True, text=True, timeout=1800)
    if completed.returncode == 0:
        print("check: pass")
        return []
    print((completed.stdout + completed.stderr)[-4000:])
    return [f"check: check_command が exit {completed.returncode} で落ちた (lint、型、dead code の違反を直す)"]


def spike_findings(repo, spike, files):
    patch = Path(spike)
    if not patch.is_file():
        return [f"spike: 試作の実装の patch {spike} が無い"]
    if Path(repo).resolve() in patch.resolve().parents:
        return [f"spike: 試作の実装の patch {spike} は repo の外に置く"]
    numstat = subprocess.run(["git", "-C", str(repo), "apply", "--numstat", str(patch.resolve())], capture_output=True, text=True)
    if numstat.returncode != 0:
        return [f"spike: 試作の実装の patch を読めない ({numstat.stderr.strip()})"]
    touched = {line.split("\t", 2)[2] for line in numstat.stdout.splitlines() if line.count("\t") >= 2}
    sealed = sorted(touched & set(files))
    if sealed:
        return [f"spike: 試作の実装の patch が凍結したファイル {', '.join(sealed)} を変えている"]
    if not touched:
        return ["spike: 試作の実装の patch が何も変えない"]
    return []


def plan_sections(text):
    found = {}
    for chunk in re.split(r"^(?=## )", text, flags=re.M):
        title, _, body = chunk.partition("\n")
        if title.startswith("## "):
            found.setdefault(title[3:].strip(), []).append(body)
    return found


def outside_digest(text):
    kept = [chunk.rstrip() for chunk in re.split(r"^(?=## )", text, flags=re.M) if chunk.partition("\n")[0][3:].strip() not in PLAN_SECTIONS or not chunk.startswith("## ")]
    return hashlib.sha256("\n".join(kept).encode("utf-8")).hexdigest()


def baseline_findings(plan, spike):
    preamble = Path(spike).read_text(encoding="utf-8", errors="replace").split("diff --git", 1)[0]
    recorded = PLAN_BASELINE_LINE.search(preamble)
    if recorded is None or recorded.group(1) == outside_digest(plan.read_text(encoding="utf-8")):
        return []
    return [f"plan: 計画の 4 節の外が `spike-open` の後に変わっている。計画の本文は元に戻し、検査が拒んだ決定は `## MECE Review` の `### {REJECTED_DECISIONS}` に書く (計画の本文を直すのは呼び出し側。直した後の計画で凍結するなら `spike-open` からやり直す)"]


def table_rows(text):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|") and not TABLE_RULE.match(line):
            rows.append((line, [cell.strip() for cell in line.strip("|").split("|")]))
    return rows


def subsections(body):
    return [(chunk.partition("\n")[0].strip(), chunk.partition("\n")[2]) for chunk in re.split(r"^### ", body, flags=re.M)[1:]]


def noted_lines(body, titled):
    return [line for title, text in subsections(body) if titled(title) for line in text.splitlines() if line.strip() and not NOTHING_NOTED.fullmatch(line.strip())]


def final_answer(plan, rule_count, non_impact_count, sha, files, patch):
    sections = plan_sections(plan.read_text(encoding="utf-8"))
    review = sections["MECE Review"][0]
    ground = sections.get("Ground Review", [""])[0]
    rows = table_rows(review)
    rejected = next((text for title, text in subsections(review) if title == REJECTED_DECISIONS), "")
    unverified = [
        *noted_lines(ground, lambda title: title.startswith("未検証")),
        *[line for line in review.splitlines() if line.startswith("- 未検証")],
        *[line for line in noted_lines(review, lambda title: "未検証" in title) if not line.startswith("|")],
        *[line for line, cells in rows if len(cells) > 1 and not REQUIREMENT_ID.fullmatch(cells[0]) and cells[1].startswith("未検証")],
    ]
    groups = [
        ("基準の無い要求", [line for line, cells in rows if len(cells) > 1 and REQUIREMENT_ID.fullmatch(cells[0]) and ROW_WITHOUT_CRITERION.match(cells[1])]),
        ("実装が足すテスト", [line for line, cells in rows if len(cells) > 1 and cells[1].startswith("実装のテスト")]),
        ("未決の判断", noted_lines(ground, lambda title: title.startswith("未決"))),
        ("未検証", list(dict.fromkeys(unverified))),
        (REJECTED_DECISIONS, [line for line, _ in table_rows(rejected)[1:]]),
    ]
    lines = [
        "要求:",
        *[line for line in sections["Requirements"][0].splitlines() if REQUIREMENT_LINE.match(line)],
        f"Gate: {GATE_LINE.findall(review)[0].strip()}",
        f"AC: 規則 {rule_count} 件、非影響 {non_impact_count} 件",
        f"凍結: {sha}",
        f"ファイル: {', '.join(files)}",
        *([f"試作の patch: {patch}"] if patch else []),
    ]
    for title, found in groups:
        if found:
            lines += [f"{title}:", *found]
    return lines


def locate_plan(repo, named, files):
    if named:
        path = Path(named).expanduser()
        return (path if path.is_absolute() else Path(repo) / path), []
    candidates = [path for path in files if path.endswith(".md") and PLAN_HEADING.search((Path(repo) / path).read_text(encoding="utf-8"))]
    if len(candidates) == 1:
        return Path(repo) / candidates[0], []
    if candidates:
        return None, [f"plan: 計画の候補が複数ある ({', '.join(candidates)})。`plan` に計画の path を渡す"]
    return None, ["plan: 計画が凍結するファイルに無い (repo の中の計画は non_impact に入れ、repo の外の計画は `plan` に path を渡す)"]


def plan_label(repo, plan):
    resolved, root = plan.resolve(), Path(repo).resolve()
    return resolved.relative_to(root).as_posix() if root in resolved.parents else "/".join(resolved.parts[-2:])


def plan_findings(plan, kinds):
    try:
        sections = plan_sections(plan.read_text(encoding="utf-8"))
    except OSError:
        return [f"plan: 計画 {plan} を読めない"]
    counts = {title: len(sections.get(title, [])) for title in PLAN_SECTIONS}
    if any(count != 1 for count in counts.values()):
        return [f"plan: 計画に `## {title}` の節が {count} 個ある (それぞれ 1 つにする)" for title, count in counts.items() if count != 1]
    requirements = sorted(set(REQUIREMENT_LINE.findall(sections["Requirements"][0])), key=lambda name: int(name[2:]))
    criteria = {}
    for ac, kind, rest in CRITERION_LINE.findall(sections["Acceptance Criteria"][0]):
        _, noted, sources = rest.rpartition(SOURCE_NOTE)
        criteria[ac] = {"kind": kind, "sources": set(REQUIREMENT_ID.findall(sources)) if noted else None}
    review = sections["MECE Review"][0]
    errors = []
    gates = GATE_LINE.findall(review)
    if len(gates) != 1:
        errors.append(f"plan: `## MECE Review` に `- Gate:` の行が {len(gates)} 個ある")
    elif not GATE_READY.fullmatch(gates[0].strip()):
        errors.append(f"plan: Gate が ready でない計画は凍結しない (`- Gate: {gates[0].strip()}`)")
    listed_ids = AC_IDS_LINE.findall(review)
    if len(listed_ids) != 1:
        errors.append(f"plan: `## MECE Review` に `- AC IDs:` の行が {len(listed_ids)} 個ある")
    elif set(AC_ID.findall(listed_ids[0])) != set(criteria):
        differing = sorted(set(AC_ID.findall(listed_ids[0])) ^ set(criteria))
        errors.append(f"plan: `- AC IDs:` の行と `## Acceptance Criteria` の基準が {', '.join(differing)} で食い違う (AC-ID を 1 つずつ並べる)")
    if not requirements:
        errors.append("plan: `## Requirements` に `- R-n:` の行が無い")
    for requirement, line in REQUIREMENT_TEXT.findall(sections["Requirements"][0]):
        stated = line.split(QUOTE_OPENING, 1)[0].strip()
        if CHECK_COMMAND_REQUIREMENT.fullmatch(stated):
            errors.append(f"plan: {requirement} は検査コマンドが通ることだけを述べている。要求にせず `check_command` に渡す (`## Requirements` と要求の表から行を外す)")
        elif NON_GOAL_REQUIREMENT.search(stated):
            errors.append(f"plan: {requirement} は今回は作らないものを述べている。要求にせず、計画の範囲外の宣言と突き合わせる (`## Requirements` と要求の表から行を外す)")
    for ac, kind in sorted(kinds.items()):
        entry = criteria.get(ac)
        if entry is None:
            errors.append(f"plan: テストを対応させた {ac} が計画の `## Acceptance Criteria` に無い")
            continue
        if entry["kind"] != KIND_LABELS[kind]:
            errors.append(f"plan: {ac} は計画で {'[' + entry['kind'] + ']' if entry['kind'] else '種類の印が無い'} だが、テストは{KIND_LABELS[kind]}のファイルにある")
        if entry["sources"] is None:
            errors.append(f"plan: {ac} の行に `(出典: ...)` が無い")
    for ac, entry in sorted(criteria.items()):
        unknown = sorted((entry["sources"] or set()) - set(requirements))
        if unknown:
            errors.append(f"plan: {ac} の出典 {', '.join(unknown)} が `## Requirements` に無い")
    rows = {}
    for requirement, cell in REQUIREMENT_ROW.findall(review):
        rows[requirement] = f"{rows.get(requirement, '')} {cell}"
    for requirement in requirements:
        cell = rows.get(requirement)
        if cell is None:
            errors.append(f"plan: {requirement} が `## MECE Review` の要求の表に無い")
            continue
        if ROW_WITHOUT_CRITERION.match(cell):
            continue
        named = AC_ID.findall(cell)
        if not named:
            errors.append(f"plan: 要求の表の {requirement} の行が、対応する AC でも `未検証:`、`範囲外:`、`不足情報:` でも始まらない")
        elif not any(requirement in (criteria.get(ac, {}).get("sources") or ()) for ac in named):
            errors.append(f"plan: 要求の表は {requirement} を {', '.join(named)} に対応させているが、そのどれも出典に {requirement} を挙げていない (出典に足すか、行を `未検証:`、`範囲外:`、`不足情報:` のどれかにする)")
    for title, text in subsections(review):
        if RESIDUAL_RISKS not in title:
            continue
        for _, cells in table_rows(text)[1:]:
            if len(cells) < 2:
                continue
            destination = cells[1].lstrip("`* ")
            unknown = sorted(set(AC_ID.findall(destination)) - set(criteria)) if AC_ID.match(destination) else []
            if not RISK_DESTINATION.match(destination):
                errors.append(f"plan: 残ったリスクの表の「{cells[0]}」の守る先が {'、'.join(RISK_DESTINATIONS)} のどれでも始まらない")
            elif unknown:
                errors.append(f"plan: 残ったリスクの表の「{cells[0]}」の守る先 {', '.join(unknown)} が `## Acceptance Criteria` に無い")
    return errors


def digest(text):
    return hashlib.sha256("".join(text.split()).encode("utf-8")).hexdigest()[:10]


def plan_digests(plan):
    sections = plan_sections(plan.read_text(encoding="utf-8"))
    criteria = {}
    for ac, _, rest in CRITERION_LINE.findall(sections["Acceptance Criteria"][0]):
        body, noted, _ = rest.rpartition(SOURCE_NOTE)
        criteria[ac] = digest(body if noted else rest)
    requirements = {name: digest(line.split(QUOTE_OPENING, 1)[0]) for name, line in REQUIREMENT_TEXT.findall(sections["Requirements"][0])}
    return criteria, requirements


def recorded_digests(value):
    return dict(DIGEST_ENTRY.findall(value or ""))


def moved_from(name, value, known, current):
    return sorted(old for old, recorded in known.items() if recorded == value and old != name and current.get(old) != value)


def identity_findings(earlier, criteria, requirements, reworded):
    known = recorded_digests(earlier["values"].get(CRITERIA_TRAILER))
    known_requirements = recorded_digests(earlier["values"].get(REQUIREMENTS_TRAILER))
    seal = earlier["sha"][:12]
    errors = []
    for ac, value in sorted(criteria.items()):
        moved = moved_from(ac, value, known, criteria)
        if ac in known and known[ac] != value and ac not in reworded:
            same = f" (今の本文は、前の凍結の {', '.join(moved)} と同じ)" if moved else ""
            errors.append(f"criteria: {ac} の本文が、前の凍結 {seal} から変わっている{same}。意味が変わったなら、旧い ID を使わず新しい ID の基準にする。言い回しだけを直したなら、標準入力の JSON の \"reworded\" に {ac} を挙げる")
        elif ac not in known and moved:
            errors.append(f"criteria: {ac} は、前の凍結 {seal} の {', '.join(moved)} と同じ本文である。意味の変わらない基準は ID を保つ ({', '.join(moved)} のまま書く)")
    for ac in reworded:
        if known.get(ac) == criteria.get(ac) or ac not in criteria:
            errors.append(f"reworded: {ac} は、前の凍結 {seal} から本文が変わっていない (\"reworded\" には、言い回しだけを直した基準を挙げる)")
    for name, value in sorted(requirements.items(), key=lambda item: int(item[0][2:])):
        moved = moved_from(name, value, known_requirements, requirements)
        if moved and known_requirements.get(name) != value:
            errors.append(f"requirements: {name} は、前の凍結 {seal} の {', '.join(moved)} と同じ文である。意味の変わらない要求は番号を保つ ({', '.join(moved)} のまま書く)")
    return errors


def carried(current, earlier, trailer):
    known = recorded_digests(earlier["values"].get(trailer)) if earlier else {}
    return {**{name: value for name, value in known.items() if name not in current}, **current}


def digest_line(entries):
    order = lambda name: (name[:2], int(name.split("-")[1]))
    return ", ".join(f"{name}={entries[name]}" for name in sorted(entries, key=order))


def spike_open(repo, files):
    missing = [path for path in files if not (Path(repo) / path).is_file()]
    if missing:
        return [f"spike: {', '.join(missing)} が無い"]
    texts = {path: (Path(repo) / path).read_text(encoding="utf-8") for path in files if path.endswith(".md")}
    plans = [path for path, text in texts.items() if PLAN_HEADING.search(text)]
    if len(plans) > 1:
        return [f"plan: 計画の候補が複数ある ({', '.join(plans)})。計画は 1 つだけ渡す"]
    baseline = outside_digest(texts[plans[0]]) if plans else ""
    files = [path for path in files if path not in plans]
    work = Path(tempfile.mkdtemp(prefix="define-done-spike-")) / "tree"
    git(repo, "worktree", "add", "-q", "--detach", str(work), "HEAD")
    ignored = git(repo, "ls-files", "--others", "--ignored", "--exclude-standard", "--directory", "-z").split("\0")
    linked = [path.rstrip("/") for path in ignored if path.endswith("/") and any(path.rstrip("/") == name or path.rstrip("/").endswith("/" + name) for name in DEPENDENCY_DIRS)]
    for path in linked:
        (work / path).parent.mkdir(parents=True, exist_ok=True)
        (work / path).symlink_to((Path(repo) / path).resolve())
    for path in files:
        (work / path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(repo) / path, work / path)
    record = Path(git(work, "rev-parse", "--absolute-git-dir").strip()) / SPIKE_RECORD
    record.write_text(json.dumps({"linked": linked, "copied": list(files), "plan": baseline}), encoding="utf-8")
    print(f"worktree: {work}")
    env_files = sorted(path for path in ignored if posixpath.basename(path).startswith(".env"))
    if env_files:
        print(f"env: {', '.join(env_files)} は複製に無い (git が無視する file)。複製の中でテストを流すときは、runner の flag で repo の file を指す")
    return []


def spike_close(repo, work):
    work = Path(work)
    try:
        record = json.loads((Path(git(work, "rev-parse", "--absolute-git-dir").strip()) / SPIKE_RECORD).read_text(encoding="utf-8"))
    except (RuntimeError, OSError, json.JSONDecodeError):
        return [f"spike: {work} は `spike-open` が作った複製でない"]
    stale = [path for path in record["copied"] if not ((work / path).is_file() and (Path(repo) / path).is_file() and (work / path).read_bytes() == (Path(repo) / path).read_bytes())]
    if stale:
        return [f"spike: 複製の {', '.join(stale)} が repo と食い違う (受け入れテストと土台は repo で直し、複製へ写し直す)"]
    scope = [".", *[f":(exclude){path}" for path in record["linked"] + record["copied"]]]
    git(work, "add", "-N", "--", *scope)
    diff = git(work, "diff", "--binary", "HEAD", "--", *scope)
    if not diff.strip():
        return ["spike: 複製に試作の実装の変更が無い"]
    patch = work.parent / "spike.patch"
    baseline = record.get("plan")
    patch.write_text((f"{PLAN_BASELINE}: {baseline}\n" if baseline else "") + diff, encoding="utf-8")
    git(repo, "worktree", "remove", "--force", str(work))
    print(f"spike: {patch}")
    return []


def remembered(repo, name):
    record = Path(repo) / git(repo, "rev-parse", "--git-common-dir").strip() / name
    try:
        return record, json.loads(record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return record, {}


def remember(repo, name, path):
    record, paths = remembered(repo, name)
    paths[git(repo, "rev-parse", "HEAD").strip()] = str(Path(path).expanduser().absolute())
    try:
        record.write_text(json.dumps(paths), encoding="utf-8")
    except OSError:
        pass


def remembered_file(repo, name, found):
    paths = remembered(repo, name)[1]
    return next((paths[seal["sha"]] for seal in found if Path(paths.get(seal["sha"]) or repo).is_file()), "")


def ran_names(entries, path):
    return [next((name for name in entry["names"] if name), "") for entry in entries if in_files(entry, [path])]


def seal(repo, spec_text):
    try:
        spec = json.loads(spec_text)
    except json.JSONDecodeError as exc:
        return [f"spec: 標準入力の JSON を読めない ({exc})"]
    test_command, supersedes = str(spec.get("test_command") or ""), str(spec.get("supersedes") or "")
    reworded = [str(ac) for ac in spec.get("reworded") or []]
    check_command, spike = str(spec.get("check_command") or ""), str(spec.get("spike") or "")
    rule_files = list(dict.fromkeys(spec.get("rule") or []))
    non_impact_files = list(dict.fromkeys(spec.get("non_impact") or []))
    mapping = [{"ac": str(test.get("ac", "")), "file": str(test.get("file", "")), "name": str(test.get("name", ""))} for test in spec.get("tests") or []]
    files = rule_files + non_impact_files
    errors = []
    if set(rule_files) & set(non_impact_files):
        errors.append(f"files: {', '.join(sorted(set(rule_files) & set(non_impact_files)))} が両方の種類に挙がっている")
    if REPORT_PLACEHOLDER not in test_command:
        errors.append(f"command: test_command に結果の出力先 {REPORT_PLACEHOLDER} が無い")
    missing = [path for path in files if not (Path(repo) / path).is_file()]
    if missing:
        errors.append(f"files: {', '.join(missing)} が無い")
    elif files and not changed_files(repo, files):
        errors.append("files: 渡したファイルがどれも HEAD から変わっていない (凍結し直すのは、受け入れテスト・土台・計画を直したときだけ)")
    if not mapping:
        errors.append("tests: AC とテストの対応が無い")
    kinds = {}
    for test in mapping:
        if not AC_ID.fullmatch(test["ac"]) or not test["name"] or "\n" in test["name"] or TEST_SEPARATOR in test["file"]:
            errors.append(f"tests: 対応 {test} の AC-ID かテスト名が読めない")
            continue
        if test["file"] not in files:
            errors.append(f"tests: {test['ac']} のテストのファイル {test['file']} が rule にも non_impact にも無い")
            continue
        kind = "rule" if test["file"] in rule_files else "non-impact"
        if kinds.setdefault(test["ac"], kind) != kind:
            errors.append(f"kind: {test['ac']} のテストが規則と非影響の両方のファイルにある")
    if errors:
        return errors
    plan, errors = locate_plan(repo, str(spec.get("plan") or ""), files)
    if errors:
        return errors
    errors = plan_findings(plan, kinds)
    found = seals(repo)
    label = plan_label(repo, plan)
    earlier = next((seal for seal in found if seal["behavior"] and not seal["completed"] and seal["values"].get(PLAN_TRAILER) == label and CRITERIA_TRAILER in seal["values"]), None)
    criteria, requirements = ({}, {}) if errors else plan_digests(plan)
    if earlier and not errors:
        errors = identity_findings(earlier, criteria, requirements, reworded)
    elif reworded and not errors:
        errors = ["reworded: 同じ計画の前の凍結が本文を記録していないので、\"reworded\" は要らない"]
    recorded = {
        PLAN_TRAILER: label,
        CRITERIA_TRAILER: digest_line(carried(criteria, earlier, CRITERIA_TRAILER)),
        REQUIREMENTS_TRAILER: digest_line(carried(requirements, earlier, REQUIREMENTS_TRAILER)),
        **({REWORDED_TRAILER: ", ".join(reworded)} if reworded else {}),
    }
    subject = str(spec.get("subject") or f"test: {plan_label(repo, plan)} の受け入れテスト{'を直す' if spec.get('resealed') else ''}")
    test_files = sorted({test["file"] for test in mapping})
    for path in files:
        if path.endswith(CODE_SUFFIXES) and AC_ID.search((Path(repo) / path).read_text(encoding="utf-8")):
            errors.append(f"tests: {path} に AC-ID を書かない (AC との対応は凍結の commit が記録する)")
    for path in test_files:
        for specifier in import_findings(path, (Path(repo) / path).read_text(encoding="utf-8")):
            errors.append(f"boundary: {path} が土台とテストランナーの外の {specifier} を import している")
    protected = protected_paths(found)
    frozen = sorted(set(protected) - set(files))
    dirty = git(repo, "status", "--porcelain", "--", *frozen).splitlines() if frozen else []
    if dirty:
        errors.append(f"tamper: 凍結したファイルに未 commit の変更がある ({'; '.join(line.strip() for line in dirty)})。戻してから凍結する")
    permanent = {path for path, entry in protected.items() if entry["permanent"]}
    rewritten = sorted(permanent & set(files))
    if rewritten and not supersedes:
        errors.append(f"supersedes: 恒久に守っている規則の基準 {', '.join(rewritten)} を書き直すには supersedes に置き換える AC-ID と根拠の要求が要る")
    if spike:
        errors.extend(spike_findings(repo, spike, files))
        if not errors and not spec.get("resealed"):
            errors.extend(baseline_findings(plan, spike))
    aside = SetAside(repo, outside_paths(repo, files))
    if errors:
        return errors
    changed = changed_files(repo, files)
    try:
        passing = passing_criteria(kind_states(repo, test_command, test_files, mapping, kinds)) if aside.paths and not spike else set()
        aside.stash()
        errors = seal_in_tree(repo, aside, test_command, test_files, mapping, kinds, spike, check_command, passing)
        if not errors:
            commit_seal(repo, subject, kinds, rule_files, changed, mapping, test_command, supersedes, recorded)
            if spike:
                remember(repo, SPIKE_PATCHES, spike)
            if spec.get("plan"):
                remember(repo, PLAN_PATHS, plan)
    except RuntimeError as exc:
        errors = [f"git: {exc}"]
    return errors + aside.restore()


def is_file_entry(entry, test_files):
    return any(same_file(name, path) for name in entry["names"] if name for path in test_files)


def kind_states(repo, test_command, test_files, mapping, kinds):
    code, output, entries = run_tests(repo, test_command)
    unmatched = []
    for entry in entries:
        if in_files(entry, test_files) and not is_file_entry(entry, test_files) and not any(matches(entry, test) for test in mapping):
            unmatched.append(f"tests: 対応する AC が無いテスト「{next(name for name in entry['names'] if name)}」がある")
    states = states_by_ac(entries, mapping)
    outcomes = {ac: outcome(states.get(ac)) for ac in kinds}
    missing = {}
    for ac, state in sorted(outcomes.items()):
        if state == "missing":
            files = sorted({test["file"] for test in mapping if test["ac"] == ac})
            ran = [name for path in files for name in ran_names(entries, path)]
            hint = f" このファイルで流れたテスト: {'; '.join(ran)}" if ran else ""
            missing[ac] = f"missing: {ac} のテストが実行されなかった (テスト名の対応か、import やセットアップの失敗を直す)。{hint}".rstrip("。 ")
    never_ran = {ac for ac in missing if "skipped" not in states.get(ac, [])}
    return {"outcomes": outcomes, "unmatched": unmatched, "missing": missing, "never_ran": never_ran, "output": output}


def passing_criteria(run):
    if run["unmatched"] or run["missing"]:
        return set()
    return {ac for ac, state in run["outcomes"].items() if state == "pass"}


UNLOADED_HINT = "変更前の tree に無い module を土台が静的に import していると、テストは落ちずに実行されない。試作の実装の patch を `spike` に渡すか、土台がその module を実行時に import する"


def seal_in_tree(repo, aside, test_command, test_files, mapping, kinds, spike, check_command, passing):
    if check_command and not spike:
        errors = run_check(repo, check_command)
        if errors:
            return errors
    run = kind_states(repo, test_command, test_files, mapping, kinds)
    now, output = run["outcomes"], run["output"]
    unloaded = {ac for ac in run["never_ran"] if kinds[ac] == "rule"}
    errors = run["unmatched"] + [message for ac, message in run["missing"].items() if ac not in unloaded]
    proved = {}
    if spike and not errors:
        patch = str(Path(spike).resolve())
        git(repo, "apply", patch)
        try:
            trial = kind_states(repo, test_command, test_files, mapping, kinds)
            proved, passing = trial["outcomes"], passing_criteria(trial)
            errors = trial["unmatched"] + list(trial["missing"].values())
            for ac, state in sorted(proved.items()):
                if state != "pass" and state != "missing":
                    errors.append(f"spike: {ac} が試作の実装で通らない (テスト、土台、要求のどれかを確かめる)")
            if errors:
                print(trial["output"][-4000:])
            elif check_command:
                errors = run_check(repo, check_command)
        finally:
            git(repo, "apply", "-R", patch)
        if errors:
            return errors
    for ac in sorted(unloaded - passing):
        errors.append(f"{run['missing'][ac]}。{UNLOADED_HINT}")
    if aside.sha and any(error.startswith("missing:") for error in errors):
        errors.append(f"missing: 凍結の外の変更 ({len(aside.paths)} 件) は退避して流している。凍結するファイルが、凍結に含めない変更に頼っていないかを確かめる")
    for ac in sorted(unloaded & passing):
        now[ac] = "fail"
        print(f"unloaded: {ac} のテストは変更前の tree で読み込めず実行されなかった。実装のある tree では通ったので、落ちたものと数える")
    for ac, kind in sorted(kinds.items()):
        state = now[ac]
        expected = "fail" if kind == "rule" else "pass"
        print(f"{ac}: {kind}{f' spike={proved[ac]}' if spike else ''} now={state}")
        if state != "missing" and state != expected:
            errors.append(f"kind: {ac} は{'規則' if kind == 'rule' else '非影響'}の基準だが、今の tree で {state} だった")
    if errors:
        print(output[-4000:])
    return errors


def commit_seal(repo, subject, kinds, rule_files, changed, mapping, test_command, supersedes, recorded):
    rule_acs = sorted(ac for ac, kind in kinds.items() if kind == "rule")
    lines = [
        f"{SEAL_TRAILER}: {', '.join(sorted(kinds))}",
        *([f"{RULE_TRAILER}: {', '.join(rule_acs)}"] if rule_acs else []),
        *([f"{RULE_FILES_TRAILER}: {', '.join(rule_files)}"] if rule_files else []),
        f"{FILES_TRAILER}: {', '.join(changed)}",
        *[f"{TEST_TRAILER}: {test['ac']} = {test['file']}{TEST_SEPARATOR}{test['name']}" for test in mapping],
        f"{COMMAND_TRAILER}: {test_command}",
        *([f"{SUPERSEDES_TRAILER}: {supersedes}"] if supersedes else []),
        *[f"{trailer}: {value}" for trailer, value in recorded.items() if value],
    ]
    message = f"{subject}\n\n" + "\n".join(lines) + "\n"
    git(repo, "add", "--", *changed)
    git_stdin(repo, message, "commit", "-q", "-F", "-", "--", *changed)
    print(f"seal: {git(repo, 'rev-parse', 'HEAD').strip()}")


def planned_criteria(repo, named, sealed):
    try:
        plan, errors = locate_plan(repo, named, [path for path in sealed if (Path(repo) / path).is_file()])
        if errors:
            return set()
        body = plan_sections(plan.read_text(encoding="utf-8")).get("Acceptance Criteria", [""])[0]
    except OSError:
        return set()
    return {ac for ac, _, _ in CRITERION_LINE.findall(body)}


def reseal_spec(repo, spec_text):
    try:
        overrides = json.loads(spec_text) if spec_text.strip() else {}
    except json.JSONDecodeError as exc:
        return None, [f"spec: 標準入力の JSON を読めない ({exc})"]
    found = [seal for seal in seals(repo) if seal["behavior"] and seal["recorded"] and not seal["completed"]]
    if not found:
        return None, ["reseal: 凍結し直す元の、進行中の凍結の commit が HEAD から辿れない"]
    latest = found[0]
    rule_files = sorted(latest["rule_files"])
    sealed = list(dict.fromkeys(path for seal in found for path in seal["files"]))
    given = list(overrides.get("tests") or [])
    replaced = {(str(test.get("ac", "")), str(test.get("file", ""))) for test in given}
    tests = [test for test in latest["mapping"] if (test["ac"], test["file"]) not in replaced] + given
    plan = remembered_file(repo, PLAN_PATHS, found[:1])
    kept = planned_criteria(repo, str(overrides.get("plan") or plan), sealed)
    if kept:
        for ac in sorted({test["ac"] for test in tests} - kept):
            print(f"dropped: {ac} は計画の `## Acceptance Criteria` に無いので、テストの対応を外した")
        tests = [test for test in tests if test["ac"] in kept]
    rule = list(dict.fromkeys(rule_files + list(overrides.get("rule") or [])))
    spec = {
        "test_command": overrides.get("test_command") or latest["values"].get(COMMAND_TRAILER, ""),
        "rule": rule,
        "non_impact": list(dict.fromkeys([path for path in sealed if path not in rule] + list(overrides.get("non_impact") or []))),
        "tests": tests,
        "resealed": True,
        **({"plan": plan} if plan else {}),
        **{key: overrides[key] for key in ("subject", "plan", "supersedes", "spike", "check_command", "reworded") if key in overrides},
    }
    return json.dumps(spec), []


def report(repo, named_plan):
    found = [seal for seal in seals(repo) if seal["behavior"] and seal["recorded"] and not seal["completed"]]
    if not found:
        return ["seal: 進行中の `Define-Done-Seal:` の凍結の commit が HEAD から辿れない"]
    latest = found[0]
    sealed = list(dict.fromkeys(path for seal in found for path in seal["files"] if (Path(repo) / path).is_file()))
    plan, errors = locate_plan(repo, named_plan or remembered_file(repo, PLAN_PATHS, found[:1]), sealed)
    if errors:
        return errors
    acs, rule = listed(latest["values"].get(SEAL_TRAILER)), listed(latest["values"].get(RULE_TRAILER))
    patch = remembered_file(repo, SPIKE_PATCHES, found)
    try:
        print("\n".join(final_answer(plan, len(rule), len(acs) - len(rule), latest["sha"], sealed, patch)))
    except (OSError, KeyError, IndexError):
        return [f"plan: 計画 {plan} から最終回答を組み立てられない (4 節と `- Gate:` の行を確かめる)"]
    return []


def protection(repo, paths):
    found = seals(repo)
    protected = protected_paths(found)
    sealed = {path for seal in found for path in seal["files"]}
    for path in paths:
        state = ("permanent" if protected[path]["permanent"] else "in-progress") if path in protected else "released" if path in sealed else "unsealed"
        print(f"protection: {path} = {state}: {PROTECTION_NOTES[state]}")


def main(argv=None, stdin=None):
    parser = argparse.ArgumentParser(prog="check_seal.py")
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser("check")
    check_parser.add_argument("repo", type=Path)
    check_parser.add_argument("paths", nargs="*")
    report_parser = sub.add_parser("report")
    report_parser.add_argument("repo", type=Path)
    report_parser.add_argument("plan", nargs="?", default="")
    sub.add_parser("verify").add_argument("repo", type=Path)
    sub.add_parser("seal").add_argument("repo", type=Path)
    sub.add_parser("reseal").add_argument("repo", type=Path)
    spike_open_parser = sub.add_parser("spike-open")
    spike_open_parser.add_argument("repo", type=Path)
    spike_open_parser.add_argument("files", nargs="*")
    spike_close_parser = sub.add_parser("spike-close")
    spike_close_parser.add_argument("repo", type=Path)
    spike_close_parser.add_argument("worktree", type=Path)
    args = parser.parse_args(argv)
    code = run_command(args, stdin)
    print(f"exit: {code}")
    return code


def run_command(args, stdin):
    try:
        if args.command in ("seal", "reseal"):
            spec_text = sys.stdin.read() if stdin is None else stdin
            errors = []
            if args.command == "reseal":
                spec_text, errors = reseal_spec(args.repo, spec_text)
            errors = errors or seal(args.repo, spec_text)
            for error in errors:
                print(error)
            return 1 if errors else 0
        if args.command in ("spike-open", "spike-close"):
            errors = spike_open(args.repo, args.files) if args.command == "spike-open" else spike_close(args.repo, args.worktree)
            for error in errors:
                print(error)
            return 1 if errors else 0
        if args.command == "report":
            errors = report(args.repo, args.plan)
            for error in errors:
                print(error)
            return 1 if errors else 0
        if args.command == "check" and args.paths:
            protection(args.repo, args.paths)
            return 0
        info, findings = inspect(args.repo)
    except RuntimeError as exc:
        print(f"git: {exc}")
        return 1
    if info:
        for key, value in info.items():
            if key not in ("recorded", "mapping"):
                print(f"{key}: {value}")
    for finding in findings:
        print(finding)
    if findings:
        return 1
    if args.command == "verify":
        failures = verify(args.repo, info)
        for failure in failures or [REPORT_REMINDER]:
            print(failure)
        return 1 if failures else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
