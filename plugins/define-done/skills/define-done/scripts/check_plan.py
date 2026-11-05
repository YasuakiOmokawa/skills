import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

MANAGED_SECTIONS = ("Requirements", "Ground Review", "Acceptance Criteria", "MECE Review", "Verification Plan")
SEALED_SECTIONS = ("Requirements", "Acceptance Criteria", "Verification Plan")
FORBIDDEN_ORACLE = "check_plan.py の禁止の検査が通り、Violation sample を入れると落ち、除くと通る"
ENTRY_KEYS = ("Oracle", "Evidence anchors", "Prerequisites", "Required effects")
FORBIDDEN_KEYS = ("Violation sample", "Forbidden row")

REQUIREMENT_RE = re.compile(r"^- (R-\d+): (.+?) \(「(.+)」 ([^「」()]+)\)\s*$")
AC_RE = re.compile(r"^- (?:\[[ xX]\] )?(AC-\d{3}): \[(振る舞い|禁止)\] (.+) \(出典: ([^()]+)\)\s*$")
AC_ID_RE = re.compile(r"^- (?:\[[ xX]\] )?(AC-\d{3})\b")
ENTRY_RE = re.compile(r"^### (AC-\d{3})\s*$")
FIELD_RE = re.compile(r"^- ([A-Za-z ]+): (.*)$")
TABLE_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$")
HEADING_RE = re.compile(r"^(#{1,6}) (.+?)\s*$")
DECISION_RE = re.compile(r"(?<![A-Za-z0-9_])D[0-9]+(?![A-Za-z0-9_])")
SAMPLE_RE = re.compile(r"^`([^`]+)` に `(.+)`$")


@dataclass
class Finding:
    check: str
    line: int
    reason: str

    def render(self):
        return f"{self.check}: {self.line}: {self.reason}"


@dataclass
class Section:
    heading_line: int
    lines: list

    def numbered(self):
        return [(self.heading_line + offset + 1, line) for offset, line in enumerate(self.lines)]


@dataclass
class Plan:
    raw_lines: list
    sections: dict
    duplicates: list
    requirements: dict = field(default_factory=dict)
    acs: dict = field(default_factory=dict)
    entries: dict = field(default_factory=dict)
    mece: dict = field(default_factory=dict)
    vp_ids: tuple = None


def split_sections(raw_lines):
    sections, duplicates, current = {}, [], None
    for number, line in enumerate(raw_lines, 1):
        text = line.rstrip("\n")
        if text.startswith("## "):
            name = text[3:].strip()
            if name in MANAGED_SECTIONS:
                if name in sections:
                    duplicates.append((number, name))
                    current = None
                    continue
                current = Section(number, [])
                sections[name] = current
            else:
                current = None
            continue
        if current is not None:
            current.lines.append(text)
    return sections, duplicates


def parse_ids(value):
    return tuple(part.strip() for part in value.split(",") if part.strip())


def parse_plan(text):
    raw_lines = text.splitlines(keepends=True)
    sections, duplicates = split_sections(raw_lines)
    plan = Plan(raw_lines, sections, duplicates)
    findings = [Finding("format", number, f"節 `## {name}` が重複している") for number, name in duplicates]
    for name in MANAGED_SECTIONS:
        if name not in sections:
            findings.append(Finding("format", 1, f"節 `## {name}` が無い"))
    if "Requirements" in sections:
        findings += parse_requirements(plan, sections["Requirements"])
    if "Acceptance Criteria" in sections:
        findings += parse_acs(plan, sections["Acceptance Criteria"])
    if "MECE Review" in sections:
        findings += parse_mece(plan, sections["MECE Review"])
    if "Verification Plan" in sections:
        findings += parse_vp(plan, sections["Verification Plan"])
    return plan, findings


def parse_requirements(plan, section):
    findings = []
    for number, line in section.numbered():
        if not line.strip():
            continue
        match = REQUIREMENT_RE.match(line)
        if not match:
            findings.append(Finding("format", number, "要求の行が `- R-n: <要求> (「<引用>」 <場所>)` の形でない"))
            continue
        rid, body, quote, location = match.groups()
        if rid in plan.requirements:
            findings.append(Finding("format", number, f"{rid} が重複している"))
            continue
        plan.requirements[rid] = {"line": number, "body": body, "quote": quote, "location": location.strip()}
    return findings


