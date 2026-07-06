#!/usr/bin/env python3
"""skill 構造の機械検証 (CI: validate-skills.yml / ローカル: python3 scripts/validate_skills.py)。

CLAUDE.md の「改名時のチェックリスト」「公開前チェック」の機械化。参照切れ・改名漏れ・
絶対パス混入は実行時 (Task 起動時の Read 失敗) まで顕在化しないため、PR 単位で検出する。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS = os.path.join(ROOT, "plugins")
errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def parse_frontmatter(path: str) -> dict:
    text = open(path, encoding="utf-8").read()
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not m:
        err(f"{path}: frontmatter が無い")
        return {}
    validate_frontmatter_yaml(path, m.group(1))
    fm = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z-]+):\s*(.*)$", line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip()
    return fm


def validate_frontmatter_yaml(path: str, block: str) -> None:
    """frontmatter を厳密な YAML として検証する。

    本スクリプトの行 regex パースは寛容だが、npx skills add (vercel-labs/skills) は
    厳密な YAML パーサで frontmatter を読む。unquoted 値に「: 」が混入すると
    そちらでだけ skill が発見不能になり、install/update が黙って失敗する
    (v1.14.0 の qa-ui description で実際に発生し、`mapping values are not
    allowed here` で弾かれていた)。
    """
    try:
        import yaml
    except ImportError:
        for line in block.splitlines():
            kv = re.match(r"^([A-Za-z-]+):\s*(.*)$", line)
            if kv and not kv.group(2).startswith(('"', "'")) and ": " in kv.group(2):
                err(f"{path}: frontmatter '{kv.group(1)}' の unquoted 値に ': ' を含む (YAML として不正)")
        return
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError as e:
        first = str(e).splitlines()[0] if str(e) else "parse error"
        err(f"{path}: frontmatter が YAML として不正 ({first})")
        return
    if not isinstance(data, dict):
        err(f"{path}: frontmatter が YAML mapping でない")


def check_skill_md(plugin: str, skill_dir: str, skill_md: str) -> None:
    fm = parse_frontmatter(skill_md)
    name = fm.get("name", "")
    if name != os.path.basename(skill_dir):
        err(f"{skill_md}: frontmatter name '{name}' がディレクトリ名と不一致")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name or ""):
        err(f"{skill_md}: name '{name}' が kebab-case でない")
    desc = fm.get("description", "")
    if not desc:
        err(f"{skill_md}: description が無い")
    elif len(desc) > 1024:
        err(f"{skill_md}: description が {len(desc)} 字 (agentskills spec 上限 1024)")


def check_md_links(plugin: str, skill_dir: str, md_path: str) -> None:
    text = open(md_path, encoding="utf-8").read()
    base = os.path.dirname(md_path)
    # 相対 markdown リンク (references/*.md, agents/*.md)
    for rel in re.findall(r"\]\(((?:references|agents)/[^)#]+)\)", text):
        if not os.path.exists(os.path.join(base, rel)):
            err(f"{md_path}: 参照先が存在しない: {rel}")
    # ${CLAUDE_PLUGIN_ROOT}/skills/... パス (プレースホルダ <...> 入りは対象外)
    for rel in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/((?:[\w.-]+/)*[\w.-]+\.md)", text):
        if not os.path.exists(os.path.join(PLUGINS, plugin, rel)):
            err(f"{md_path}: ${{CLAUDE_PLUGIN_ROOT}}/{rel} が存在しない")
    # 絶対パス混入 (マシン依存パスは配布物に書かない)
    for line_no, line in enumerate(text.splitlines(), 1):
        if re.search(r"(?<![\w@])(/home/|/Users/)", line):
            err(f"{md_path}:{line_no}: マシン依存の絶対パス混入: {line.strip()[:80]}")


def check_marketplace() -> None:
    mk_path = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
    mk = json.load(open(mk_path, encoding="utf-8"))
    listed = {p["name"]: p for p in mk["plugins"]}
    dirs = {d for d in os.listdir(PLUGINS) if os.path.isdir(os.path.join(PLUGINS, d))}
    for name in listed.keys() - dirs:
        err(f"marketplace.json: entry '{name}' に対応する plugins/ ディレクトリが無い")
    for name in dirs - listed.keys():
        err(f"marketplace.json: plugins/{name} が plugins 配列に列挙されていない")
    for name, entry in listed.items():
        if entry.get("source") != f"./plugins/{name}":
            err(f"marketplace.json: '{name}' の source が ./plugins/{name} でない")
        pj_path = os.path.join(PLUGINS, name, ".claude-plugin", "plugin.json")
        if not os.path.exists(pj_path):
            err(f"plugins/{name}: .claude-plugin/plugin.json が無い")
            continue
        pj = json.load(open(pj_path, encoding="utf-8"))
        if pj.get("name") != name:
            err(f"{pj_path}: name '{pj.get('name')}' がディレクトリ名と不一致")
        if pj.get("version") != entry.get("version"):
            err(
                f"version 不一致: plugins/{name}/plugin.json={pj.get('version')} "
                f"marketplace.json={entry.get('version')} (同 PR で揃えて bump する)"
            )


def main() -> int:
    check_marketplace()
    for plugin in sorted(os.listdir(PLUGINS)):
        pdir = os.path.join(PLUGINS, plugin)
        if not os.path.isdir(pdir):
            continue
        skills_dir = os.path.join(pdir, "skills")
        if os.path.isdir(skills_dir):
            for sk in sorted(os.listdir(skills_dir)):
                sdir = os.path.join(skills_dir, sk)
                skill_md = os.path.join(sdir, "SKILL.md")
                if not os.path.isfile(skill_md):
                    err(f"{sdir}: SKILL.md が無い")
                    continue
                check_skill_md(plugin, sdir, skill_md)
        # plugin 配下の全 md でリンク・絶対パスを検査
        for dirpath, _, files in os.walk(pdir):
            for f in files:
                if f.endswith(".md"):
                    check_md_links(plugin, pdir, os.path.join(dirpath, f))

    if errors:
        print(f"NG: {len(errors)} 件")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK: 全チェック通過 (frontmatter / 参照実在 / 絶対パス / marketplace 整合)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
