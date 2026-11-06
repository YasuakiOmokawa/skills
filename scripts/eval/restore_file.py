import argparse
import json
import re
import sys
from pathlib import Path


def tool_events(trace_path):
    uses, failed = [], set()
    for raw in trace_path.read_text(encoding="utf-8").splitlines():
        event = json.loads(raw)
        message = event.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, list):
            continue
        for block in content:
            if block.get("type") == "tool_use":
                uses.append(block)
            elif block.get("type") == "tool_result" and block.get("is_error"):
                failed.add(block.get("tool_use_id"))
    return [use for use in uses if use["id"] not in failed]


def cat_output(trace_path, relpath):
    command = re.compile(r"^(?:\s*cd\s+\S+\s*&&)?\s*cat\s+\S*" + re.escape(relpath) + r"\s*$")
    commands, output = {}, None
    for raw in trace_path.read_text(encoding="utf-8").splitlines():
        event = json.loads(raw)
        message = event.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, list):
            continue
        for block in content:
            if block.get("type") == "tool_use" and block.get("name") == "Bash" and command.match(block.get("input", {}).get("command", "")):
                commands[block["id"]] = True
            elif block.get("type") == "tool_result" and block.get("tool_use_id") in commands and not block.get("is_error"):
                body = block.get("content")
                output = body if isinstance(body, str) else "".join(part.get("text", "") for part in body or [])
    return output


def writes_to(command, relpath):
    target = r"[\"']?[^\s\"';|&]*" + re.escape(relpath)
    patterns = (rf"(?<![0-9&])>>?\s*{target}", rf"\btee(?:\s+-a)?\s+{target}", rf"\bsed\s+-i[^;|&]*{target}", rf"\b(?:cp|mv)\s+(?:-\w+\s+)*\S+\s+{target}")
    return any(re.search(pattern, command) for pattern in patterns)


def restore(trace_path, relpath, base=None):
    text, bash_writes, fixture_seen = base, 0, base is None
    suffix = "/" + relpath
    for use in tool_events(trace_path):
        name, data = use["name"], use.get("input", {})
        if name == "Bash" and not fixture_seen:
            fixture_seen = True
            continue
        if name == "Bash" and writes_to(data.get("command", ""), relpath):
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