def parse_acs(plan, section):
    findings = []
    for number, line in section.numbered():
        if not line.strip():
            continue
        match = AC_RE.match(line)
        if not match:
            id_match = AC_ID_RE.match(line)
            reason = "AC の行が `- AC-NNN: [振る舞い|禁止] <本文> (出典: <出典>)` の形でない"
            if id_match and "(出典:" not in line:
                reason = f"{id_match.group(1)} に出典が無い"
            findings.append(Finding("format", number, reason))
            continue
        ac_id, kind, body, sources = match.groups()
        if ac_id in plan.acs:
            findings.append(Finding("format", number, f"{ac_id} が重複している"))
            continue
        plan.acs[ac_id] = {"line": number, "kind": kind, "body": body, "sources": parse_ids(sources)}
    return findings


def parse_mece(plan, section):
    findings = []
    singles = {"AC IDs": [], "Gate": [], "Fingerprint": []}
    plan.mece = {"decisions": {}, "requirements": {}}
    for number, line in section.numbered():
        field_match = FIELD_RE.match(line)
        if field_match and field_match.group(1) in singles:
            singles[field_match.group(1)].append((number, field_match.group(2).strip()))
            continue
        row = TABLE_ROW_RE.match(line)
        if not row:
            continue
        key, value = row.groups()
        if DECISION_RE.fullmatch(key):
            plan.mece["decisions"][key] = (number, value)
        elif re.fullmatch(r"R-\d+", key):
            plan.mece["requirements"][key] = (number, value)
    for name in ("AC IDs", "Gate"):
        if len(singles[name]) != 1:
            findings.append(Finding("format", section.heading_line, f"`## MECE Review` に `- {name}:` 行がちょうど 1 つ無い"))
    if len(singles["Fingerprint"]) > 1:
        findings.append(Finding("format", section.heading_line, "`- Fingerprint:` 行が複数ある"))
    plan.mece["ac_ids"] = singles["AC IDs"][0] if len(singles["AC IDs"]) == 1 else None
    plan.mece["gate"] = singles["Gate"][0] if len(singles["Gate"]) == 1 else None
    plan.mece["fingerprint"] = singles["Fingerprint"][0] if len(singles["Fingerprint"]) == 1 else None
    return findings


def parse_vp(plan, section):
    findings = []
    current = None
    for number, line in section.numbered():
        entry = ENTRY_RE.match(line)
        if entry:
            ac_id = entry.group(1)
            if ac_id in plan.entries:
                findings.append(Finding("format", number, f"`### {ac_id}` が重複している"))
                current = None
                continue
            current = {"line": number, "fields": {}}
            plan.entries[ac_id] = current
            continue
        field_match = FIELD_RE.match(line)
        if not field_match:
            continue
        key, value = field_match.group(1), field_match.group(2).strip()
        if current is None:
            if key == "AC IDs":
                plan.vp_ids = (number, value)
            continue
        if key in current["fields"]:
            findings.append(Finding("format", number, f"`- {key}:` が重複している"))
            continue
        current["fields"][key] = (number, value)
    return findings


def negative_pathspec(spec):
    if spec.startswith((":!", ":^")):
        return True
    if spec.startswith(":("):
        magic = spec[2 : spec.find(")")] if ")" in spec else spec[2:]
        return "exclude" in magic.split(",")
    return False


def parse_forbidden_row(value):
    try:
        row = json.loads(value)
    except json.JSONDecodeError:
        return None, "`- Forbidden row:` が JSON として読めない"
    if not isinstance(row, dict) or set(row) != {"pattern", "pathspec"}:
        return None, "`- Forbidden row:` の key が `pattern` と `pathspec` の 2 つでない"
    if not isinstance(row["pattern"], str) or not row["pattern"]:
        return None, "`pattern` が空でない文字列でない"
    pathspec = row["pathspec"]
    if not isinstance(pathspec, list) or not pathspec or not all(isinstance(p, str) and p for p in pathspec):
        return None, "`pathspec` が空でない文字列の配列でない"
    negatives = [p for p in pathspec if negative_pathspec(p)]
    if negatives:
        return None, f"`pathspec` に除外 ({', '.join(negatives)}) がある。範囲は正の pathspec で絞る"
    return row, None


def parse_sample(value):
    match = SAMPLE_RE.match(value)
    if not match:
        return None
    return match.group(1), match.group(2)


