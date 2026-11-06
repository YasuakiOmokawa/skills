import argparse
import json
import re
import sys
from pathlib import Path


def tool_events(trace_path):
    uses, failed = [], set()
    for raw in trace_path.read_text(encoding="utf-8").splitlines():
        event = json.loads(raw)
        content = event.get("message", {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if block.get("type") == "tool_use":
                uses.append(block)
            elif block.get("type") == "tool_result" and block.get("is_error"):
                failed.add(block.get("tool_use_id"))
    return [use for use in uses if use["id"] not in failed]


def restore(trace_path, relpath):
    text, bash_writes = None, 0
    suffix = "/" + relpath
    for use in tool_events(trace_path):
        name, data = use["name"], use.get("input", {})
        if name == "Bash" and relpath in data.get("command", "") and re.search(r">|tee |sed -i|cp |mv ", data["command"]):
            bash_writes += 1
            continue
        if not str(data.get("file_path", "")).endswith(suffix):
            continue
        if name == "Write":
            text = data["content"]
        elif name == "Edit" and text is not None:
            old, new = data["old_string"], data["new_string"]
            text = text.replace(old, new) if data.get("replace_all") else text.replace(old, new, 1)
    return text, bash_writes


def main(argv=None):
    parser = argparse.ArgumentParser(prog="restore_file.py")
    parser.add_argument("trace", type=Path)
    parser.add_argument("relpath")
    parser.add_argument("out_root", type=Path)
    args = parser.parse_args(argv)
    text, bash_writes = restore(args.trace, args.relpath)
    print(json.dumps({"restored": text is not None, "bash_writes": bash_writes}))
    if text is None:
        return 1
    target = args.out_root / args.relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
