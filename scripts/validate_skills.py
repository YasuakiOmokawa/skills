"""Validate the deliberately small skill repository format used by this project."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


_NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_HEADING_RE = re.compile(
    r"^[ \t]{0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$", re.MULTILINE
)
_INLINE_LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
_REFERENCE_LINK_RE = re.compile(
    r"^[ \t]{0,3}\[[^\]\n]+\]:[ \t]*(?:<([^>\n]+)>|(\S+))",
    re.MULTILINE,
)
_WEB_URL_RE = re.compile(r"\b(?:https?|ftp)://[^\s<>]+", re.IGNORECASE)
_WINDOWS_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/][^\s`\"'<>]+")
_HOME_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:~|\$HOME|\$\{HOME\})[/\\][^\s`\"'<>]+"
)
_UNIX_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_:/])/(?!/)[A-Za-z0-9_~$%+={}-][^\s`\"'<>)]*"
)
_LONG_OPTION_RE = re.compile(r"(?<![A-Za-z0-9_-])--[A-Za-z0-9][A-Za-z0-9-]*")
_POSITIONAL_ARGUMENT_RE = re.compile(r"(?<!\$)\$[0-9](?![0-9])")
_SKILLS_CONFIG_PREFIXES = (
    "~/.claude/skills-config/",
    "$HOME/.claude/skills-config/",
    "${HOME}/.claude/skills-config/",
)
_OUTCOME_SECTIONS = ["Trigger", "Outcome", "Authorization", "Hold-out"]


class _ErrorCollector:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._records: list[tuple[str, int, str]] = []
        self._seen: set[str] = set()

    def add(self, path: Path, message: str) -> None:
        try:
            label = path.relative_to(self.root).as_posix()
        except ValueError:
            label = path.as_posix()
        label = label or "."
        rendered = f"{label}: {message}"
        if rendered in self._seen:
            return
        self._seen.add(rendered)
        self._records.append((label, len(self._records), rendered))

    def render(self) -> list[str]:
        return [record[2] for record in sorted(self._records, key=lambda item: (item[0], item[1]))]


def _load_json(path: Path, errors: _ErrorCollector, kind: str) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.add(path, f"missing {kind}")
        return None
    except (OSError, UnicodeError) as exc:
        errors.add(path, f"cannot read {kind}: {exc}")
        return None

    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        errors.add(path, f"malformed {kind} JSON at line {exc.lineno}, column {exc.colno}")
        return None
    if not isinstance(value, dict):
        errors.add(path, f"{kind} must contain a JSON object")
        return None
    return value


def _marketplace_entries(
    root: Path, errors: _ErrorCollector
) -> tuple[Path, dict[str, dict]]:
    path = root / ".claude-plugin" / "marketplace.json"
    marketplace = _load_json(path, errors, "marketplace.json")
    if marketplace is None:
        return path, {}

    raw_entries = marketplace.get("plugins")
    if not isinstance(raw_entries, list):
        errors.add(path, "marketplace 'plugins' must be an array")
        return path, {}

    entries: dict[str, dict] = {}
    for index, entry in enumerate(raw_entries):
        if not isinstance(entry, dict):
            errors.add(path, f"marketplace plugin entry {index} must be an object")
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            errors.add(path, f"marketplace plugin entry {index} has an invalid name")
            continue
        if name in entries:
            errors.add(path, f"marketplace contains duplicate plugin entry '{name}'")
            continue
        entries[name] = entry

        if len(name) > 64 or _NAME_RE.fullmatch(name) is None:
            errors.add(path, f"marketplace plugin '{name}' has an invalid name")

        expected_source = f"./plugins/{name}"
        if entry.get("source") != expected_source:
            errors.add(
                path,
                f"marketplace plugin '{name}' source must be '{expected_source}'",
            )
        if not isinstance(entry.get("version"), str) or not entry["version"]:
            errors.add(path, f"marketplace plugin '{name}' has an invalid version")

    return path, entries


def _plugin_directories(root: Path, errors: _ErrorCollector) -> dict[str, Path]:
    plugins_root = root / "plugins"
    if not plugins_root.is_dir():
        errors.add(plugins_root, "missing plugins directory")
        return {}

    directories: dict[str, Path] = {}
    try:
        children = sorted(plugins_root.iterdir(), key=lambda path: path.name)
    except OSError as exc:
        errors.add(plugins_root, f"cannot inspect plugins directory: {exc}")
        return {}

    for child in children:
        if child.is_dir():
            directories[child.name] = child
        else:
            errors.add(child, "plugins must be represented by directories")
    return directories


def _validate_manifest(
    plugin_name: str,
    plugin_root: Path,
    marketplace_entry: dict | None,
    errors: _ErrorCollector,
) -> None:
    path = plugin_root / ".claude-plugin" / "plugin.json"
    manifest = _load_json(path, errors, "plugin.json")
    if manifest is None:
        return

    declared_name = manifest.get("name")
    if declared_name != plugin_name:
        errors.add(
            path,
            f"plugin.json name {declared_name!r} must match plugin directory and marketplace name '{plugin_name}'",
        )

    for field in ("skills", "commands", "agents"):
        if field in manifest:
            errors.add(path, f"plugin.json must not declare the '{field}' discovery array")

    version = manifest.get("version")
    if not isinstance(version, str) or not version:
        errors.add(path, "plugin.json has an invalid version")
    if marketplace_entry is not None:
        marketplace_version = marketplace_entry.get("version")
        if version != marketplace_version:
            errors.add(
                path,
                f"plugin.json version {version!r} does not match marketplace version {marketplace_version!r}",
            )


def _parse_scalar(value: str) -> tuple[str | None, str | None]:
    if not value:
        return "", None

    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None, "malformed double-quoted scalar"
        if not isinstance(parsed, str):
            return None, "frontmatter values must be strings"
        return parsed, None

    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            return None, "malformed single-quoted scalar"
        inner = value[1:-1]
        without_escaped_quotes = inner.replace("''", "")
        if "'" in without_escaped_quotes:
            return None, "malformed single-quoted scalar"
        return inner.replace("''", "'"), None

    if value[0] in "[{|>!&*" or value.startswith(("- ", "? ")):
        return None, "unsupported non-scalar frontmatter value"
    return value, None


def _parse_frontmatter(
    path: Path, errors: _ErrorCollector
) -> tuple[dict[str, str], str] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.add(path, f"cannot read SKILL.md: {exc}")
        return None

    lines = text.splitlines()
    if not lines or lines[0] != "---":
        errors.add(path, "frontmatter must start with an exact '---' delimiter")
        return {}, text

    closing_index = next(
        (index for index, line in enumerate(lines[1:], start=1) if line == "---"),
        None,
    )
    if closing_index is None:
        errors.add(path, "frontmatter is missing its closing '---' delimiter")
        return {}, ""

    metadata: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:closing_index], start=2):
        if not line.strip():
            continue
        if line[:1].isspace() or line.lstrip().startswith("#"):
            errors.add(path, f"unsupported frontmatter syntax on line {line_number}")
            continue
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*):[ \t]*(.*)", line)
        if match is None:
            errors.add(path, f"malformed frontmatter on line {line_number}")
            continue
        key, raw_value = match.groups()
        if key in metadata:
            errors.add(path, f"frontmatter contains duplicate key '{key}'")
            continue
        value, scalar_error = _parse_scalar(raw_value.strip())
        if scalar_error is not None:
            errors.add(path, f"{scalar_error} for frontmatter key '{key}' on line {line_number}")
            continue
        assert value is not None
        metadata[key] = value

    allowed_keys = {"name", "description"}
    for key in sorted(set(metadata) - allowed_keys):
        errors.add(path, f"frontmatter contains unsupported key '{key}'")
    for key in sorted(allowed_keys - set(metadata)):
        errors.add(path, f"frontmatter is missing required key '{key}'")

    body = "\n".join(lines[closing_index + 1 :])
    return metadata, body


def _link_destinations(markdown: str) -> list[str]:
    destinations: list[str] = []
    for match in _INLINE_LINK_RE.finditer(markdown):
        payload = match.group(1).strip()
        if payload.startswith("<") and ">" in payload:
            destination = payload[1 : payload.index(">")]
        else:
            destination = payload.split(None, 1)[0] if payload else ""
        if destination:
            destinations.append(destination)
    for match in _REFERENCE_LINK_RE.finditer(markdown):
        destination = match.group(1) or match.group(2)
        if destination:
            destinations.append(destination)
    return destinations


def _local_link_target(
    destination: str, source: Path, skill_root: Path
) -> tuple[str, Path | None, str]:
    raw = destination.strip().replace("\\ ", " ")
    decoded = unquote(raw)
    if _WINDOWS_PATH_RE.match(decoded) or decoded.startswith(("/", "~/", "~\\")):
        return "absolute", None, decoded
    if decoded.startswith("//"):
        return "external", None, decoded

    split = urlsplit(decoded)
    if split.scheme:
        return "external", None, decoded
    if not split.path:
        return "anchor", None, decoded

    candidate = (source.parent / split.path).resolve()
    resolved_skill_root = skill_root.resolve()
    try:
        candidate.relative_to(resolved_skill_root)
    except ValueError:
        return "outside", candidate, decoded
    return "local", candidate, decoded


def _validate_links(
    source: Path,
    markdown: str,
    skill_root: Path,
    errors: _ErrorCollector,
    *,
    nested_references_forbidden: bool,
) -> set[Path]:
    markdown_targets: set[Path] = set()
    for destination in _link_destinations(markdown):
        kind, target, decoded = _local_link_target(destination, source, skill_root)
        if kind == "absolute":
            errors.add(source, f"Markdown link uses a forbidden absolute path '{decoded}'")
            continue
        if kind == "outside":
            errors.add(source, f"Markdown link target '{decoded}' escapes the skill directory")
            continue
        if kind != "local" or target is None:
            continue

        is_markdown = target.suffix.lower() in {".md", ".markdown"}
        if is_markdown:
            markdown_targets.add(target)
            if nested_references_forbidden:
                errors.add(
                    source,
                    f"nested Markdown reference '{decoded}' is not allowed; link it directly from SKILL.md",
                )
        if not target.is_file():
            errors.add(source, f"Markdown link target does not exist: {decoded}")
    return markdown_targets


def _headings(markdown: str) -> list[tuple[int, str]]:
    return [
        (len(match.group(1)), match.group(2).strip())
        for match in _HEADING_RE.finditer(markdown)
    ]


def _absolute_paths(markdown: str, known_skills: set[str]) -> list[str]:
    without_urls = _WEB_URL_RE.sub("", markdown)
    matches: list[str] = []
    for pattern in (_WINDOWS_PATH_RE, _HOME_PATH_RE, _UNIX_PATH_RE):
        for match in pattern.finditer(without_urls):
            value = match.group(0).rstrip(".,;:!?")
            if value.startswith("/") and "/" not in value[1:] and value[1:] in known_skills:
                continue
            if any(value.startswith(prefix) for prefix in _SKILLS_CONFIG_PREFIXES):
                prefix = next(
                    prefix
                    for prefix in _SKILLS_CONFIG_PREFIXES
                    if value.startswith(prefix)
                )
                suffix = value[len(prefix) :]
                if (
                    suffix
                    and all(part not in {"", ".", ".."} for part in suffix.split("/"))
                    and re.fullmatch(r"[A-Za-z0-9._/-]+", suffix)
                ):
                    continue
            if value and value not in matches:
                matches.append(value)
    if "file://" in without_urls.lower() and "file://" not in matches:
        matches.append("file://")
    return matches


def _validate_instruction_surfaces(
    path: Path,
    markdown: str,
    skill_name: str,
    known_skills: set[str],
    errors: _ErrorCollector,
) -> None:
    for absolute_path in _absolute_paths(markdown, known_skills):
        errors.add(path, f"contains forbidden absolute path '{absolute_path}'")

    if "$ARGUMENTS" in markdown:
        errors.add(path, "argument surface '$ARGUMENTS' is not allowed")
    if "${ARGUMENTS}" in markdown:
        errors.add(path, "argument surface '${ARGUMENTS}' is not allowed")
    for match in _POSITIONAL_ARGUMENT_RE.finditer(markdown):
        errors.add(path, f"positional argument surface '{match.group(0)}' is not allowed")
    for option in dict.fromkeys(_LONG_OPTION_RE.findall(markdown)):
        errors.add(path, f"skill-specific long option '{option}' is not allowed")

    argument_headings = {
        "argument",
        "arguments",
        "parameter",
        "parameters",
        "option",
        "options",
        "input",
        "inputs",
        "引数",
        "オプション",
        "パラメータ",
    }
    for level, heading in _headings(markdown):
        if level == 1:
            continue
        normalized = heading.strip("`*_ ").casefold()
        normalized_words = set(re.findall(r"[a-z]+", normalized))
        if normalized in argument_headings or normalized_words.intersection(
            argument_headings
        ) or any(word in normalized for word in ("引数", "オプション", "パラメータ")):
            errors.add(path, f"argument heading '{heading}' is not allowed")
        if re.search(r"\b(?:tier|tiers|mode|modes)\b", normalized) or any(
            word in normalized for word in ("ティア", "モード")
        ):
            errors.add(path, f"named tier/mode heading '{heading}' is not allowed")

    if skill_name != "apply-findings" and re.search(
        r"(?<![A-Za-z0-9])review-only(?![A-Za-z0-9])", markdown, re.IGNORECASE
    ):
        errors.add(path, "review-only is reserved for the apply-findings skill")

    for other_skill in sorted(known_skills - {skill_name}):
        invocation = re.compile(
            rf"(?<![A-Za-z0-9_])([/$]){re.escape(other_skill)}(?![A-Za-z0-9-])"
        )
        for match in invocation.finditer(markdown):
            errors.add(
                path,
                f"invocation '{match.group(0)}' calls another skill '{other_skill}'",
            )


def _validate_skill_file(
    path: Path,
    plugin_name: str,
    known_skills: set[str],
    errors: _ErrorCollector,
) -> None:
    parsed = _parse_frontmatter(path, errors)
    if parsed is None:
        return
    metadata, body = parsed
    skill_root = path.parent

    name = metadata.get("name")
    if name is not None:
        if len(name) > 64 or _NAME_RE.fullmatch(name) is None:
            errors.add(
                path,
                "frontmatter name is invalid; use at most 64 lowercase letters, digits, and single hyphens",
            )
        if name != skill_root.name:
            errors.add(
                path,
                f"frontmatter name '{name}' must match its parent skill directory '{skill_root.name}'",
            )
        if name != plugin_name:
            errors.add(
                path,
                f"frontmatter name '{name}' must match parent plugin name '{plugin_name}'",
            )

    description = metadata.get("description")
    if description is not None and (not description.strip() or len(description) > 1024):
        errors.add(path, "frontmatter description must be nonempty and at most 1024 characters")

    _validate_instruction_surfaces(path, body, plugin_name, known_skills, errors)
    direct_markdown = _validate_links(
        path,
        body,
        skill_root,
        errors,
        nested_references_forbidden=False,
    )

    markdown_files: list[Path] = []
    try:
        markdown_files = sorted(
            (
                candidate
                for candidate in skill_root.rglob("*")
                if candidate.is_file()
                and candidate != path
                and candidate.suffix.lower() in {".md", ".markdown"}
            ),
            key=lambda candidate: candidate.as_posix(),
        )
    except OSError as exc:
        errors.add(skill_root, f"cannot inspect Markdown references: {exc}")

    resolved_direct = {candidate.resolve() for candidate in direct_markdown}
    for markdown_path in markdown_files:
        if markdown_path.resolve() not in resolved_direct:
            errors.add(
                markdown_path,
                "orphan Markdown reference; every Markdown file must be linked directly from SKILL.md",
            )

    for reference in sorted(resolved_direct, key=lambda candidate: candidate.as_posix()):
        if not reference.is_file():
            continue
        try:
            reference_text = reference.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.add(reference, f"cannot read directly linked Markdown reference: {exc}")
            continue
        _validate_instruction_surfaces(
            reference, reference_text, plugin_name, known_skills, errors
        )
        _validate_links(
            reference,
            reference_text,
            skill_root,
            errors,
            nested_references_forbidden=True,
        )


def _validate_skill_layout(
    plugin_name: str,
    plugin_root: Path,
    known_skills: set[str],
    errors: _ErrorCollector,
) -> None:
    skills_root = plugin_root / "skills"
    expected_root = skills_root / plugin_name
    expected_skill = expected_root / "SKILL.md"

    if not skills_root.is_dir():
        errors.add(skills_root, f"missing skills directory for plugin '{plugin_name}'")
        return

    try:
        direct_children = sorted(skills_root.iterdir(), key=lambda path: path.name)
    except OSError as exc:
        errors.add(skills_root, f"cannot inspect skills directory: {exc}")
        return

    for child in direct_children:
        if not child.is_dir():
            errors.add(child, "unexpected file; skills must use plugins/<plugin>/skills/<plugin>/SKILL.md")
        elif child.name != plugin_name:
            errors.add(
                child,
                f"skill directory name '{child.name}' must match parent plugin name '{plugin_name}'",
            )

    if not expected_skill.is_file():
        errors.add(expected_skill, "missing SKILL.md at the exact required skill layout")

    try:
        candidates = sorted(plugin_root.rglob("SKILL.md"), key=lambda path: path.as_posix())
    except OSError as exc:
        errors.add(plugin_root, f"cannot inspect skill layout: {exc}")
        return

    for candidate in candidates:
        if candidate != expected_skill:
            errors.add(
                candidate,
                f"SKILL.md must be located at plugins/{plugin_name}/skills/{plugin_name}/SKILL.md",
            )
        _validate_skill_file(candidate, plugin_name, known_skills, errors)


def _validate_agent_markdown(plugin_root: Path, errors: _ErrorCollector) -> None:
    try:
        candidates = sorted(plugin_root.rglob("*"), key=lambda path: path.as_posix())
    except OSError as exc:
        errors.add(plugin_root, f"cannot inspect plugin files: {exc}")
        return
    for candidate in candidates:
        if not candidate.is_file() or candidate.suffix.lower() not in {".md", ".markdown"}:
            continue
        relative_parts = [part.casefold() for part in candidate.relative_to(plugin_root).parts]
        if "agents" in relative_parts:
            errors.add(candidate, "agents Markdown files are not allowed")


def _validate_outcomes(plugin_root: Path, errors: _ErrorCollector) -> None:
    path = plugin_root / "evals" / "outcomes.md"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.add(path, "missing outcomes.md")
        return
    except (OSError, UnicodeError) as exc:
        errors.add(path, f"cannot read outcomes.md: {exc}")
        return

    sections = [heading for level, heading in _headings(text) if level == 1]
    if sections != _OUTCOME_SECTIONS:
        errors.add(
            path,
            f"top-level sections must be exactly {_OUTCOME_SECTIONS!r} in order",
        )


def validate_repository(root: Path) -> list[str]:
    """Return every validation error for *root* in stable relative-path order."""

    root = Path(root).resolve()
    errors = _ErrorCollector(root)
    if not root.is_dir():
        errors.add(root, "repository root is not a directory")
        return errors.render()

    marketplace_path, marketplace = _marketplace_entries(root, errors)
    plugin_directories = _plugin_directories(root, errors)

    directory_names = set(plugin_directories)
    marketplace_names = set(marketplace)
    for name in sorted(directory_names - marketplace_names):
        errors.add(
            marketplace_path,
            f"plugin directory '{name}' is missing a corresponding marketplace entry",
        )
    for name in sorted(marketplace_names - directory_names):
        errors.add(
            marketplace_path,
            f"marketplace plugin '{name}' has no corresponding plugin directory",
        )

    known_skills = directory_names | marketplace_names
    for plugin_name, plugin_root in sorted(plugin_directories.items()):
        if len(plugin_name) > 64 or _NAME_RE.fullmatch(plugin_name) is None:
            errors.add(plugin_root, f"invalid plugin and skill name '{plugin_name}'")
        _validate_manifest(
            plugin_name,
            plugin_root,
            marketplace.get(plugin_name),
            errors,
        )
        _validate_skill_layout(plugin_name, plugin_root, known_skills, errors)
        _validate_agent_markdown(plugin_root, errors)
        _validate_outcomes(plugin_root, errors)

    return errors.render()


def main() -> int:
    errors = validate_repository(Path.cwd())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("OK: skills repository is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
