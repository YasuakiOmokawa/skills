import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TAP_LINE = re.compile(r"^(\s*)(not ok|ok) \d+ - (.*?)(?: # .*)?$")
AC_ID = re.compile(r"AC-\d{3}")
REPEATS = 5


def leaf_results(tap):
    results, previous_indent = {}, None
    for line in tap.splitlines():
        match = TAP_LINE.match(line)
        if not match:
            continue
        indent = len(match.group(1))
        is_parent = previous_indent is not None and previous_indent > indent
        previous_indent = indent
        if is_parent:
            continue
        name = f"{indent}:{match.group(3)}"
        results[name] = match.group(2) == "ok"
    return results


def run_suite(source, tests_root, test_paths):
    with tempfile.TemporaryDirectory() as work:
        work = Path(work)
        for rel in test_paths:
            target = work / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(tests_root / rel, target)
        (work / "src").mkdir(exist_ok=True)
        (work / "src" / "reset.js").write_text(source, encoding="utf-8")
        (work / "package.json").write_text('{"type": "module"}\n', encoding="utf-8")
        completed = subprocess.run(
            ["node", "--test", "--test-reporter=tap", *test_paths],
            cwd=work, capture_output=True, text=True, timeout=120,
        )
        return leaf_results(completed.stdout)


def mutate(reference, mutation):
    count = reference.count(mutation["find"])
    if count != 1:
        raise ValueError(f"find matched {count} times")
    return reference.replace(mutation["find"], mutation["replace"])


def score(subject, tests_root, test_paths, stub):
    reference = (subject / "reference.js").read_text(encoding="utf-8")
    mutants = json.loads((subject / "mutants.json").read_text(encoding="utf-8"))
    runs = [run_suite(reference, tests_root, test_paths) for _ in range(REPEATS)]
    baseline = runs[0]
    passing = {name for name, ok in baseline.items() if ok}
    report = {
        "tests": len(baseline),
        "tests_with_ac_id": sum(1 for name in baseline if AC_ID.search(name)),
        "reference_pass": len(passing),
        "reference_failures": sorted(name for name, ok in baseline.items() if not ok),
        "reference_repeatable": all(run == baseline for run in runs),
        "mutants": {},
    }
    if stub is not None:
        stub_results = run_suite(stub.read_text(encoding="utf-8"), tests_root, test_paths)
        report["stub_red"] = sum(1 for name in passing if not stub_results.get(name, False))
    for mutant_id, mutation in mutants.items():
        results = run_suite(mutate(reference, mutation), tests_root, test_paths)
        killers = sorted(name for name in passing if not results.get(name, False))
        report["mutants"][mutant_id] = {"requirement": mutation["requirement"], "killed_by": killers}
    report["killed"] = sum(1 for m in report["mutants"].values() if m["killed_by"])
    report["mutant_total"] = len(mutants)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(prog="mutant_score.py")
    parser.add_argument("subject", type=Path)
    parser.add_argument("tests_root", type=Path)
    parser.add_argument("test_paths", nargs="+")
    parser.add_argument("--stub", type=Path)
    args = parser.parse_args(argv)
    report = score(args.subject, args.tests_root, args.test_paths, args.stub)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
