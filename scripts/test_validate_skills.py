import json
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from scripts.validate_skills import validate_repository


class ValidateSkillsTest(unittest.TestCase):
    @staticmethod
    def _write(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _write_plugin(
        self,
        root,
        *,
        plugin_name,
        skill_directory=None,
        declared_name=None,
        description="A disposable test skill.",
        body=None,
        extra_frontmatter=None,
        files=None,
        plugin_version="1.0.0",
        marketplace_version=None,
        manifest_overrides=None,
    ):
        skill_directory = skill_directory or plugin_name
        declared_name = declared_name or plugin_name
        marketplace_version = marketplace_version or plugin_version

        plugin_root = root / "plugins" / plugin_name
        skill_root = plugin_root / "skills" / skill_directory

        manifest = {
            "name": plugin_name,
            "description": f"Plugin containing {plugin_name}.",
            "version": plugin_version,
        }
        manifest.update(manifest_overrides or {})
        self._write(
            plugin_root / ".claude-plugin" / "plugin.json",
            json.dumps(manifest, indent=2) + "\n",
        )

        frontmatter = [
            f"name: {declared_name}",
            f"description: {description}",
        ]
        for key, value in (extra_frontmatter or {}).items():
            frontmatter.append(f"{key}: {value}")

        if body is None:
            body = f"# {declared_name}\n\nFollow the documented workflow.\n"
        skill_markdown = "---\n" + "\n".join(frontmatter) + "\n---\n\n" + body
        self._write(skill_root / "SKILL.md", skill_markdown)
        self._write(
            plugin_root / "evals" / "outcomes.md",
            (
                "# Trigger\n\n- fixture: trigger\n\n"
                "# Outcome\n\n- fixture: outcome\n\n"
                "# Authorization\n\n- fixture: authorization\n\n"
                "# Hold-out\n\n- fixture: hold-out\n"
            ),
        )

        for relative_path, content in (files or {}).items():
            self._write(skill_root / relative_path, content)

        return {
            "name": plugin_name,
            "source": f"./plugins/{plugin_name}",
            "description": f"Marketplace entry for {plugin_name}.",
            "version": marketplace_version,
        }

    @contextmanager
    def repository(self, additional_plugins=None, **primary_overrides):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            primary = {"plugin_name": "sample-skill"}
            primary.update(primary_overrides)

            entries = [self._write_plugin(root, **primary)]
            for plugin in additional_plugins or []:
                entries.append(self._write_plugin(root, **plugin))

            marketplace = {
                "name": "disposable-test-marketplace",
                "owner": {"name": "validator-tests"},
                "plugins": entries,
            }
            self._write(
                root / ".claude-plugin" / "marketplace.json",
                json.dumps(marketplace, indent=2) + "\n",
            )
            yield root

    def assert_valid(self, root):
        self.assertEqual([], validate_repository(root))

    def assert_invalid(self, root, *expected_substrings):
        errors = validate_repository(root)
        self.assertTrue(errors, "expected repository validation to fail")
        rendered_errors = "\n".join(errors).lower()
        for substring in expected_substrings:
            self.assertIn(substring.lower(), rendered_errors)

    def test_complete_minimal_repository_passes(self):
        with self.repository() as root:
            self.assert_valid(root)

    def test_extra_frontmatter_is_rejected(self):
        with self.repository(extra_frontmatter={"license": "MIT"}) as root:
            self.assert_invalid(root, "frontmatter", "license")

    def test_description_must_be_nonempty_and_at_most_1024_characters(self):
        for label, description in [
            ("empty", ""),
            ("too long", "x" * 1025),
        ]:
            with self.subTest(label=label):
                with self.repository(description=description) as root:
                    self.assert_invalid(root, "description")

    def test_invalid_name_and_directory_mismatch_are_rejected(self):
        cases = [
            (
                "consecutive hyphens",
                {"plugin_name": "bad--name"},
                ("invalid", "name"),
            ),
            (
                "name differs from parent directory",
                {
                    "plugin_name": "sample-skill",
                    "skill_directory": "different-skill",
                    "declared_name": "sample-skill",
                },
                ("parent", "name"),
            ),
        ]
        for label, overrides, expected in cases:
            with self.subTest(label=label):
                with self.repository(**overrides) as root:
                    self.assert_invalid(root, *expected)

    def test_missing_markdown_link_target_is_rejected(self):
        body = "# sample-skill\n\nSee [the missing guide](references/missing.md).\n"
        with self.repository(body=body) as root:
            self.assert_invalid(root, "references/missing.md")

    def test_machine_dependent_absolute_paths_are_rejected_but_https_is_allowed(self):
        invalid_cases = [
            (
                "Unix home path in SKILL.md",
                {
                    "body": (
                        "# sample-skill\n\n"
                        "Read configuration from /home/alice/work/config.yml.\n"
                    )
                },
            ),
            (
                "Windows drive path in SKILL.md",
                {
                    "body": (
                        "# sample-skill\n\n"
                        "Read configuration from C:\\Users\\Alice\\work\\config.yml.\n"
                    )
                },
            ),
            (
                "absolute path in a directly referenced Markdown file",
                {
                    "body": "# sample-skill\n\nSee [the guide](references/guide.md).\n",
                    "files": {
                        "references/guide.md": (
                            "# Guide\n\nUse /Users/alice/work/config.yml.\n"
                        )
                    },
                },
            ),
            (
                "non-skill home configuration",
                {
                    "body": (
                        "# sample-skill\n\n"
                        "Read configuration from ~/.claude/config.toml.\n"
                    )
                },
            ),
            (
                "skill configuration traversal",
                {
                    "body": (
                        "# sample-skill\n\n"
                        "Read configuration from ~/.claude/skills-config/../secrets.md.\n"
                    )
                },
            ),
        ]
        for label, overrides in invalid_cases:
            with self.subTest(label=label):
                with self.repository(**overrides) as root:
                    self.assert_invalid(root, "absolute path")

        allowed_body = (
            "# sample-skill\n\n"
            "Read ~/.claude/skills-config/jira.md when it exists.\n"
            "See [the hosted guide](https://example.com/docs/root/path) and "
            "https://example.com/another/path.\n"
        )
        with self.repository(body=allowed_body) as root:
            self.assert_valid(root)

    def test_plugin_and_marketplace_version_mismatch_is_rejected(self):
        with self.repository(
            plugin_version="1.2.3", marketplace_version="1.2.4"
        ) as root:
            self.assert_invalid(root, "version")

    def test_outcome_contract_is_required_with_exact_top_level_sections(self):
        with self.repository() as root:
            (root / "plugins" / "sample-skill" / "evals" / "outcomes.md").unlink()
            self.assert_invalid(root, "outcomes.md", "missing")

        with self.repository() as root:
            self._write(
                root / "plugins" / "sample-skill" / "evals" / "outcomes.md",
                "# Trigger\n\n# Authorization\n\n# Outcome\n\n# Hold-out\n",
            )
            self.assert_invalid(root, "outcomes.md", "sections")

    def test_manifest_and_marketplace_plugin_names_must_match(self):
        with self.repository() as root:
            marketplace_path = root / ".claude-plugin" / "marketplace.json"
            marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
            marketplace["plugins"] = []
            self._write(
                marketplace_path,
                json.dumps(marketplace, indent=2) + "\n",
            )
            self.assert_invalid(root, "marketplace", "sample-skill")

    def test_plugin_manifest_does_not_declare_discovery_arrays(self):
        with self.repository(
            manifest_overrides={"skills": ["./skills/sample-skill"]}
        ) as root:
            self.assert_invalid(root, "plugin.json", "skills")

    def test_each_argument_surface_is_rejected(self):
        cases = [
            (
                "$ARGUMENTS placeholder",
                {"body": "# sample-skill\n\nProcess $ARGUMENTS.\n"},
                "$ARGUMENTS",
            ),
            (
                "English argument heading",
                {"body": "# sample-skill\n\n## Arguments\n\nProvide a file.\n"},
                "arguments",
            ),
            (
                "Japanese argument heading",
                {"body": "# sample-skill\n\n## 引数\n\nファイルを指定します。\n"},
                "引数",
            ),
            (
                "argument frontmatter",
                {"extra_frontmatter": {"argument-hint": "input-file"}},
                "argument-hint",
            ),
            (
                "skill-specific long option",
                {
                    "body": (
                        "# sample-skill\n\n## Options\n\n"
                        "`--summary-format` selects this skill's alternate output contract.\n"
                    )
                },
                "--summary-format",
            ),
        ]
        for label, overrides, expected in cases:
            with self.subTest(label=label):
                with self.repository(**overrides) as root:
                    self.assert_invalid(root, expected)

    def test_review_only_exception_and_named_tier_policy(self):
        apply_findings_body = (
            "# apply-findings\n\nUse review-only when the user requests no edits.\n"
        )
        with self.repository(
            plugin_name="apply-findings", body=apply_findings_body
        ) as root:
            self.assert_valid(root)

        other_skill_body = (
            "# sample-skill\n\nUse review-only when the user requests no edits.\n"
        )
        with self.repository(body=other_skill_body) as root:
            self.assert_invalid(root, "review-only")

        named_tier_body = (
            "# sample-skill\n\n## Tiers\n\n"
            "### deep-review\n\nThe deep-review tier performs expanded checks.\n"
        )
        with self.repository(body=named_tier_body) as root:
            self.assert_invalid(root, "tier")

        ordinary_mode_body = (
            "# sample-skill\n\n"
            "The editor may remain in its current mode while the check runs.\n"
        )
        with self.repository(body=ordinary_mode_body) as root:
            self.assert_valid(root)

    def test_slash_and_dollar_cross_skill_invocations_are_rejected(self):
        additional_plugins = [{"plugin_name": "other-skill"}]
        cases = [
            ("slash invocation", "Run `/other-skill` now.\n"),
            ("dollar mention", "Run `$other-skill` now.\n"),
        ]
        for label, invocation in cases:
            with self.subTest(label=label):
                body = "# sample-skill\n\n" + invocation
                with self.repository(
                    body=body, additional_plugins=additional_plugins
                ) as root:
                    self.assert_invalid(root, "another skill")

    def test_orphan_and_nested_markdown_references_are_rejected_and_direct_passes(self):
        with self.repository(
            files={"references/orphan.md": "# Orphan\n"}
        ) as root:
            self.assert_invalid(root, "orphan.md")

        nested_body = (
            "# sample-skill\n\n"
            "See [first](references/first.md) and [second](references/second.md).\n"
        )
        nested_files = {
            "references/first.md": "# First\n\nSee [second](second.md).\n",
            "references/second.md": "# Second\n",
        }
        with self.repository(body=nested_body, files=nested_files) as root:
            self.assert_invalid(root, "nested")

        direct_body = "# sample-skill\n\nSee [the guide](references/guide.md).\n"
        direct_files = {"references/guide.md": "# Guide\n\nUse this workflow.\n"}
        with self.repository(body=direct_body, files=direct_files) as root:
            self.assert_valid(root)

    def test_agents_markdown_file_is_rejected(self):
        with self.repository(
            files={"agents/reviewer.md": "# Reviewer agent\n"}
        ) as root:
            self.assert_invalid(root, "agents/reviewer.md")


if __name__ == "__main__":
    unittest.main()
