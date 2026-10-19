import collections
import json
import sys

labels = []
passes = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for argument in sys.argv[1:]:
    label, paths = argument.split("=", 1)
    labels.append(label)
    for path in paths.split(","):
        with open(path) as handle:
            result = json.load(handle)
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
