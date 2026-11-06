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
HIDDEN_TEST = "test/hidden.test.js"
SWAPS = {"===": "!==", "!==": "===", "<=": "<", ">=": ">", "<": "<=", ">": ">=", "&&": "||", "||": "&&"}
SWAP_TOKENS = sorted(SWAPS, key=len, reverse=True)
ARITHMETIC = {"+": "-", "-": "+", "*": "/", "/": "*"}
NON_EXPRESSION_STATEMENT = re.compile(r"^(?:return|const|let|var|if|else|for|while|throw|export|import|function|case|default)\b|^[{}]")


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
        results[f"{indent}:{match.group(3)}"] = match.group(2) == "ok"
    return results


def code_spans(source):
    spans, i, start = [], 0, 0
    while i < len(source):
        char = source[i]
        if source.startswith("//", i):
            spans.append((start, i))
            i = source.find("\n", i)
            i = len(source) if i < 0 else i
            start = i
        elif source.startswith("/*", i):
            spans.append((start, i))
            i = source.index("*/", i) + 2
            start = i
        elif char in "'\"`":
            spans.append((start, i))
            i += 1
            while source[i] != char:
                i += 2 if source[i] == "\\" else 1
            i += 1
            start = i
        else:
            i += 1
    spans.append((start, len(source)))
    return spans


def position(source, offset):
    line = source.count("\n", 0, offset) + 1
    return f"L{line}C{offset - (source.rfind(chr(10), 0, offset) + 1) + 1}"


def auto_mutants(source):
    mutants = []
    for begin, end in code_spans(source):
        i = begin
        while i < end:
            token = next((t for t in SWAP_TOKENS if source.startswith(t, i)), None)
            if token and not (token == ">" and source[i - 1] == "="):
                mutants.append((f"swap-{position(source, i)}", source[:i] + SWAPS[token] + source[i + len(token):]))
                i += len(token)
                continue
            char = source[i]
            pair = source[i - 1:i + 2] if i > 0 else source[i:i + 2]
            if char in ARITHMETIC and not any(op in pair for op in ("++", "--", "+=", "-=", "**", "*=", "/=", "//", "/*", "*/")):
                mutants.append((f"arith-{position(source, i)}", source[:i] + ARITHMETIC[char] + source[i + 1:]))
            elif char == "!" and source[i + 1:i + 2] != "=":
                mutants.append((f"not-{position(source, i)}", source[:i] + source[i + 1:]))
            word = re.match(r"[A-Za-z_$][\w$]*|\d+", source[i:end])
            if word:
                text = word.group(0)
                if text.isdigit():
                    for delta, name in ((1, "inc"), (-1, "dec")):
                        mutants.append((f"{name}-{position(source, i)}", source[:i] + str(int(text) + delta) + source[i + len(text):]))
                elif text in ("true", "false"):
                    flipped = "false" if text == "true" else "true"
                    mutants.append((f"bool-{position(source, i)}", source[:i] + flipped + source[i + len(text):]))
                i += len(text)
                continue
            i += 1
    offset = 0
    for line in source.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.endswith(";") and not NON_EXPRESSION_STATEMENT.match(stripped):
            mutants.append((f"delete-{position(source, offset)}", source[:offset] + source[offset + len(line):]))
        offset += len(line)
    return mutants


def run_suite(target, source, tests_root, test_paths):
    with tempfile.TemporaryDirectory() as work:
        work = Path(work)
        for rel in test_paths:
            destination = work / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(tests_root / rel, destination)
        (work / target).parent.mkdir(parents=True, exist_ok=True)
        (work / target).write_text(source, encoding="utf-8")
        (work / "package.json").write_text('{"type": "module"}\n', encoding="utf-8")
        completed = subprocess.run(
            ["node", "--test", "--test-reporter=tap", *test_paths],
            cwd=work, capture_output=True, text=True, timeout=120,
        )
        return leaf_results(completed.stdout)


def mutate(reference, mutation):
    source = reference
    for edit in mutation.get("edits") or [mutation]:
        count = source.count(edit["find"])
        if count != 1:
            raise ValueError(f"find matched {count} times: {edit['find'][:60]}")
        source = source.replace(edit["find"], edit["replace"])
    return source


def killers(passing, results):
    return sorted(name for name in passing if not results.get(name, False))


def score(subject, tests_root, test_paths):
    config = json.loads((subject / "subject.json").read_text(encoding="utf-8"))
    target = config["target"]
    reference_names = config.get("references") or ["reference.js"]
    references = [(subject / name).read_text(encoding="utf-8") for name in reference_names]
    reference = references[0]
    mutants = json.loads((subject / "mutants.json").read_text(encoding="utf-8"))
    run = lambda source: run_suite(target, source, tests_root, test_paths)
    runs = [run(reference) for _ in range(REPEATS)]
    baseline = runs[0]
    per_reference = [baseline] + [run(source) for source in references[1:]]
    passing = {name for name in baseline if all(result.get(name, False) for result in per_reference)}
    stub_results = run((subject / "stub.js").read_text(encoding="utf-8"))
    report = {
        "tests": len(baseline),
        "tests_with_ac_id": sum(1 for name in baseline if AC_ID.search(name)),
        "reference_pass": len(passing),
        "reference_failures": sorted(name for name in baseline if name not in passing),
        "reference_failures_by_reference": {
            reference_name: sorted(name for name in baseline if not result.get(name, False))
            for reference_name, result in zip(reference_names, per_reference)
        },
        "reference_repeatable": all(result == baseline for result in runs),
        "stub_red": sum(1 for name in passing if not stub_results.get(name, False)),
        "mutants": {},
    }
    for mutant_id, mutation in mutants.items():
        report["mutants"][mutant_id] = {"requirement": mutation["requirement"], "killed_by": killers(passing, run(mutate(reference, mutation)))}
    report["killed"] = sum(1 for m in report["mutants"].values() if m["killed_by"])
    report["mutant_total"] = len(mutants)
    hidden_passing = {name for name, ok in run_suite(target, reference, subject, [HIDDEN_TEST]).items() if ok}
    killable, killed, survivors = 0, 0, []
    generated = auto_mutants(reference)
    for mutant_id, source in generated:
        if not killers(hidden_passing, run_suite(target, source, subject, [HIDDEN_TEST])):
            continue
        killable += 1
        if killers(passing, run(source)):
            killed += 1
        else:
            survivors.append(mutant_id)
    report["auto"] = {"generated": len(generated), "killable": killable, "killed": killed, "survivors": survivors}
    return report


def score_code(subject, source):
    target = json.loads((subject / "subject.json").read_text(encoding="utf-8"))["target"]
    results = run_suite(target, source, subject, [HIDDEN_TEST])
    return {"hidden_passed": sum(results.values()), "hidden_total": len(results), "hidden_failures": sorted(name for name, ok in results.items() if not ok)}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="mutant_score.py")
    parser.add_argument("subject", type=Path)
    parser.add_argument("tests_root", type=Path)
    parser.add_argument("test_paths", nargs="+")
    args = parser.parse_args(argv)
    print(json.dumps(score(args.subject, args.tests_root, args.test_paths), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
