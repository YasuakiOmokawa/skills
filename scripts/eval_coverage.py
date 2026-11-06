from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from scripts.check_version_bump import plugins_with_shipped_changes

RECORD_NAME = "last-run.json"
SHIPPED_DIRECTORIES = ("skills", "commands")


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, text=True, capture_output=True).stdout


def shipped_digest(plugin_root: Path) -> str:
    tracked = _git("-C", str(plugin_root), "ls-files", "--", *SHIPPED_DIRECTORIES).splitlines()
    digest = hashlib.sha256()
    for relative in sorted(tracked):
        digest.update(relative.encode() + b"\0" + (plugin_root / relative).read_bytes() + b"\0")
    return digest.hexdigest()


def case_names(plugin_root: Path) -> set[str]:
    return {path.parent.name for path in (plugin_root / "evals").glob("*/prompt.md")}


def tally(results: list[dict]) -> dict[str, dict[str, int]]:
    cases: dict[str, dict[str, int]] = {}
    for result in results:
        for case in result["cases"]:
            passed = total = 0
            for run in case["arms"].get("with") or []:
                for grader in run.get("graders") or []:
                    total += 1
                    passed += 1 if grader.get("passed") else 0
            cases[case["name"]] = {"passed": passed, "total": total, **({"startedAt": result["startedAt"]} if result.get("startedAt") else {})}
    return cases


def coverage_errors(plugin: str, record: dict | None, digest: str, cases: set[str]) -> list[str]:
    where = f"plugins/{plugin}/evals/{RECORD_NAME}"
    if record is None:
        return [f"{where}: shipped content changed, so record an eval run (or a waiver) with scripts/eval_coverage.py"]
    errors = []
    if record.get("shipped_sha256") != digest:
        errors.append(f"{where}: recorded run is for different shipped content; rerun the suite or record a waiver")
    waived = record.get("waived")
    if isinstance(waived, str) and waived.strip():
        return errors
    missing = sorted(cases - set(record.get("cases") or {}))
    if missing:
        errors.append(f"{where}: cases not run: {', '.join(missing)}")
    return errors


def _load_record(plugin_root: Path) -> dict | None:
    path = plugin_root / "evals" / RECORD_NAME
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_record(plugin_root: Path, record: dict) -> None:
    path = plugin_root / "evals" / RECORD_NAME
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(path)


def _record(plugin_root: Path, result_paths: list[Path]) -> int:
    results = [json.loads(path.read_text(encoding="utf-8")) for path in result_paths]
    previous = _load_record(plugin_root) or {}
    digest = shipped_digest(plugin_root)
    cases = dict(previous.get("cases") or {}) if previous.get("shipped_sha256") == digest else {}
    cases.update(tally(results))
    _write_record(plugin_root, {"shipped_sha256": digest, "cases": cases, "waived": None})
    missing = sorted(case_names(plugin_root) - set(cases))
    if missing:
        print(f"cases not run yet: {', '.join(missing)}")
    return 0


def _waive(plugin_root: Path, reason: str) -> int:
    if not reason.strip():
        print("a waiver needs a reason", file=sys.stderr)
        return 1
    _write_record(plugin_root, {"shipped_sha256": shipped_digest(plugin_root), "cases": {}, "waived": reason})
    return 0


def _check(base_ref: str) -> int:
    changed = _git("diff", "--name-only", f"{base_ref}...HEAD").splitlines()
    errors = []
    for plugin in sorted(plugins_with_shipped_changes(changed)):
        plugin_root = Path("plugins") / plugin
        if not plugin_root.is_dir():
            continue
        errors += coverage_errors(plugin, _load_record(plugin_root), shipped_digest(plugin_root), case_names(plugin_root))
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print("OK: eval runs cover shipped plugin changes")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="eval_coverage")
    sub = parser.add_subparsers(dest="command", required=True)
    record = sub.add_parser("record")
    record.add_argument("plugin_root", type=Path)
    record.add_argument("results", type=Path, nargs="+")
    waive = sub.add_parser("waive")
    waive.add_argument("plugin_root", type=Path)
    waive.add_argument("reason")
    check = sub.add_parser("check")
    check.add_argument("base_ref")
    args = parser.parse_args(argv)
    if args.command == "record":
        return _record(args.plugin_root, args.results)
    if args.command == "waive":
        return _waive(args.plugin_root, args.reason)
    return _check(args.base_ref)


if __name__ == "__main__":
    raise SystemExit(main())
