import json
import pathlib
import subprocess
import sys

result_path, case_prefix, grader_path = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
votes_per_run = int(sys.argv[4]) if len(sys.argv) > 4 else 3
criterion = grader_path.read_text().split("---", 2)[2].strip()
grader_name = grader_path.stem

with open(result_path) as handle:
    result = json.load(handle)
for case in result["cases"]:
    if not case["name"].startswith(case_prefix):
        continue
    for index, run in enumerate(case["arms"].get("with") or []):
        grader = next(g for g in run["graders"] if g["name"] == grader_name)
        if grader.get("passed"):
            continue
        prompt = (
            "You are grading the output of a coding agent against a criterion.\n\n"
            f"Criterion:\n{criterion}\n\n"
            f"Agent output:\n{grader.get('evidence', '')}\n\n"
            "Respond with exactly one word: PASS or FAIL."
        )
        votes = [
            subprocess.run(
                ["claude", "-p", "--model", "sonnet"], input=prompt, capture_output=True, text=True
            ).stdout.strip().split()[0:1]
            for _ in range(votes_per_run)
        ]
        print(case["name"], f"run {index}", [vote[0] if vote else "" for vote in votes])
