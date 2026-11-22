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

REPORT_PLACEHOLDER = "{report}"
AC_ID = re.compile(r"AC-\d{3}")
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
KINDS = {"規則": "rule", "非影響": "non-impact"}
DEPENDENCY_DIRS = ("node_modules", ".venv", "vendor/bundle")
SPIKE_RECORD = "define-done-spike-paths"
CHECK_RECORD = "define-done-checks"
PLAN_BASELINE = "Define-Done-Plan-Outside"
PLAN_BASELINE_LINE = re.compile(rf"^{PLAN_BASELINE}: ([0-9a-f]{{64}})$", re.M)
REJECTED_DECISIONS = "検査が拒んだ決定"
CHECK_COMMAND_REQUIREMENT = re.compile(r"`[^`]+`\s*(?:が|も)\s*(?:すべて|全部)?\s*(?:通る|成功する)[。.]?")
NON_GOAL_REQUIREMENT = re.compile(r"(?:まだ|今回は|(?:この|本) ?(?:issue|PR|計画) ?では)\s*(?:作ら|実装し|扱わ|含め|入れ)ない")
REQUIREMENT_TEXT = re.compile(r"^- (R-\d+):[ \t]*(.*)$", re.M)
QUOTE_OPENING = "(「"
RESIDUAL_RISKS = "残ったリスク"
RISK_DESTINATIONS = ("`AC-NNN`", "`実装のテスト:`", "`既存のテスト:`", "`規約`", "`未検証:`")
RISK_DESTINATION = re.compile(r"AC-\d{3}|(?:実装のテスト|既存のテスト|未検証)[:：]|規約")
IMPLEMENTATION_TEST_ROW = re.compile(r"実装のテスト[:：]")
EXISTING_TEST_ROW = re.compile(r"既存のテスト[:：](.*)")
PATH_TOKEN = re.compile(r"[\w@.+\-/]+")
NOTHING_NOTED = re.compile(r"-?\s*(?:無い|無し|なし|ない|該当なし|該当無し)(?:[\s。.、(（].*)?")
TABLE_RULE = re.compile(r"^\|[\s:|-]+\|$")
IMPORT_LINE = re.compile(r"\s*(?:import\b|from\s+\S+\s+import\b|require(?:_relative)?\b|(?:const|let|var)\s[^=]*=\s*require\()")
NO_NEWLINE = "\\ No newline at end of file"


def git(repo, *args):
    completed = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout


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


def at_path(entry, paths):
    reported = [candidate.replace("\\", "/").removeprefix("./") for candidate in entry["files"]]
    return any(candidate == path or candidate.endswith("/" + path) for candidate in reported for path in paths)


def matches(entry, test):
    return in_files(entry, [test["file"]]) and any(name == test["name"] or name.endswith(test["name"]) for name in entry["names"] if name)


def states_by_ac(entries, mapping):
    states = {}
    for test in mapping:
        found = [entry["state"] for entry in entries if matches(entry, test)]
        states.setdefault(test["ac"], []).extend(found or ["missing"])
    return states


def outcome(states):
    if not states or "missing" in states or "skipped" in states:
        return "missing"
    if all(state == "fail" for state in states):
        return "fail"
    if all(state == "pass" for state in states):
        return "pass"
    return "mixed"


def changed_files(repo, files):
    entries = git(repo, "status", "--porcelain", "-z", "--untracked-files=all", "--", *files).split("\0")
    dirty = {entry[3:] for entry in entries if len(entry) > 3}
    return [path for path in files if path in dirty]


SET_ASIDE_MESSAGE = "define-done check: 受け入れテストの外の変更"


def outside_paths(repo, files):
    tracked = git(repo, "diff", "--name-only", "--no-renames", "-z", "HEAD").split("\0")
    untracked = git(repo, "ls-files", "--others", "--exclude-standard", "-z").split("\0")
    given = set(files)
    return sorted({path for path in tracked + untracked if path and path not in given})


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
            raise RuntimeError("受け入れテストの外の変更を退避できなかった")

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
            return [f"set-aside: 受け入れテストの外の変更を戻せなかった ({exc})。{kept}"]
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
    given = sorted(touched & set(files))
    if given:
        return [f"spike: 試作の実装の patch が、渡したファイル {', '.join(given)} を変えている"]
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
    return [f"plan: 計画の 4 節の外が `spike-open` の後に変わっている。計画の本文は元に戻し、検査が拒んだ決定は `## MECE Review` の `### {REJECTED_DECISIONS}` に書く (計画の本文を直すのは呼び出し側。直した後の計画で確かめるなら `spike-open` からやり直す)"]


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