def check_format(plan):
    findings = []
    ac_ids = tuple(sorted(plan.acs))
    gate = plan.mece.get("gate")
    if gate and gate[1] != "ready":
        findings.append(Finding("format", gate[0], "Gate が ready でない"))
    listed = plan.mece.get("ac_ids")
    if listed and parse_ids(listed[1]) != ac_ids:
        findings.append(Finding("format", listed[0], "`## MECE Review` の `- AC IDs:` が AC の集合 (昇順) と一致しない"))
    if "Verification Plan" in plan.sections:
        if plan.vp_ids is None:
            findings.append(Finding("format", plan.sections["Verification Plan"].heading_line, "`## Verification Plan` に `- AC IDs:` 行が無い"))
        elif parse_ids(plan.vp_ids[1]) != ac_ids:
            findings.append(Finding("format", plan.vp_ids[0], "`## Verification Plan` の `- AC IDs:` が AC の集合 (昇順) と一致しない"))
        for ac_id, ac in plan.acs.items():
            if ac_id not in plan.entries:
                findings.append(Finding("format", ac["line"], f"{ac_id} の `### {ac_id}` エントリが無い"))
        for ac_id, entry in plan.entries.items():
            if ac_id not in plan.acs:
                findings.append(Finding("format", entry["line"], f"`### {ac_id}` に対応する AC が無い"))
                continue
            findings += check_entry(ac_id, plan.acs[ac_id]["kind"], entry)
    return findings


def check_entry(ac_id, kind, entry):
    findings = []
    fields = entry["fields"]
    required = ENTRY_KEYS + (FORBIDDEN_KEYS if kind == "禁止" else ())
    for key in required:
        if key not in fields or not fields[key][1]:
            findings.append(Finding("format", entry["line"], f"{ac_id} に `- {key}:` が無い"))
    if kind != "禁止":
        return findings
    if "Oracle" in fields and fields["Oracle"][1] != FORBIDDEN_ORACLE:
        findings.append(Finding("format", fields["Oracle"][0], f"{ac_id} の `[禁止]` の Oracle が定型 `{FORBIDDEN_ORACLE}` でない"))
    if "Forbidden row" in fields:
        _, error = parse_forbidden_row(fields["Forbidden row"][1])
        if error:
            findings.append(Finding("format", fields["Forbidden row"][0], f"{ac_id}: {error}"))
    if "Violation sample" in fields and parse_sample(fields["Violation sample"][1]) is None:
        findings.append(Finding("format", fields["Violation sample"][0], f"{ac_id} の Violation sample が「`<path>` に `<内容>`」の形でない"))
    return findings


def normalize(text):
    return " ".join(text.split())


def plan_headings(plan):
    found = []
    for number, line in enumerate(plan.raw_lines, 1):
        match = HEADING_RE.match(line.rstrip("\n"))
        if match:
            found.append((number, len(match.group(1)), match.group(2).strip()))
    return found


def plan_section_text(plan, heading):
    headings = plan_headings(plan)
    for index, (number, level, text) in enumerate(headings):
        if text != heading:
            continue
        end = len(plan.raw_lines)
        for later_number, later_level, _ in headings[index + 1 :]:
            if later_level <= level:
                end = later_number - 1
                break
        return "".join(plan.raw_lines[number:end])
    return None


def check_source(plan, base):
    findings = []
    headings = {text for _, _, text in plan_headings(plan)}
    for rid, req in plan.requirements.items():
        location = req["location"]
        if location == "依頼" or re.fullmatch(r"issue#\d+", location):
            continue
        if location.startswith("計画:"):
            heading = location[len("計画:") :].strip()
            if heading in MANAGED_SECTIONS:
                findings.append(Finding("source", req["line"], f"{rid} の引用元 `## {heading}` は define-done が書く節で、要求の引用元にできない"))
                continue
            text = plan_section_text(plan, heading)
            if text is None:
                findings.append(Finding("source", req["line"], f"{rid} の引用元の見出し `{heading}` が計画に無い"))
            elif normalize(req["quote"]) not in normalize(text):
                findings.append(Finding("source", req["line"], f"{rid} の引用が計画の `{heading}` の節に原文のまま無い"))
            continue
        content, error = base.read(location)
        if error:
            findings.append(Finding("source", req["line"], f"{rid} の引用元 `{location}` を base の tree で読めない ({error})"))
        elif normalize(req["quote"]) not in normalize(content):
            findings.append(Finding("source", req["line"], f"{rid} の引用が `{location}` に原文のまま無い"))
    for ac_id, ac in plan.acs.items():
        if not ac["sources"]:
            findings.append(Finding("source", ac["line"], f"{ac_id} に出典が無い"))
        for source in ac["sources"]:
            if re.fullmatch(r"R-\d+", source):
                if source not in plan.requirements:
                    findings.append(Finding("source", ac["line"], f"{ac_id} の出典 {source} が `## Requirements` に無い"))
            elif DECISION_RE.fullmatch(source):
                findings.append(Finding("source", ac["line"], f"{ac_id} の出典 {source} は計画の決定で、出典にできない"))
            elif source in headings or source.lstrip("#").strip() in headings:
                findings.append(Finding("source", ac["line"], f"{ac_id} の出典 `{source}` は計画の節で、出典にできない"))
            else:
                exists, error = base.exists(source)
                if not exists:
                    findings.append(Finding("source", ac["line"], f"{ac_id} の出典 `{source}` が base の tree に無い{f' ({error})' if error else ''}"))
    return findings


