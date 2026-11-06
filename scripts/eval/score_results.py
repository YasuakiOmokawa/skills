import argparse
import json
import re
import sys
from pathlib import Path

from scripts.eval import mutant_score, restore_file
from scripts.eval_coverage import shipped_digest

ROOT = Path(__file__).resolve().parents[2]
GATE_HALT = re.compile(r"Gate[^\n]{0,80}(?:not ready|ready でない|ready にならな|ready ではな)", re.I)
RECORD_NAME = "mutant-record.json"


def last_message(trace_path):
    text = ""
    for raw in Path(trace_path).read_text(encoding="utf-8").splitlines():
        event = json.loads(raw)
        if event.get("type") == "result":
            text = event.get("result") or ""
    return text


def score_code(run, mapping, durable):
    subject = ROOT / mapping["subject"]
    target = json.loads((subject / "subject.json").read_text(encoding="utf-8"))["target"]
    stub = (subject / "stub.js").read_text(encoding="utf-8")
    source = restore_file.cat_output(Path(run["tracePath"]), target)
    if source is None:
        source, bash_writes = restore_file.restore(Path(run["tracePath"]), target, base=stub)
        if bash_writes:
            return {"code": "unrestorable"}
    if source == stub:
        return {"code": "unchanged"}
    destination = durable / target
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(source, encoding="utf-8")
    return {"code": "scored", **mutant_score.score_code(subject, source)}


def score_run(run, mapping, durable):
    code = score_code(run, mapping, durable) if mapping.get("code") else {}
    restored = restore_file.cat_output(Path(run["tracePath"]), mapping["test"])
    if restored is None:
        restored, _ = restore_file.restore(Path(run["tracePath"]), mapping["test"])
    if restored is None:
        outcome = "gate" if GATE_HALT.search(last_message(run["tracePath"])) else "no-test"
        return {"outcome": outcome, **code}
    target = durable / mapping["test"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(restored, encoding="utf-8")
    report = mutant_score.score(ROOT / mapping["subject"], durable, [mapping["test"]])
    return {
        "outcome": "tests",
        "tests": report["tests"],
        "valid": report["reference_pass"],
        "invalid": report["reference_failures"],
        "requirement_killed": report["killed"],
        "requirement_total": report["mutant_total"],
        "requirement_survivors": sorted(m for m, v in report["mutants"].items() if not v["killed_by"]),
        "auto_killed": report["auto"]["killed"],
        "auto_killable": report["auto"]["killable"],
        "auto_survivors": report["auto"]["survivors"],
        "repeatable": report["reference_repeatable"],
        **code,
    }


def score_result(result_path):
    result = json.loads(Path(result_path).read_text(encoding="utf-8"))
    plugin_root = Path(result["suite"]["root"])
    durable_root = Path(f"{result_path}.restored")
    scored = {}
    for case in result["cases"]:
        mapping_path = plugin_root / case["dir"] / "mutant.json"
        if not mapping_path.exists():
            continue
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        scored[case["name"]] = {
            arm: [score_run(run, mapping, durable_root / case["name"] / f"{arm}{index}") for index, run in enumerate(runs)]
            for arm, runs in case["arms"].items()
        }
    return plugin_root, result.get("startedAt"), scored


def cell(runs, key_killed, key_total):
    scored = [r for r in runs if r["outcome"] == "tests"]
    return " ".join(f"{r[key_killed]}/{r[key_total]}" for r in scored) or "-"


def table(case, arms):
    lines = [f"### {case}", "", "| arm | テストを書いた run | 全テストが有効な run | 要件適合度 | バグ検出率 |", "|---|---|---|---|---|"]
    for arm, runs in arms.items():
        written = sum(r["outcome"] == "tests" for r in runs)
        halted = sum(r["outcome"] == "gate" for r in runs)
        valid = sum(r["outcome"] == "tests" and r["valid"] == r["tests"] for r in runs)
        written_cell = f"{written}/{len(runs)}" + (f" (Gate で停止 {halted})" if halted else "")
        lines.append(f"| {arm} | {written_cell} | {valid}/{len(runs)} | {cell(runs, 'requirement_killed', 'requirement_total')} | {cell(runs, 'auto_killed', 'auto_killable')} |")
    if any("code" in r for runs in arms.values() for r in runs):
        lines += ["", "| arm | 隠しテストを全部通したコード | 隠しテストの pass |", "|---|---|---|"]
        for arm, runs in arms.items():
            scored = [r for r in runs if r.get("code") == "scored"]
            full = sum(r["hidden_passed"] == r["hidden_total"] for r in scored)
            passes = " ".join(f"{r['hidden_passed']}/{r['hidden_total']}" for r in scored) or "-"
            unrestorable = sum(r.get("code") == "unrestorable" for r in runs)
            unchanged = sum(r.get("code") == "unchanged" for r in runs)
            notes = [f"復元できず {unrestorable}"] * bool(unrestorable) + [f"未実装 {unchanged}"] * bool(unchanged)
            lines.append(f"| {arm} | {full}/{len(runs)}" + (f" ({', '.join(notes)})" if notes else "") + f" | {passes} |")
        for arm, runs in arms.items():
            for index, r in enumerate(runs):
                if r.get("hidden_failures"):
                    lines.append(f"- {arm}{index} のコードが落とした隠しテスト: {r['hidden_failures']}")
    for arm, runs in arms.items():
        for index, r in enumerate(runs):
            if r["outcome"] == "tests" and (r["invalid"] or r["requirement_survivors"] or r["auto_survivors"]):
                lines.append(f"- {arm}{index}: 無効 {r['invalid'][:3]} 生存 {r['requirement_survivors'] + r['auto_survivors']}")
    return "\n".join(lines) + "\n"


def record(plugin_root, started_at, scored):
    path = plugin_root / "evals" / RECORD_NAME
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    entry = data.setdefault(shipped_digest(plugin_root), {})
    for case, arms in scored.items():
        entry[case] = {"startedAt": started_at, "arms": arms}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(prog="score_results")
    parser.add_argument("results", nargs="+", type=Path)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args(argv)
    for result_path in args.results:
        plugin_root, started_at, scored = score_result(result_path)
        for case, arms in scored.items():
            print(table(case, arms))
        if args.record and scored:
            print(f"recorded: {record(plugin_root, started_at, scored)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
