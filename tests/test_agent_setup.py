"""Agent-skill packaging and installation guarantees."""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cortex.agent_setup import install_agent_skill, skill_destinations  # noqa: E402


class TestAgentSkill(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = pathlib.Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_user_install_covers_portable_and_claude_paths(self):
        results = install_agent_skill(home=self.home)
        self.assertEqual([r["status"] for r in results], ["installed", "installed"])
        for destination in skill_destinations(home=self.home):
            skill = destination / "SKILL.md"
            metadata = destination / "agents" / "openai.yaml"
            self.assertTrue(skill.is_file())
            self.assertTrue(metadata.is_file())
            self.assertIn("name: project-cortex", skill.read_text())

    def test_reinstall_is_idempotent(self):
        install_agent_skill(home=self.home)
        results = install_agent_skill(home=self.home)
        self.assertEqual([r["status"] for r in results], ["unchanged", "unchanged"])

    def test_modified_skill_is_preserved_without_force(self):
        install_agent_skill(home=self.home)
        destination = skill_destinations(home=self.home)[0]
        (destination / "SKILL.md").write_text("local customization\n")

        results = install_agent_skill(home=self.home)

        self.assertEqual(results[0]["status"], "conflict")
        self.assertEqual((destination / "SKILL.md").read_text(), "local customization\n")
        self.assertEqual(results[1]["status"], "unchanged")

    def test_missing_metadata_is_repaired_without_force(self):
        install_agent_skill(home=self.home)
        destination = skill_destinations(home=self.home)[0]
        (destination / "agents" / "openai.yaml").unlink()

        results = install_agent_skill(home=self.home)

        self.assertEqual(results[0]["status"], "updated")
        self.assertTrue((destination / "agents" / "openai.yaml").is_file())

    def test_force_replaces_only_shipped_files(self):
        install_agent_skill(home=self.home)
        destination = skill_destinations(home=self.home)[0]
        (destination / "SKILL.md").write_text("local customization\n")
        extra = destination / "notes.md"
        extra.write_text("keep me\n")

        results = install_agent_skill(home=self.home, force=True)

        self.assertEqual(results[0]["status"], "updated")
        self.assertIn("name: project-cortex", (destination / "SKILL.md").read_text())
        self.assertEqual(extra.read_text(), "keep me\n")

    def test_project_scope_uses_repository_paths(self):
        root = self.home / "repo"
        results = install_agent_skill(scope="project", project_root=root)
        self.assertEqual(len(results), 2)
        self.assertTrue((root / ".agents/skills/project-cortex/SKILL.md").is_file())
        self.assertTrue((root / ".claude/skills/project-cortex/SKILL.md").is_file())

    def test_checked_in_and_packaged_skills_stay_identical(self):
        checked_in = ROOT / ".agents" / "skills" / "project-cortex"
        packaged = ROOT / "src" / "cortex" / "skills" / "project-cortex"
        for relative in ("SKILL.md", "agents/openai.yaml"):
            self.assertEqual((checked_in / relative).read_bytes(),
                             (packaged / relative).read_bytes())


if __name__ == "__main__":
    unittest.main()