def decision_ids(plan):
    managed_lines = set()
    for section in plan.sections.values():
        managed_lines.add(section.heading_line)
        managed_lines.update(number for number, _ in section.numbered())
    found = {}
    for number, line in enumerate(plan.raw_lines, 1):
        if number in managed_lines:
            continue
        for token in DECISION_RE.findall(line):
            found.setdefault(token, number)
    return found


def check_coverage(plan):
    findings, notes = [], []
    cited = {source for ac in plan.acs.values() for source in ac["sources"]}
    rows = plan.mece.get("requirements", {})
    for rid, req in plan.requirements.items():
        row = rows.get(rid)
        if row and row[1].startswith("範囲外"):
            findings.append(Finding("coverage", row[0], f"{rid} を範囲外にしている。計画を直すか、利用者が要求を取り下げるまで進めない"))
        elif rid in cited:
            continue
        elif row and row[1].startswith("未検証"):
            notes.append(f"coverage: {rid}: {row[1]}")
        else:
            findings.append(Finding("coverage", req["line"], f"{rid} がどの AC の出典にも、`## MECE Review` の要求の表にも無い"))
    decision_rows = plan.mece.get("decisions", {})
    for token, number in decision_ids(plan).items():
        row = decision_rows.get(token)
        if row is None:
            findings.append(Finding("coverage", number, f"決定 {token} が `## MECE Review` の決定 → 要求の表に無い"))
            continue
        if row[1] == "範囲外":
            notes.append(f"coverage: {token}: 範囲外")
            continue
        for rid in parse_ids(row[1]):
            if rid not in plan.requirements:
                findings.append(Finding("coverage", row[0], f"決定 {token} の行が挙げる {rid} が `## Requirements` に無い"))
    return findings, notes


class Repo:
    def __init__(self, root, base_ref):
        self.root = root
        self.base_ref = base_ref
        self._commit = None

    def git(self, *args, stdin=None):
        return subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, input=stdin)

    def commit(self):
        if self._commit is not None:
            return self._commit, None
        ref = self.base_ref
        if ref is None:
            ref = "origin/main" if self.git("rev-parse", "--verify", "-q", "origin/main").returncode == 0 else "main"
        result = self.git("merge-base", "HEAD", ref)
        if result.returncode != 0:
            return None, f"`git merge-base HEAD {ref}` が失敗した: {result.stderr.strip()}"
        self._commit = result.stdout.strip()
        return self._commit, None

    def exists(self, path):
        commit, error = self.commit()
        if error:
            return False, error
        return self.git("cat-file", "-e", f"{commit}:{path}").returncode == 0, None

    def read(self, path):
        commit, error = self.commit()
        if error:
            return None, error
        result = self.git("show", f"{commit}:{path}")
        if result.returncode != 0:
            return None, "file が無い"
        return result.stdout, None

    def grep(self, row, plan_path):
        args = ["grep", "--untracked", "-n", "-E", "-e", row["pattern"], "--", *row["pathspec"]]
        try:
            relative = plan_path.resolve().relative_to(self.root.resolve())
            args.append(f":(exclude){relative.as_posix()}")
        except ValueError:
            pass
        result = self.git(*args)
        if result.returncode not in (0, 1):
            return None, result.stderr.strip() or f"git grep が exit {result.returncode} で終わった"
        return result.returncode == 0, None


