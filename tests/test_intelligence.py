"""Live index guard, architecture map, and git preflight guarantees."""
from __future__ import annotations

import pathlib
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cortex.db import migrate  # noqa: E402
from cortex.indexer import index_project  # noqa: E402
from cortex.intelligence import architecture, preflight  # noqa: E402


class TestRepositoryIntelligence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name) / "intel"
        (self.repo / "src").mkdir(parents=True)
        (self.repo / "tests").mkdir()
        (self.repo / "src" / "db.ts").write_text(
            "export const db = { query: async (_q: string) => [] };\n")
        (self.repo / "src" / "auth.ts").write_text(
            "import { db } from './db';\n"
            "export function login(email: string) { return db.query(email); }\n"
            "app.post('/login', login);\n")
        (self.repo / "src" / "app.ts").write_text(
            "import { login } from './auth';\nexport const boot = () => login('x');\n")
        (self.repo / "tests" / "auth.test.ts").write_text(
            "import { login } from '../src/auth';\ntest('login', () => login('x'));\n")
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "-C", str(self.repo), "-c", "user.email=t@t",
                        "-c", "user.name=t", "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "-c", "user.email=t@t",
                        "-c", "user.name=t", "commit", "-qm", "feat: auth"], check=True)
        head = subprocess.run(["git", "-C", str(self.repo), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        migrate(self.con)
        index_project(self.con, {
            "id": "intel", "name": "Intel", "path": str(self.repo),
            "repo_path": str(self.repo), "git_head": head,
            "top_exts": ".ts", "kind": "app"}, full=True)

    def tearDown(self):
        self.con.close()
        self.tmp.cleanup()

    def test_architecture_maps_surfaces_boundaries_and_hotspots(self):
        result = architecture(self.con, "intel")
        self.assertEqual(result["index_sync"]["status"], "current")
        self.assertEqual(result["summary"]["files"], 4)
        self.assertTrue(any(a["route"] == "/login" for a in result["api_surface"]))
        self.assertTrue(any(b["from"] == "tests" and b["to"] == "src" or
                            b["from"] == "tests" and b["to"].startswith("src/")
                            for b in result["boundaries"]))
        self.assertEqual(result["hotspots"][0]["path"], "src/auth.ts")

    def test_preflight_selects_tests_and_dependents(self):
        auth = self.repo / "src" / "auth.ts"
        auth.write_text(auth.read_text() + "\nexport const sessionTtl = 60;\n")
        result = preflight(self.con, "intel")
        self.assertEqual(result["changed_files"], [{"status": "M", "path": "src/auth.ts"}])
        self.assertEqual(result["test_mapping"], "mapped")
        self.assertIn("tests/auth.test.ts", result["recommended_tests"])
        self.assertIn("src/app.ts", result["direct_dependents"])
        self.assertIn("POST /login", result["api_surface"])
        self.assertIn(result["risk"], {"medium", "high"})

    def test_preflight_keeps_deleted_file_evidence(self):
        (self.repo / "src" / "auth.ts").unlink()
        result = preflight(self.con, "intel")
        self.assertEqual(result["risk"], "high")
        self.assertIn("tests/auth.test.ts", result["recommended_tests"])
        self.assertIn("src/app.ts", result["direct_dependents"])
        self.assertTrue(any("deletes" in reason for reason in result["reasons"]))

    def test_preflight_rejects_option_like_git_base(self):
        with self.assertRaises(ValueError):
            preflight(self.con, "intel", base="--output=/tmp/nope")


if __name__ == "__main__":
    unittest.main()
