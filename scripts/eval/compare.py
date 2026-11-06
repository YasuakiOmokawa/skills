import collections
import json
import sys
from pathlib import Path



def recorded_results(plugin_root):
    record = json.loads((plugin_root / "evals" / "last-run.json").read_text(encoding="utf-8"))
    for name, entry in sorted((record.get("cases") or {}).items()):
        if not entry.get("startedAt"):
            sys.exit(f"{plugin_root}: {name} has no startedAt in last-run.json; record it again with eval_coverage")
        stamp = entry["startedAt"].replace(":", "-").replace(".", "-")
        path = plugin_root / "evals" / "results" / stamp / "aggregate-result.json"
        if not path.exists():
            sys.exit(f"{path}: missing; results are kept only on the machine that ran the eval")
        result = json.loads(path.read_text(encoding="utf-8"))
        yield {"cases": [case for case in result["cases"] if case["name"] == name]}


def load(paths):
    for path in paths.split(","):
        if path.startswith("@"):
            yield from recorded_results(Path(path[1:]))
        else:
            with open(path) as handle:
                yield json.load(handle)


labels = []
passes = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for argument in sys.argv[1:]:
    label, paths = argument.split("=", 1)
    labels.append(label)
    for result in load(paths):
        for case in result["cases"]:
            for run in case["arms"].get("with") or []:
                if run.get("error"):
                    print(f"ERROR {label} {case['name']}: {str(run['error'])[:120]}", file=sys.stderr)
                for grader in run.get("graders") or []:
                    if grader["name"] == "skill-fired":
                        continue
                    key = (case["name"][:2], grader["name"])
                    passes[key][label][1] += 1
                    passes[key][label][0] += 1 if grader.get("passed") else 0

print(f"{'case/grader':48s} " + " ".join(f"{label:>9s}" for label in labels))
totals = {label: [0, 0] for label in labels}
for key in sorted(passes):
    cells = []
    for label in labels:
        passed, runs = passes[key][label]
        cells.append(f"{passed}/{runs}" if runs else "-")
        totals[label][0] += passed
        totals[label][1] += runs
    rates = [passes[key][label][0] / passes[key][label][1] for label in labels if passes[key][label][1]]
    marker = "  <<" if rates and max(rates) - min(rates) >= 0.3 else ""
    print(f"{key[0] + ' ' + key[1]:48s} " + " ".join(f"{cell:>9s}" for cell in cells) + marker)
print(f"{'TOTAL pass rate':48s} " + " ".join(f"{totals[l][0] / totals[l][1]:9.3f}" for l in labels))
