import unittest

from scripts.check_version_bump import bump_errors


def marketplace(version):
    return {"version": version}


class CheckVersionBumpTest(unittest.TestCase):
    def errors(self, changed, base_top, head_top, base_plugin, head_plugin):
        return bump_errors(
            changed,
            marketplace(base_top),
            marketplace(head_top),
            {"sample": base_plugin},
            {"sample": head_plugin},
        )

    def test_skill_change_with_both_minor_bumps_passes(self):
        self.assertEqual(
            [],
            self.errors(["plugins/sample/skills/sample/SKILL.md"], "1.2.0", "1.3.0", "2.0.0", "2.1.0"),
        )

    def test_skill_change_without_plugin_bump_fails(self):
        errors = self.errors(["plugins/sample/skills/sample/SKILL.md"], "1.2.0", "1.3.0", "2.0.0", "2.0.0")
        self.assertEqual(1, len(errors))
        self.assertIn("plugins/sample", errors[0])

    def test_skill_change_without_top_level_bump_fails(self):
        errors = self.errors(["plugins/sample/skills/sample/references/x.md"], "1.2.0", "1.2.0", "2.0.0", "2.1.0")
        self.assertEqual(1, len(errors))
        self.assertIn("top-level", errors[0])

    def test_patch_bump_is_rejected(self):
        errors = self.errors(["plugins/sample/commands/sample.md"], "1.2.0", "1.2.1", "2.0.0", "2.0.1")
        self.assertEqual(2, len(errors))

    def test_major_bump_passes(self):
        self.assertEqual(
            [],
            self.errors(["plugins/sample/skills/sample/SKILL.md"], "1.2.0", "2.0.0", "2.0.0", "3.0.0"),
        )

    def test_eval_only_change_needs_no_bump(self):
        self.assertEqual(
            [],
            self.errors(["plugins/sample/evals/01-case/prompt.md", "scripts/validate_skills.py"], "1.2.0", "1.2.0", "2.0.0", "2.0.0"),
        )


if __name__ == "__main__":
    unittest.main()
