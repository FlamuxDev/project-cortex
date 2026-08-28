"""Disk-truth and vault-hygiene guarantees.

These cover the failure modes where the brain keeps serving knowledge that no
longer matches the filesystem, and where generated pages outlive their source.
"""
from __future__ import annotations
import json, os, pathlib, shutil, sqlite3, subprocess, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cortex.db import code_root, migrate                      # noqa: E402
from cortex.indexer import index_project                      # noqa: E402
from cortex.contextpack import context, context_text          # noqa: E402


def _mem_db():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    migrate(con)
    return con


def _repo(base: pathlib.Path, sub: str = "") -> tuple[pathlib.Path, pathlib.Path]:
    """Project dir, and the code root inside it (optionally a subdirectory)."""
    proj = base / "proj"
    code = proj / sub if sub else proj
    (code / "src").mkdir(parents=True)
    (code / "src" / "billing.ts").write_text(
        "export class BillingService { charge(cents: number) { return cents } }\n")
    (code / "src" / "index.ts").write_text("import { BillingService } from './billing'\n")
    (code / "package.json").write_text('{"name":"p","dependencies":{"express":"^4"}}')
    subprocess.run(["git", "init", "-q"], cwd=code, check=True)
    subprocess.run(["git", "-C", str(code), "-c", "user.email=t@t", "-c", "user.name=t",
                    "add", "."], check=True)
    subprocess.run(["git", "-C", str(code), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "feat: billing"], check=True)
    return proj, code


