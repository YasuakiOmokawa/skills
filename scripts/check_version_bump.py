from __future__ import annotations

import json
import subprocess
import sys

_SHIPPED_DIRECTORIES = ("skills", "commands")


def _parse(version: str) -> tuple[int, int, int]:
    major, minor, patch = (int(part) for part in version.split("."))
    return major, minor, patch


def _is_minor_or_major_bump(base: str, head: str) -> bool:
    base_version, head_version = _parse(base), _parse(head)
    return head_version > base_version and head_version[2] == 0


def plugins_with_shipped_changes(changed_paths: list[str]) -> set[str]:
    plugins = set()
    for path in changed_paths:
        parts = path.split("/")
        if len(parts) > 3 and parts[0] == "plugins" and parts[2] in _SHIPPED_DIRECTORIES:
            plugins.add(parts[1])
    return plugins


def bump_errors(
    changed_paths: list[str],
    base_marketplace: dict,
    head_marketplace: dict,
    base_plugin_versions: dict[str, str],
    head_plugin_versions: dict[str, str],
) -> list[str]:
    errors = []
    changed_plugins = plugins_with_shipped_changes(changed_paths)
    for plugin in sorted(changed_plugins):
        base = base_plugin_versions.get(plugin)
        head = head_plugin_versions.get(plugin)
        if head is None or base is None:
            continue
        if not _is_minor_or_major_bump(base, head):
            errors.append(
                f"plugins/{plugin}: shipped content changed, so plugin.json version must take a minor (or major) bump from {base}; found {head}"
            )
    if changed_plugins and not _is_minor_or_major_bump(
        base_marketplace["version"], head_marketplace["version"]
    ):
        errors.append(
            f".claude-plugin/marketplace.json: top-level version must take a minor (or major) bump from {base_marketplace['version']}; found {head_marketplace['version']}"
        )
    return errors


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, text=True, capture_output=True).stdout


def _plugin_versions(marketplace: dict) -> dict[str, str]:
    return {entry["name"]: entry["version"] for entry in marketplace.get("plugins", [])}


def main() -> int:
    base_ref = sys.argv[1]
    merge_base = _git("merge-base", base_ref, "HEAD").strip()
    changed_paths = _git("diff", "--name-only", merge_base, "HEAD").splitlines()
    base_marketplace = json.loads(_git("show", f"{merge_base}:.claude-plugin/marketplace.json"))
    with open(".claude-plugin/marketplace.json", encoding="utf-8") as handle:
        head_marketplace = json.load(handle)
    errors = bump_errors(
        changed_paths,
        base_marketplace,
        head_marketplace,
        _plugin_versions(base_marketplace),
        _plugin_versions(head_marketplace),
    )
    for error in errors:
        print(error, file=sys.stderr)
    if not errors:
        print("OK: version bumps match shipped plugin changes")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