def inside(root, target):
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def apply_sample(repo_root, sample_path, content):
    target = repo_root / sample_path
    if Path(sample_path).is_absolute() or not inside(repo_root, target):
        raise ValueError(f"見本の path `{sample_path}` が repo の外を指す")
    if target.exists():
        original = target.read_bytes()
        prefix = b"" if original.endswith(b"\n") or not original else b"\n"
        target.write_bytes(original + prefix + content.encode() + b"\n")

        def restore():
            target.write_bytes(original)
            if hashlib.sha256(target.read_bytes()).hexdigest() != hashlib.sha256(original).hexdigest():
                return f"`{sample_path}` を元に戻せなかった (sha256 が一致しない)"
            return None

        return restore
    created = None
    parent = target.parent
    while not parent.exists():
        created = parent
        parent = parent.parent
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content + "\n")

    def remove():
        target.unlink()
        if created is not None:
            shutil.rmtree(created)
        return None

    return remove


def check_forbidden(plan, repo, plan_path, expect_green):
    findings = []
    for ac_id, ac in plan.acs.items():
        if ac["kind"] != "禁止" or ac_id not in plan.entries:
            continue
        fields = plan.entries[ac_id]["fields"]
        if "Forbidden row" not in fields or "Violation sample" not in fields:
            continue
        row, error = parse_forbidden_row(fields["Forbidden row"][1])
        sample = parse_sample(fields["Violation sample"][1])
        if error or sample is None:
            continue
        line = fields["Forbidden row"][0]
        if expect_green:
            hit, error = repo.grep(row, plan_path)
            if error:
                findings.append(Finding("forbidden", line, f"{ac_id}: {error}"))
                continue
            if hit:
                findings.append(Finding("forbidden", line, f"{ac_id}: 見本なしで禁止の行に当たる"))
                continue
        try:
            undo = apply_sample(repo.root, *sample)
        except (OSError, ValueError) as exc:
            findings.append(Finding("forbidden", line, f"{ac_id}: 見本を入れられない ({exc})"))
            continue
        try:
            hit, error = repo.grep(row, plan_path)
        finally:
            undo_error = undo()
        if undo_error:
            findings.append(Finding("forbidden", line, f"{ac_id}: {undo_error}"))
        if error:
            findings.append(Finding("forbidden", line, f"{ac_id}: {error}"))
        elif not hit:
            findings.append(Finding("forbidden", line, f"{ac_id}: 見本を入れても禁止の行に当たらない"))
    return findings


def fingerprint(plan):
    digest = hashlib.sha256()
    for name in SEALED_SECTIONS:
        section = plan.sections.get(name)
        if section is None:
            continue
        start = section.heading_line - 1
        end = start + 1 + len(section.lines)
        digest.update("".join(plan.raw_lines[start:end]).encode("utf-8"))
    return digest.hexdigest()


def check_seal(plan):
    recorded = plan.mece.get("fingerprint")
    line = plan.sections["MECE Review"].heading_line if "MECE Review" in plan.sections else 1
    if recorded is None:
        return [Finding("seal", line, "`- Fingerprint:` 行が無い。define-done の seal を通っていない")]
    if recorded[1] != fingerprint(plan):
        return [Finding("seal", recorded[0], "fingerprint が一致しない。define-done の後で要求・AC・検証の対応付けが変わった")]
    return []


def run_checks(plan_path, repo, expect_green):
    plan, findings = parse_plan(plan_path.read_text(encoding="utf-8"))
    findings += check_format(plan)
    findings += check_source(plan, repo)
    coverage, notes = check_coverage(plan)
    findings += coverage
    findings += check_forbidden(plan, repo, plan_path, expect_green)
    return plan, findings, notes


def write_fingerprint(plan_path, plan, value):
    lines = list(plan.raw_lines)
    recorded = plan.mece.get("fingerprint")
    new_line = f"- Fingerprint: {value}\n"
    if recorded is not None:
        lines[recorded[0] - 1] = new_line
    else:
        gate_line = plan.mece["gate"][0]
        lines.insert(gate_line, new_line)
    plan_path.write_text("".join(lines), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="check_plan.py")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("seal", "check", "check-green"):
        command = sub.add_parser(name)
        command.add_argument("plan", type=Path)
        command.add_argument("repo", type=Path)
        command.add_argument("--base")
    args = parser.parse_args(argv)
    repo = Repo(args.repo, args.base)
    plan, findings, notes = run_checks(args.plan, repo, args.command == "check-green")
    if args.command != "seal":
        findings += check_seal(plan)
    for finding in findings:
        print(finding.render())
    for note in notes:
        print(note)
    if findings:
        return 1
    if args.command == "seal":
        value = fingerprint(plan)
        write_fingerprint(args.plan, plan, value)
        print(value)
    return 0


if __name__ == "__main__":
    sys.exit(main())