def _index(con, proj_dir, code_dir, pid="p"):
    head = subprocess.run(["git", "-C", str(code_dir), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    return index_project(con, {
        "id": pid, "name": pid, "path": str(proj_dir), "repo_path": str(code_dir),
        "git_head": head, "top_exts": "ts", "kind": "app"}, full=True)


class TestCodeRoot(unittest.TestCase):
    """Code living in a subdirectory must stay resolvable after indexing."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj, self.code = _repo(pathlib.Path(self.tmp.name), sub="app")
        self.con = _mem_db()
        _index(self.con, self.proj, self.code)

    def tearDown(self):
        self.con.close()
        self.tmp.cleanup()

    def test_repo_path_is_persisted(self):
        row = self.con.execute("SELECT * FROM projects WHERE id='p'").fetchone()
        self.assertEqual(row["repo_path"], str(self.code))
        self.assertNotEqual(row["repo_path"], row["path"])

    def test_indexed_paths_resolve_under_code_root(self):
        row = self.con.execute("SELECT * FROM projects WHERE id='p'").fetchone()
        root = pathlib.Path(code_root(row))
        files = [r["path"] for r in self.con.execute("SELECT path FROM files WHERE project_id='p'")]
        self.assertTrue(files)
        for f in files:
            self.assertTrue((root / f).exists(), f"{f} unresolvable under {root}")

    def test_code_root_falls_back_to_path(self):
        self.con.execute("UPDATE projects SET repo_path=NULL WHERE id='p'")
        row = self.con.execute("SELECT * FROM projects WHERE id='p'").fetchone()
        self.assertEqual(code_root(row), row["path"])

    def test_packet_path_header_is_the_code_root(self):
        txt = context_text(self.con, "fix billing charge", "p", 800)
        self.assertIn(f"PATH: {self.code}", txt)

    def test_file_content_is_full_text_indexed(self):
        ids = [r[0] for r in self.con.execute("SELECT rowid FROM files WHERE project_id='p'")]
        q = ",".join("?" * len(ids))
        terms = [r[0] for r in self.con.execute(
            f"SELECT terms FROM fts_files WHERE rowid IN ({q})", ids)]
        self.assertTrue(any((t or "").strip() for t in terms),
                        "no file content indexed — code root was misresolved")


class TestDiscovery(unittest.TestCase):
    def test_nested_repo_selection_ignores_unrelated_first_directory(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = pathlib.Path(tmp.name) / "repos"
        wrapper = root / "wrapped-project"
        (wrapper / "docs").mkdir(parents=True)
        app = wrapper / "service"
        (app / "src").mkdir(parents=True)
        (app / "src" / "a.py").write_text("def a(): pass\n")
        (app / "src" / "b.py").write_text("def b(): pass\n")
        (app / "src" / "c.py").write_text("def c(): pass\n")
        subprocess.run(["git", "init", "-q", str(app)], check=True)

        from cortex.discovery import discover_projects
        projects = discover_projects(root)

        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["path"], str(wrapper))
        self.assertEqual(projects[0]["repo_path"], str(app))


class TestDiskTruth(unittest.TestCase):
    """A packet must never claim freshness for code that is not on disk."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj, self.code = _repo(pathlib.Path(self.tmp.name))
        self.con = _mem_db()
        _index(self.con, self.proj, self.code)

    def tearDown(self):
        self.con.close()
        self.tmp.cleanup()

    def test_healthy_project_reports_fresh(self):
        self.assertIn("FRESHNESS: fresh", context_text(self.con, "fix billing", "p", 800))

    def test_dirty_worktree_is_not_reported_fresh(self):
        (self.code / "src" / "billing.ts").write_text(
            "export function changed() { return true }\n")
        txt = context_text(self.con, "fix billing", "p", 800)
        self.assertNotIn("FRESHNESS: fresh", txt)
        self.assertIn("DIRTY", txt)
        self.assertIsNotNone(self.con.execute(
            "SELECT 1 FROM symbols WHERE project_id='p' AND name='changed'").fetchone())

    def test_live_guard_refreshes_each_new_dirty_snapshot_once(self):
        billing = self.code / "src" / "billing.ts"
        billing.write_text("export function firstSnapshot() { return 1 }\n")
        first = context(self.con, "first snapshot billing", "p", 800)
        self.assertEqual(first["index_sync"]["status"], "refreshed")
        self.assertIsNotNone(self.con.execute(
            "SELECT 1 FROM symbols WHERE project_id='p' AND name='firstSnapshot'").fetchone())

        unchanged = context(self.con, "first snapshot billing", "p", 800)
        self.assertEqual(unchanged["index_sync"]["status"], "current")

        billing.write_text("export function secondSnapshot() { return 2 }\n")
        second = context(self.con, "second snapshot billing", "p", 800)
        self.assertEqual(second["index_sync"]["status"], "refreshed")
        self.assertIsNotNone(self.con.execute(
            "SELECT 1 FROM symbols WHERE project_id='p' AND name='secondSnapshot'").fetchone())
        self.assertIsNone(self.con.execute(
            "SELECT 1 FROM symbols WHERE project_id='p' AND name='firstSnapshot'").fetchone())

    def test_non_code_dirty_file_does_not_force_reindex(self):
        (self.code / "README.md").write_text("docs only\n")
        result = context(self.con, "fix billing", "p", 800)
        self.assertEqual(result["index_sync"]["status"], "current")
        self.assertIn("DIRTY", result["packet"])

    def test_new_commit_reports_live_distance_before_reindex(self):
        (self.code / "src" / "new.ts").write_text("export const added = true\n")
        subprocess.run(["git", "-C", str(self.code), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.code), "-c", "user.email=t@t",
                        "-c", "user.name=t", "commit", "-qm", "feat: add file"], check=True)
        txt = context_text(self.con, "fix billing", "p", 800, refresh="never")
        self.assertNotIn("FRESHNESS: fresh", txt)
        self.assertIn("1 commit(s)", txt)

    def test_non_git_project_reports_freshness_unavailable(self):
        shutil.rmtree(self.code / ".git")
        self.con.execute("UPDATE projects SET indexed_commit=NULL WHERE id='p'")
        txt = context_text(self.con, "fix billing", "p", 800, refresh="never")
        self.assertIn("FRESHNESS: not available (non-git project)", txt)
        self.assertNotIn("STALE", txt)

    def test_non_git_live_guard_updates_incrementally(self):
        shutil.rmtree(self.code / ".git")
        self.con.execute("UPDATE projects SET indexed_commit=NULL WHERE id='p'")
        self.con.commit()
        billing = self.code / "src" / "billing.ts"
        billing.write_text("export function offlineChange() { return true }\n")

        result = context(self.con, "offline billing change", "p", 800)

        self.assertEqual(result["index_sync"]["status"], "refreshed")
        self.assertEqual(result["index_sync"]["stats"]["changed"], 1)
        self.assertIsNotNone(self.con.execute(
            "SELECT 1 FROM symbols WHERE project_id='p' AND name='offlineChange'").fetchone())

    def test_moved_code_is_flagged_not_called_fresh(self):
        # the directory survives but the indexed files no longer live there
        for f in (self.code / "src").iterdir():
            f.unlink()
        txt = context_text(self.con, "fix billing", "p", 800, refresh="never")
        self.assertNotIn("FRESHNESS: fresh", txt)
        self.assertIn("STALE", txt)

    def test_deleted_project_dir_is_flagged(self):
        self.con.execute("UPDATE projects SET path=?, repo_path=? WHERE id='p'",
                         ("/nonexistent/gone", "/nonexistent/gone"))
        txt = context_text(self.con, "fix billing", "p", 800)
        self.assertNotIn("FRESHNESS: fresh", txt)
        self.assertIn("DOES NOT EXIST", txt)

    def test_unknown_project_raises_a_useful_error(self):
        with self.assertRaises(ValueError) as cm:
            context_text(self.con, "anything", "no-such-project", 800)
        self.assertIn("no-such-project", str(cm.exception))
        self.assertIn("p", str(cm.exception))   # names what IS indexed

    def test_refresh_lock_recovers_after_owner_process_dies(self):
        from cortex.indexer import _lock_dir, project_refresh_lock
        lock_root = _lock_dir(self.con)
        lock_root.mkdir(parents=True, exist_ok=True)
        lock = lock_root / "p.lock"
        dead_pid = max(os.getpid() + 10_000_000, 999_999_999)
        lock.write_text(f"pid={dead_pid} time=0\n")

        with project_refresh_lock(self.con, "p", timeout=0.2):
            self.assertTrue(lock.exists())

        self.assertFalse(lock.exists())


class TestFtsCoverage(unittest.TestCase):
    """Indexing one project must not blind full-text search for the others."""

    def test_full_index_does_not_wipe_other_projects(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = pathlib.Path(tmp.name)
        con = _mem_db()
        self.addCleanup(con.close)

        a_proj, a_code = _repo(base / "a")
        _index(con, a_proj, a_code, pid="a")

        def fts_rows(pid):
            return con.execute(
                "SELECT COUNT(*) FROM fts_symbols WHERE rowid IN "
                "(SELECT id FROM symbols WHERE project_id=?)", (pid,)).fetchone()[0]

        before = fts_rows("a")
        self.assertGreater(before, 0)

        b_proj, b_code = _repo(base / "b")
        _index(con, b_proj, b_code, pid="b")          # full index of a DIFFERENT project

        self.assertEqual(fts_rows("a"), before, "indexing 'b' wiped 'a' from the symbol index")
        self.assertGreater(fts_rows("b"), 0)

    def test_version_upgrade_repairs_derived_index(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        con = _mem_db()
        self.addCleanup(con.close)
        proj, code = _repo(pathlib.Path(tmp.name))
        _index(con, proj, code)
        con.execute("UPDATE refs SET dst_path=NULL WHERE project_id='p'")
        con.execute("UPDATE index_state SET value='1:legacy' WHERE key='worktree:p'")
        con.commit()

        result = context(con, "billing charge", "p", 800)

        self.assertEqual(result["index_sync"]["status"], "refreshed")
        self.assertEqual(con.execute(
            """SELECT dst_path FROM refs WHERE project_id='p' AND src_path='src/index.ts'
               AND kind='import'""").fetchone()["dst_path"], "src/billing.ts")
        self.assertIn("format_repair", result["index_sync"]["stats"])

    def test_full_rebuild_preserves_live_module_ownership(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        con = _mem_db()
        self.addCleanup(con.close)
        proj, code = _repo(pathlib.Path(tmp.name))
        _index(con, proj, code)
        con.execute("""INSERT INTO modules(id,project_id,name,slug,path_prefixes)
                       VALUES ('p:billing','p','Billing','billing','src')""")
        con.executemany("""INSERT INTO module_files(module_id,project_id,path)
                           VALUES ('p:billing','p',?)""",
                        [("src/billing.ts",), ("src/gone.ts",)])
        con.commit()

        _index(con, proj, code)

        owned = [row["path"] for row in con.execute(
            "SELECT path FROM module_files WHERE module_id='p:billing' ORDER BY path")]
        self.assertEqual(owned, ["src/billing.ts"])

    def test_reindex_prunes_contentless_fts_ghosts(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        con = _mem_db()
        self.addCleanup(con.close)
        proj, code = _repo(pathlib.Path(tmp.name))
        _index(con, proj, code)

        # Removing a symbol-bearing file used to leave its old contentless FTS
        # row behind because source rows were deleted before FTS cleanup.
        (code / "src" / "billing.ts").unlink()
        _index(con, proj, code)

        symbols = con.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
        fts_symbols = con.execute("SELECT COUNT(*) FROM fts_symbols").fetchone()[0]
        files = con.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        fts_files = con.execute("SELECT COUNT(*) FROM fts_files").fetchone()[0]
        self.assertEqual(fts_symbols, symbols)
        self.assertEqual(fts_files, files)

    def test_incremental_reindex_keeps_changed_test_mapping(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        con = _mem_db()
        self.addCleanup(con.close)
        proj, code = _repo(pathlib.Path(tmp.name))
        tests = code / "src" / "__tests__"
        tests.mkdir()
        test_file = tests / "billing.test.ts"
        test_file.write_text("import { BillingService } from '../billing'\n")
        _index(con, proj, code)

        test_file.write_text("import { BillingService } from '../billing'\n// changed\n")
        head = subprocess.run(["git", "-C", str(code), "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        from cortex.indexer import index_project
        index_project(con, {
            "id": "p", "name": "p", "path": str(proj), "repo_path": str(code),
            "git_head": head, "top_exts": "ts", "kind": "app",
        }, full=False)

        row = con.execute("SELECT targets_json FROM tests WHERE project_id='p' "
                          "AND path='src/__tests__/billing.test.ts'").fetchone()
        self.assertIsNotNone(row)
        self.assertIn("src/billing.ts", json.loads(row["targets_json"] or "[]"))

    def test_incremental_removal_clears_stale_import_and_test_mapping(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        con = _mem_db()
        self.addCleanup(con.close)
        proj, code = _repo(pathlib.Path(tmp.name))
        tests = code / "src" / "__tests__"
        tests.mkdir()
        (tests / "billing.test.ts").write_text(
            "import { BillingService } from '../billing'\n")
        _index(con, proj, code)

        (code / "src" / "billing.ts").unlink()
        head = subprocess.run(["git", "-C", str(code), "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        from cortex.indexer import index_project
        index_project(con, {
            "id": "p", "name": "p", "path": str(proj), "repo_path": str(code),
            "git_head": head, "top_exts": "ts", "kind": "app",
        }, full=False)

        ref = con.execute("SELECT dst_path FROM refs WHERE project_id='p' "
                          "AND dst_name='../billing'").fetchone()
        row = con.execute("SELECT targets_json FROM tests WHERE project_id='p' "
                          "AND path='src/__tests__/billing.test.ts'").fetchone()
        self.assertIsNotNone(ref)
        self.assertIsNone(ref["dst_path"])
        self.assertEqual(json.loads(row["targets_json"] or "[]"), [])


class TestVaultPrune(unittest.TestCase):
    """Generated pages must not outlive the rows they describe."""

    def test_prune_removes_orphans_and_keeps_human_notes(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        vault_dir = pathlib.Path(tmp.name) / "vault"
        (vault_dir / "Projects").mkdir(parents=True)

        from cortex import vault
        vault._WRITTEN.clear()

        live = vault_dir / "Projects" / "Live.md"
        orphan = vault_dir / "Projects" / "Orphan.md"
        human = vault_dir / "Projects" / "MyNotes.md"
        orphan.write_text(vault.fm("orphan", "[x]") + "stale page\n")
        human.write_text("# my own notes, no frontmatter\n")

        vault.w(live, vault.fm("live", "[x]") + "current\n")
        removed = vault.prune(vault_dir)

        self.assertEqual([p.name for p in removed], ["Orphan.md"])
        self.assertTrue(live.exists())
        self.assertTrue(human.exists(), "a hand-written note was deleted")
        self.assertFalse(orphan.exists())

    def test_generate_resets_written_paths_between_runs(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        vault_dir = pathlib.Path(tmp.name) / "vault"
        vault_dir.mkdir()
        con = _mem_db()
        self.addCleanup(con.close)

        from cortex import vault
        original_vault = vault.VAULT
        self.addCleanup(setattr, vault, "VAULT", original_vault)
        vault.VAULT = vault_dir
        orphan = vault_dir / "old.md"
        orphan.write_text(vault.fm("old", "[x]") + "old\n")
        vault._WRITTEN.add(orphan.resolve())  # state left by a previous run

        vault.generate(con)

        self.assertFalse(orphan.exists())


if __name__ == "__main__":
    unittest.main()
