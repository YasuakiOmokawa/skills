import pathlib
import shutil
import subprocess
import sys

source_plugin, skill_source, out_dir = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
removals = sys.argv[4:]
if out_dir.exists():
    shutil.rmtree(out_dir)
subprocess.run(
    ["rsync", "-a", "--exclude", "evals/results", source_plugin.rstrip("/") + "/", f"{out_dir}/"],
    check=True,
)
text = pathlib.Path(skill_source).read_text()
for removal in removals:
    assert text.count(removal) == 1, f"not unique ({text.count(removal)}): {removal[:60]}"
    text = text.replace(removal, "")
skills = list((out_dir / "skills").iterdir())
assert len(skills) == 1
(skills[0] / "SKILL.md").write_text(text)
print(out_dir, len(text.split("---", 2)[2].strip()))