def final_answer(plan, checked):
    sections = plan_sections(plan.read_text(encoding="utf-8"))
    review = sections["MECE Review"][0]
    ground = sections.get("Ground Review", [""])[0]
    rows = table_rows(review)
    rejected = next((text for title, text in subsections(review) if title == REJECTED_DECISIONS), "")
    kinds = [kind for _, kind, _ in CRITERION_LINE.findall(sections["Acceptance Criteria"][0])]
    unverified = [
        *noted_lines(ground, lambda title: title.startswith("未検証")),
        *[line for line in review.splitlines() if line.startswith("- 未検証")],
        *[line for line in noted_lines(review, lambda title: "未検証" in title) if not line.startswith("|")],
        *[line for line, cells in rows if len(cells) > 1 and not REQUIREMENT_ID.fullmatch(cells[0]) and cells[1].startswith("未検証")],
    ]
    patch = checked.get("spike", "")
    groups = [
        ("書き直した既存のテスト", [f"{target}: {reason}" for target, reason in checked.get("rewrites", {}).items()]),
        ("新しく作ったディレクトリ", [f"{target}: {reason}" for target, reason in checked.get("new_dirs", {}).items()]),
        ("実装の後に確かめた基準 (実装の前に落ちることは確かめていない)", checked.get("implemented", [])),
        ("基準の無い要求", [line for line, cells in rows if len(cells) > 1 and REQUIREMENT_ID.fullmatch(cells[0]) and ROW_WITHOUT_CRITERION.match(cells[1])]),
        ("実装が足すテスト", [line for line, cells in rows if len(cells) > 1 and cells[1].startswith("実装のテスト")]),
        ("実装のテストの対応 (作業ツリーの実装で通った)", [f"{test['risk']}: {test['file']}「{test['name']}」" for test in checked.get("impl_tests", [])]),
        ("未決の判断", noted_lines(ground, lambda title: title.startswith("未決"))),
        ("未検証", list(dict.fromkeys(unverified))),
        (REJECTED_DECISIONS, [line for line, _ in table_rows(rejected)[1:]]),
    ]
    lines = [
        "要求:",
        *[line for line in sections["Requirements"][0].splitlines() if REQUIREMENT_LINE.match(line)],
        f"Gate: {GATE_LINE.findall(review)[0].strip()}",
        f"AC: 規則 {kinds.count('規則')} 件、非影響 {kinds.count('非影響')} 件",
        f"テストを確かめた AC: {', '.join(checked['acs'])}" if checked.get("acs") else "テストを確かめた AC: 無い (`check` が通っていない)",
        *([f"ファイル: {', '.join(checked['files'])}"] if checked.get("files") else []),
        *([f"試作の patch: {patch}"] if patch and Path(patch).is_file() else []),
        *(["実装: 作業ツリーの実装で、テストを対応させた基準がすべて通った"] if checked.get("worktree") else []),
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
    return None, ["plan: 計画が渡したファイルに無い (repo の中の計画は files に入れ、repo の外の計画は `plan` に path を渡す)"]


def plan_findings(plan, tested):
    try:
        sections = plan_sections(plan.read_text(encoding="utf-8"))
    except OSError:
        return [f"plan: 計画 {plan} を読めない"], {}
    counts = {title: len(sections.get(title, [])) for title in PLAN_SECTIONS}
    if any(count != 1 for count in counts.values()):
        return [f"plan: 計画に `## {title}` の節が {count} 個ある (それぞれ 1 つにする)" for title, count in counts.items() if count != 1], {}
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
        errors.append(f"plan: Gate が ready でない計画には受け入れテストを書かない (`- Gate: {gates[0].strip()}`)")
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
    kinds = {}
    for ac in sorted(tested):
        entry = criteria.get(ac)
        if entry is None:
            errors.append(f"plan: テストを対応させた {ac} が計画の `## Acceptance Criteria` に無い")
            continue
        if entry["kind"] in KINDS:
            kinds[ac] = KINDS[entry["kind"]]
        else:
            errors.append(f"plan: {ac} の行に種類の印 (`[規則]` か `[非影響]`) が無い")
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
        if not AC_ID.match(cell.lstrip(" \t`*")):
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
    return errors, kinds


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
        return [f"spike: 複製の {', '.join(stale)} が repo と食い違う (受け入れテストは repo で直し、複製へ写し直す)"]
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
    print(f"deviations: 試作が計画の決定と違う形を取ったなら、`## MECE Review` の `### {REJECTED_DECISIONS}` の表に書き、`check` の JSON の \"deviations\" に決定の ID を挙げる (違わなければ空の配列)")
    return []


def risk_rows(review):
    rows = []
    for title, text in subsections(review):
        if RESIDUAL_RISKS in title:
            rows.extend((cells[0], cells[1].lstrip("`* ")) for _, cells in table_rows(text)[1:] if len(cells) > 1)
    return rows


def guarded_risks(repo, review):
    errors, files, implementation_risks = [], [], []
    for risk, destination in risk_rows(review):
        existing = EXISTING_TEST_ROW.match(destination)
        if IMPLEMENTATION_TEST_ROW.match(destination):
            implementation_risks.append(risk)
        elif existing:
            named = [token.strip(".") for token in PATH_TOKEN.findall(existing.group(1)) if "/" in token or "." in token.strip(".")]
            tracked = [path for path in named if tracked_at_head(repo, path)]
            if not tracked:
                errors.append(f"guard: 残ったリスクの表の「{risk}」の守る先の既存のテストが HEAD に無い (`既存のテスト:` の後に、変更の前からあるテストのファイルを repo からの相対 path で書く)")
            files.extend(tracked)
    return errors, list(dict.fromkeys(files)), implementation_risks


def decision_findings(review, deviations):
    if deviations is None:
        return []
    rejected = next((text for title, text in subsections(review) if title == REJECTED_DECISIONS), "")
    recorded = {cells[0].strip("`* ") for _, cells in table_rows(rejected)[1:] if cells and cells[0].strip("`* ")}
    declared = {str(decision).strip() for decision in deviations}
    errors = [f"deviations: {decision} を申告したが、`## MECE Review` の `### {REJECTED_DECISIONS}` の表に行が無い (`| <決定の ID> | <拒んだ検査とその理由> | <代わりに取る形> |` を書く)" for decision in sorted(declared - recorded)]
    errors += [f"deviations: `### {REJECTED_DECISIONS}` の表に {decision} があるが、標準入力の JSON の \"deviations\" に挙げていない" for decision in sorted(recorded - declared)]
    return errors


def implementation_test_findings(implementation_tests, implementation_risks, complete):
    errors = []
    for test in implementation_tests:
        if not test["risk"] or not test["file"] or not test["name"] or "\n" in test["name"]:
            errors.append(f"impl_tests: 対応 {test} の risk、file、name のどれかが読めない")
        elif test["risk"] not in implementation_risks:
            errors.append(f"impl_tests: 「{test['risk']}」は、残ったリスクの表の守る先が `実装のテスト:` の行のリスクでない (表のリスクの文をそのまま渡す)")
    if complete:
        mapped = {test["risk"] for test in implementation_tests}
        errors.extend(f"impl_tests: 残ったリスクの表の「{risk}」を守る実装のテストの対応が無い (標準入力の JSON の \"impl_tests\" に risk、file、name を挙げる)" for risk in implementation_risks if risk not in mapped)
    return errors


def guard_findings(repo, guard_command, guard_files, implementation_tests, tree):
    if not guard_command or not (guard_files or implementation_tests):
        return []
    _, output, entries = run_tests(repo, guard_command)
    errors = []
    for path in guard_files:
        states = [entry["state"] for entry in entries if in_files(entry, [path])]
        if "fail" in states:
            errors.append(f"guard: 既存のテスト {path} が{tree}で落ちた (実装が既存の保証を壊していないかを確かめる)")
        elif "pass" not in states:
            errors.append(f"guard: 既存のテスト {path} が{tree}で実行されなかった (guard_command がそのファイルを流し、結果を {REPORT_PLACEHOLDER} に書くようにする)")
    for test in implementation_tests:
        states = [entry["state"] for entry in entries if matches(entry, test)]
        if not states:
            errors.append(f"guard: 実装のテスト「{test['name']}」({test['file']}) が{tree}で実行されなかった (guard_command がそのファイルを流し、テスト名の対応を確かめる)")
        elif any(state != "pass" for state in states):
            errors.append(f"guard: 実装のテスト「{test['name']}」({test['file']}) が{tree}で通らない")
    if errors:
        print(output[-4000:])
    else:
        print(f"guard: pass ({tree})")
    return errors


def remembered(repo):
    record = Path(repo) / git(repo, "rev-parse", "--git-common-dir").strip() / CHECK_RECORD
    try:
        return record, json.loads(record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return record, {}


def remember(repo, plan, checked):
    record, known = remembered(repo)
    key = str(plan.resolve())
    known.pop(key, None)
    known[key] = checked
    try:
        record.write_text(json.dumps(known, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def ran_names(entries, path):
    return [next((name for name in entry["names"] if name), "") for entry in entries if in_files(entry, [path])]


def tracked_at_head(repo, path):
    return subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"HEAD:{path}"], capture_output=True).returncode == 0


def line_changes(repo, path):
    if not tracked_at_head(repo, path):
        return (Path(repo) / path).read_text(encoding="utf-8", errors="replace").splitlines(), []
    diff = git(repo, "diff", "--no-color", "--no-ext-diff", "-U0", "HEAD", "--", path).splitlines()
    hunks = diff[next((index for index, line in enumerate(diff) if line.startswith("@@")), len(diff)):]
    added = [line[1:] for line in hunks if line.startswith("+")]
    unterminated = {line[1:] for line, following in zip(hunks, hunks[1:]) if line.startswith("-") and following == NO_NEWLINE}
    removed = [line[1:] for line in hunks if line.startswith("-") and not IMPORT_LINE.match(line[1:]) and not (line[1:] in unterminated and line[1:] in added)]
    return added, removed


def place_findings(repo, paths, new_dirs):
    errors = []
    for directory in sorted({posixpath.dirname(path) for path in paths}):
        declared = any(directory == made or directory.startswith(made + "/") for made in new_dirs)
        if directory and not declared and not tracked_at_head(repo, directory):
            errors.append(f"place: {directory}/ は HEAD に無い。既存のテストの置き場所に書く。repo の規則 (製品コードの構造を写す、など) が新しいディレクトリを求めるときと、依頼が名指しした置き場所が無いときだけ、標準入力の JSON の \"new_dirs\" に path と理由を挙げる")
    return errors


def existing_findings(repo, paths, rewrites):
    errors = []
    for path in paths:
        added, removed = line_changes(repo, path)
        if removed and path not in rewrites:
            errors.append(f"existing: {path} の既存の行を {len(removed)} 行、変えるか消している (最初の行: {removed[0].strip()})。既存のテストと補助には足すだけにする (import の行は数えない)。要求が既存のテストの固定する振る舞いを変えるときだけ、標準入力の JSON の \"rewrites\" に file と理由を挙げる")
        if any(AC_ID.search(line) for line in added):
            errors.append(f"tests: {path} に AC-ID を書かない (AC との対応は標準入力の JSON で渡す)")
    return errors


def noted(entries, key):
    return {str(entry.get(key, "")).rstrip("/"): str(entry.get("reason", "")).strip() for entry in entries or [] if isinstance(entry, dict)}


def check(repo, spec_text):
    try:
        spec = json.loads(spec_text)
    except json.JSONDecodeError as exc:
        return [f"spec: 標準入力の JSON を読めない ({exc})"]
    test_command, check_command, spike = str(spec.get("test_command") or ""), str(spec.get("check_command") or ""), str(spec.get("spike") or "")
    files = list(dict.fromkeys(spec.get("files") or []))
    mapping = [{"ac": str(test.get("ac", "")), "file": str(test.get("file", "")), "name": str(test.get("name", ""))} for test in spec.get("tests") or []]
    rewrites, new_dirs = noted(spec.get("rewrites"), "file"), noted(spec.get("new_dirs"), "path")
    implemented = sorted({str(ac) for ac in spec.get("implemented") or []})
    worktree, guard_command, deviations = spec.get("worktree") is True, str(spec.get("guard_command") or ""), spec.get("deviations")
    implementation_tests = [{"risk": str(test.get("risk", "")).strip(), "file": str(test.get("file", "")), "name": str(test.get("name", ""))} for test in spec.get("impl_tests") or [] if isinstance(test, dict)]
    errors = []
    if REPORT_PLACEHOLDER not in test_command:
        errors.append(f"command: test_command に結果の出力先 {REPORT_PLACEHOLDER} が無い")
    if guard_command and REPORT_PLACEHOLDER not in guard_command:
        errors.append(f"command: guard_command に結果の出力先 {REPORT_PLACEHOLDER} が無い")
    if worktree and spike:
        errors.append("worktree: `worktree` と `spike` は一緒に渡さない (実装の前は試作の patch を `spike` に、実装の後は `\"worktree\": true` を渡す)")
    if deviations is not None and not isinstance(deviations, list):
        errors.append("deviations: 決定の ID の配列で渡す (違う形を取った決定が無ければ空の配列)")
    elif spike and deviations is None:
        errors.append(f"deviations: 試作が計画の決定と違う形を取ったかを申告する。違わなければ `\"deviations\": []` を渡す。違えば決定の ID を挙げ、`## MECE Review` の `### {REJECTED_DECISIONS}` の表に書く (計画の 4 節の外は直さない)")
    missing = [path for path in files if not (Path(repo) / path).is_file()]
    if missing:
        errors.append(f"files: {', '.join(missing)} が無い")
    elif files and not changed_files(repo, files):
        errors.append("files: 渡したファイルがどれも HEAD から変わっていない (受け入れテストを書いたファイル、足した補助と期待値のファイル、repo の中の計画を渡す)")
    if not mapping:
        errors.append("tests: AC とテストの対応が無い")
    for test in mapping:
        if not AC_ID.fullmatch(test["ac"]) or not test["name"] or "\n" in test["name"]:
            errors.append(f"tests: 対応 {test} の AC-ID かテスト名が読めない")
        elif test["file"] not in files:
            errors.append(f"tests: {test['ac']} のテストのファイル {test['file']} が files に無い")
    for key, reasons in (("rewrites", rewrites), ("new_dirs", new_dirs)):
        errors.extend(f"{key}: {target or '名前の無い項目'} の理由が無い" for target, reason in reasons.items() if not target or not reason)
    if errors:
        return errors
    plan, errors = locate_plan(repo, str(spec.get("plan") or ""), files)
    if errors:
        return errors
    errors, kinds = plan_findings(plan, {test["ac"] for test in mapping})
    errors.extend(f"implemented: {ac} はテストを対応させた `[規則]` の基準でない" for ac in implemented if kinds.get(ac, "rule") != "rule" or ac not in {test["ac"] for test in mapping})
    root = Path(repo).resolve()
    written = [path for path in files if (root / path).resolve() != plan.resolve()]
    errors += place_findings(repo, written, new_dirs) + existing_findings(repo, written, rewrites)
    if spike:
        errors.extend(spike_findings(repo, spike, files))
        if not errors:
            errors.extend(baseline_findings(plan, spike))
    guard_files, implementation_risks = [], []
    if not errors:
        review = plan_sections(plan.read_text(encoding="utf-8"))["MECE Review"][0]
        found, guard_files, implementation_risks = guarded_risks(repo, review)
        errors += found + decision_findings(review, deviations) + implementation_test_findings(implementation_tests, implementation_risks, worktree)
        if not guard_command and ((spike or worktree) and guard_files or worktree and implementation_tests):
            errors.append(f"guard: 残ったリスクの表の既存のテストと実装のテストを実装のある tree で流すコマンドを `guard_command` に渡す (結果を {REPORT_PLACEHOLDER} に JUnit XML か RSpec の JSON で書く)")
    aside = SetAside(repo, outside_paths(repo, files))
    if worktree and not errors and not aside.paths:
        errors.append("worktree: 渡したファイルの外に変更が無い (実装が作業ツリーに無い。実装が HEAD に入っているなら `worktree` を渡さず、標準入力の JSON の \"implemented\" に基準を挙げる)")
    if errors:
        return errors
    new_files = [path for path in written if not tracked_at_head(repo, path)]
    guard = {"command": guard_command, "files": guard_files, "tests": implementation_tests}
    try:
        proved, passing = {}, set()
        if worktree:
            errors, proved = worktree_findings(repo, test_command, new_files, mapping, kinds, check_command, guard)
            passing = {ac for ac, state in proved.items() if state == "pass"}
        elif aside.paths and not spike:
            passing = passing_criteria(kind_states(repo, test_command, new_files, mapping, kinds, implementation_tests))
        if not errors:
            aside.stash()
            errors = check_in_tree(repo, aside, test_command, new_files, mapping, kinds, spike, "" if worktree else check_command, passing, implemented, guard, proved)
        if not errors:
            print(f"checked: {', '.join(sorted(kinds))}")
            remember(repo, plan, {"acs": sorted(kinds), "files": written, "rewrites": rewrites, "new_dirs": new_dirs, "implemented": implemented, "spike": str(Path(spike).expanduser().absolute()) if spike else "", "worktree": worktree, "impl_tests": implementation_tests if worktree else []})
    except RuntimeError as exc:
        errors = [f"git: {exc}"]
    except subprocess.TimeoutExpired as exc:
        errors = [f"command: {exc.timeout:.0f} 秒で終わらなかった ({exc.cmd})"]
    except BaseException:
        for error in aside.restore():
            print(error)
        raise
    return errors + aside.restore()


def worktree_findings(repo, test_command, new_files, mapping, kinds, check_command, guard):
    trial = kind_states(repo, test_command, new_files, mapping, kinds, guard["tests"])
    errors = trial["unmatched"] + list(trial["missing"].values())
    for ac, state in sorted(trial["outcomes"].items()):
        if state != "pass" and state != "missing":
            errors.append(f"worktree: {ac} が作業ツリーの実装で通らない (実装を直す。実装の途中で種類だけを確かめるなら `worktree` を渡さない)")
    if errors:
        print(trial["output"][-4000:])
        return errors, trial["outcomes"]
    errors = run_check(repo, check_command) if check_command else []
    if not errors:
        errors = guard_findings(repo, guard["command"], guard["files"], guard["tests"], "作業ツリーの実装")
    return errors, trial["outcomes"]


def is_file_entry(entry, test_files):
    return any(same_file(name, path) for name in entry["names"] if name for path in test_files)


def kind_states(repo, test_command, new_files, mapping, kinds, implementation_tests=()):
    code, output, entries = run_tests(repo, test_command)
    unmatched = []
    mapped_files = {test["file"] for test in mapping}
    mapped_new_files = [path for path in new_files if path in mapped_files]
    unmapped_new_files = [path for path in new_files if path not in mapped_files]
    for entry in entries:
        in_new_file = in_files(entry, mapped_new_files) or at_path(entry, unmapped_new_files)
        if in_new_file and not is_file_entry(entry, new_files) and not any(matches(entry, test) for test in [*mapping, *implementation_tests]):
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
    return {"outcomes": outcomes, "states": states, "unmatched": unmatched, "missing": missing, "never_ran": never_ran, "output": output}


def passing_criteria(run):
    if run["unmatched"] or run["missing"]:
        return set()
    return {ac for ac, state in run["outcomes"].items() if state == "pass"}


UNLOADED_HINT = "変更前の tree に無い module をテストが静的に import していると、テストは落ちずに実行されない。試作の実装の patch を `spike` に渡すか、その module を実行時に import する"


def check_in_tree(repo, aside, test_command, new_files, mapping, kinds, spike, check_command, passing, implemented, guard, proved):
    if check_command and not spike:
        errors = run_check(repo, check_command)
        if errors:
            return errors
    run = kind_states(repo, test_command, new_files, mapping, kinds, guard["tests"])
    now, output = run["outcomes"], run["output"]
    unloaded = {ac for ac in run["never_ran"] if kinds[ac] == "rule"}
    errors = run["unmatched"] + [message for ac, message in run["missing"].items() if ac not in unloaded]
    if spike and not errors:
        patch = str(Path(spike).resolve())
        git(repo, "apply", patch)
        try:
            trial = kind_states(repo, test_command, new_files, mapping, kinds, guard["tests"])
            proved, passing = trial["outcomes"], passing_criteria(trial)
            errors = trial["unmatched"] + list(trial["missing"].values())
            for ac, state in sorted(proved.items()):
                if state != "pass" and state != "missing":
                    errors.append(f"spike: {ac} が試作の実装で通らない (テストと要求のどちらかを確かめる)")
            if errors:
                print(trial["output"][-4000:])
            elif check_command:
                errors = run_check(repo, check_command)
            if not errors:
                errors = guard_findings(repo, guard["command"], guard["files"], [], "試作の実装")
        finally:
            git(repo, "apply", "-R", patch)
        if errors:
            return errors
    implementation = ("spike" if spike else "worktree") if proved else ""
    for ac in sorted(unloaded - passing):
        errors.append(f"{run['missing'][ac]}。{UNLOADED_HINT}")
    if aside.sha and any(error.startswith("missing:") for error in errors):
        errors.append(f"missing: 渡したファイルの外の変更 ({len(aside.paths)} 件) は退避して流している。受け入れテストが、渡していない変更に頼っていないかを確かめる")
    for ac in sorted(unloaded & passing):
        now[ac] = outcome(["fail" if state == "missing" else state for state in run["states"][ac]])
        print(f"unloaded: {ac} のテストは変更前の tree で読み込めず実行されなかった。実装のある tree では通ったので、落ちたものと数える")
    for ac, kind in sorted(kinds.items()):
        state = now[ac]
        expected = "fail" if kind == "rule" and ac not in implemented else "pass"
        print(f"{ac}: {kind}{' implemented' if ac in implemented else ''}{f' {implementation}={proved[ac]}' if implementation else ''} now={state}")
        if state != "missing" and state != expected:
            hint = " (実装が HEAD に入っているなら、標準入力の JSON の \"implemented\" に挙げる)" if kind == "rule" and state == "pass" else ""
            errors.append(f"kind: {ac} は{'規則' if kind == 'rule' else '非影響'}の基準だが、今の tree で {state} だった{hint}")
    if errors:
        print(output[-4000:])
    return errors


def report(repo, named_plan):
    known = remembered(repo)[1]
    named = Path(named_plan).expanduser()
    key = str((named if named.is_absolute() else Path(repo) / named).resolve()) if named_plan else next(reversed(known), "")
    if not key:
        return ["report: `check` が通った計画の記録が無い (計画の path を渡す)"]
    try:
        print("\n".join(final_answer(Path(key), known.get(key, {}))))
    except (OSError, KeyError, IndexError):
        return [f"plan: 計画 {key} から最終回答を組み立てられない (4 節と `- Gate:` の行を確かめる)"]
    return []


def main(argv=None, stdin=None):
    parser = argparse.ArgumentParser(prog="check_done.py")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check").add_argument("repo", type=Path)
    report_parser = sub.add_parser("report")
    report_parser.add_argument("repo", type=Path)
    report_parser.add_argument("plan", nargs="?", default="")
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
        if args.command == "check":
            errors = check(args.repo, sys.stdin.read() if stdin is None else stdin)
        elif args.command == "report":
            errors = report(args.repo, args.plan)
        elif args.command == "spike-open":
            errors = spike_open(args.repo, args.files)
        else:
            errors = spike_close(args.repo, args.worktree)
    except RuntimeError as exc:
        errors = [f"git: {exc}"]
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
