import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

SEAL_TRAILER = "Define-Done-Seal"
COMMAND_TRAILER = "Define-Done-Test-Command"


def git(repo, *args):
    completed = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout


def trailers(repo, sha):
    body = git(repo, "show", "-s", "--format=%B", sha)
    parsed = git_stdin(repo, body, "interpret-trailers", "--parse")
    values = {}
    for line in parsed.splitlines():
        key, _, value = line.partition(":")
        values[key.strip()] = value.strip()
    return values


def git_stdin(repo, text, *args):
    completed = subprocess.run(["git", "-C", str(repo), *args], input=text, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip())
    return completed.stdout


def seals(repo):
    out = git(repo, "log", "-E", f"--grep=^{SEAL_TRAILER}: ", "--format=%H", "HEAD")
    return [sha for sha in out.split() if SEAL_TRAILER in trailers(repo, sha)]


def files_in(repo, sha):
    return [path for path in git(repo, "show", "--name-only", "--format=", sha).splitlines() if path]


def inspect(repo):
    found = seals(repo)
    if not found:
        return None, ["seal: `Define-Done-Seal:` の trailer を持つ commit が HEAD から辿れない"]
    latest, oldest = found[0], found[-1]
    values = trailers(repo, latest)
    findings = []
    if not values.get(COMMAND_TRAILER):
        findings.append(f"seal: {latest[:12]} に `{COMMAND_TRAILER}:` の trailer が無い")
    protected = sorted({path for sha in found for path in files_in(repo, sha)})
    seal_set = set(found)
    for sha in git(repo, "log", "--format=%H", f"{oldest}..HEAD", "--", *protected).split():
        if sha not in seal_set:
            touched = sorted(set(files_in(repo, sha)) & set(protected))
            findings.append(f"tamper: {sha[:12]} が封の後に {', '.join(touched)} を変えた")
    dirty = git(repo, "status", "--porcelain", "--", *protected).splitlines()
    if dirty:
        findings.append(f"tamper: 封をしたファイルに未 commit の変更がある ({'; '.join(line.strip() for line in dirty)})")
    info = {
        "seal": latest,
        "acs": values.get(SEAL_TRAILER, ""),
        "test-command": values.get(COMMAND_TRAILER, ""),
        "protected": ", ".join(protected),
        "seals": ", ".join(sha[:12] for sha in found),
    }
    return info, findings


def run_at_seal(repo, info, command):
    with tempfile.TemporaryDirectory() as work:
        archive = subprocess.run(["git", "-C", str(repo), "archive", info["seal"]], capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", work], input=archive.stdout, check=True)
        modules = Path(repo) / "node_modules"
        if modules.is_dir():
            (Path(work) / "node_modules").symlink_to(modules.resolve())
        completed = subprocess.run(command, shell=True, cwd=work, capture_output=True, text=True, timeout=600)
        return completed.returncode, completed.stdout + completed.stderr


def main(argv=None):
    parser = argparse.ArgumentParser(prog="check_seal.py")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check").add_argument("repo", type=Path)
    at_seal = sub.add_parser("at-seal")
    at_seal.add_argument("repo", type=Path)
    at_seal.add_argument("cmd", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    try:
        info, findings = inspect(args.repo)
    except RuntimeError as exc:
        print(f"git: {exc}")
        return 1
    if info:
        for key, value in info.items():
            print(f"{key}: {value}")
    for finding in findings:
        print(finding)
    if findings:
        return 1
    if args.command == "at-seal":
        command = " ".join(part for part in args.cmd if part != "--") or info["test-command"]
        code, output = run_at_seal(args.repo, info, command)
        print(f"at-seal-command: {command}")
        print(f"at-seal-exit: {code}")
        print(output[-4000:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
