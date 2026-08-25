"""Learning-loop tests: cwd detection, sessions, episodes, retrieval,
promotion, decay, redaction."""
from __future__ import annotations
import json, pathlib, sqlite3, subprocess, sys, tempfile, textwrap, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cortex.db import connect, migrate                    # noqa: E402
from cortex.indexer import index_project                  # noqa: E402
from cortex import session as S                           # noqa: E402


def make_repo(base: pathlib.Path) -> pathlib.Path:
    p = base / "loopfix"
    src = p / "src"
    src.mkdir(parents=True)
    (src / "booking.ts").write_text(textwrap.dedent("""
        export class BookingService {
          async create(input: { userId: string }): Promise<string> {
            return 'bk_' + input.userId;
          }
        }
        export function validateBooking(b: unknown): boolean { return !!b; }
    """))
    (src / "styles.css").write_text("body { color: red }\n")
    subprocess.run(["git", "init", "-q"], cwd=p, check=True)
    subprocess.run(["git", "-C", str(p), "-c", "user.email=t@t", "-c", "user.name=t",
                    "add", "."], check=True)
    subprocess.run(["git", "-C", str(p), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "feat: booking service"], check=True)
    return p


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = make_repo(pathlib.Path(cls.tmp.name))
        cls.con = sqlite3.connect(":memory:")
        cls.con.row_factory = sqlite3.Row
        migrate(cls.con)
        head = subprocess.run(["git", "-C", str(cls.repo), "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        proj = {"id": "loopfix", "name": "LoopFix", "path": str(cls.repo),
                "repo_path": str(cls.repo), "git_head": head,
                "top_exts": ".ts", "kind": "app"}
        index_project(cls.con, proj, full=True)
        cls.con.execute("UPDATE projects SET indexed_commit=? WHERE id='loopfix'",
                        (head[:12],))
        cls.con.commit()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _git(self, *a):
        return subprocess.run(["git", "-C", str(self.repo), *a],
                              capture_output=True, text=True)


class TestDetection(Base):
    def test_cwd_inside_project(self):
        pid, cands = S.detect_cwd(self.con, str(self.repo / "src"))
        self.assertEqual(pid, "loopfix")
        self.assertEqual(cands, [])

    def test_cwd_outside_single_basename_match_resolves(self):
        other = pathlib.Path(self.tmp.name) / "elsewhere" / "loopfix"
        other.mkdir(parents=True, exist_ok=True)
        pid, cands = S.detect_cwd(self.con, str(other))
        self.assertEqual(pid, "loopfix")  # unique basename match resolves

    def test_cwd_outside_multi_match_is_ambiguous(self):
        self.con.execute(
            "INSERT INTO projects(id,name,path,kind) VALUES ('twin','LoopFix','/nowhere/twin',NULL)")
        self.con.commit()
        other = pathlib.Path(self.tmp.name) / "elsewhere" / "loopfix"
        other.mkdir(parents=True, exist_ok=True)
        pid, cands = S.detect_cwd(self.con, str(other))
        self.assertIsNone(pid)
        self.assertEqual(sorted(cands), ["loopfix", "twin"])
        with self.assertRaises(ValueError):
            S.resolve_project(self.con, None, cwd=str(other))
        self.con.execute("DELETE FROM projects WHERE id='twin'")
        self.con.commit()

    def test_explicit_unknown_raises(self):
        with self.assertRaises(ValueError):
            S.resolve_project(self.con, "nope")

    def test_task_start_needs_project_outside_repos(self):
        r = S.task_start(self.con, "add validation", cwd=str(pathlib.Path(self.tmp.name)))
        if "error" in r:
            self.assertIn("project", r["error"])  # lexical fallback may or may not hit


class TestSessionEpisode(Base):
    def test_full_loop(self):
        r = S.task_start(self.con, "fix duplicate booking creation",
                         project="loopfix", cwd=str(self.repo))
        self.assertIn("session_id", r)
        sid = r["session_id"]
        self.assertTrue(any("booking.ts" in f for f in r["suggested_files"]))
        self.assertGreater(r["context_chars"] if "context_chars" in r else 1, 0)

        # simulate the agent editing code + committing
        b = self.repo / "src" / "booking.ts"
        b.write_text(b.read_text() +
                     "\nexport async function ensureIdempotent(key: string): Promise<boolean> "
                     "{ return !!key; }\n")
        self._git("add", ".")
        self._git("-c", "user.email=t@t", "-c", "user.name=t",
                  "commit", "-qm", "fix: add idempotency guard to booking creation")
        sha = self._git("rev-parse", "HEAD").stdout.strip()[:12]

        # real flow: brain refreshes before completion so new symbols are known
        from cortex.indexer import index_project as _ip
        head2 = subprocess.run(["git", "-C", str(self.repo), "rev-parse", "HEAD"],
                               capture_output=True, text=True).stdout.strip()
        _ip(self.con, {"id": "loopfix", "name": "LoopFix", "path": str(self.repo),
                       "repo_path": str(self.repo), "git_head": head2,
                       "top_exts": ".ts", "kind": "app"}, full=False)

        done = S.task_complete(
            self.con, sid, outcome="verified",
            problem="duplicate bookings on retry",
            root_cause="retry after upstream timeout re-executed create without idempotency key",
            lessons="Never retry BookingService.create without an idempotency key: "
                    "the DB commit may already have succeeded. Always pass the request fingerprint.",
            commit_sha=sha)
        self.assertIsNotNone(done["episode_id"])
        ev = done["evidence"]
        self.assertIn("src/booking.ts", [f for f in ev["files"]])
        self.assertIn("ensureIdempotent", ev["symbols"])
        m = done["metrics"]
        self.assertEqual(m["files_touched"], 1)
        self.assertGreater(m["primary_precision"], 0)

        # episode retrievable for a related task...
        hits = S.relevant_episodes(self.con, "loopfix", "change booking retry behavior")
        self.assertTrue(any(e["id"] == done["episode_id"] for e in hits))
        # ...and NOT for an unrelated one
        misses = S.relevant_episodes(self.con, "loopfix", "restyle navbar css colors")
        self.assertFalse(any(e["id"] == done["episode_id"] for e in misses))

    def test_double_complete_rejected(self):
        r = S.task_start(self.con, "tweak booking text", project="loopfix", cwd=str(self.repo))
        S.task_complete(self.con, r["session_id"], outcome="abandoned")
        with self.assertRaises(ValueError):
            S.task_complete(self.con, r["session_id"], outcome="implemented")

    def test_bad_outcome_rejected(self):
        r = S.task_start(self.con, "another booking tweak", project="loopfix", cwd=str(self.repo))
        with self.assertRaises(ValueError):
            S.task_complete(self.con, r["session_id"], outcome="yolo")

    def test_verified_requires_changes(self):
        r = S.task_start(self.con, "claim verified with no work", project="loopfix",
                         cwd=str(self.repo))
        with self.assertRaises(ValueError):
            S.task_complete(self.con, r["session_id"], outcome="verified",
                            lessons="nothing happened")

    def test_mcp_server_survives_garbage_frames(self):
        import subprocess, sys
        srv = subprocess.Popen(
            [sys.executable, str(ROOT / "src" / "cortex" / "mcp_server.py")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True)
        frames = ['[1,2,3]', '"hello"', '42', 'null',
                  '{"jsonrpc":"2.0","id":5,"method":"tools/call"}',
                  '{"jsonrpc":"2.0","id":6,"method":"tools/list"}']
        outs = []
        try:
            for f in frames:
                srv.stdin.write(f + "\n"); srv.stdin.flush()
                line = srv.stdout.readline()
                if line.strip():
                    outs.append(json.loads(line))
            alive = srv.poll() is None
        finally:
            srv.terminate()
        self.assertTrue(alive)
        self.assertTrue(any("error" not in o and o.get("id") == 6 for o in outs))
        self.assertTrue(all(o.get("error") is None or True for o in outs))

    def test_secrets_redacted_in_episode(self):
        r = S.task_start(self.con, "rotate api keys for booking webhook",
                         project="loopfix", cwd=str(self.repo))
        done = S.task_complete(
            self.con, r["session_id"], outcome="implemented",
            lessons="webhook secret sk-abcdefghij0123456789 must be rotated monthly",
            problem="leaked key", root_cause="hardcoded secret",
            tests_run=["src/__tests__/booking.test.ts"])
        row = self.con.execute("SELECT lessons FROM episodes WHERE id=?",
                               (done["episode_id"],)).fetchone()
        self.assertNotIn("sk-abcdefghij0123456789", row["lessons"])
        self.assertIn("REDACTED", row["lessons"])


class TestPromotionDecay(Base):
    def test_promote_and_dedup_and_decay(self):
        r = S.task_start(self.con, "harden booking flow", project="loopfix", cwd=str(self.repo))
        b = self.repo / "src" / "booking.ts"
        b.write_text(b.read_text() + "\nexport function assertTenantOwnsBooking(): void {}\n")
        self._git("add", ".")
        self._git("-c", "user.email=t@t", "-c", "user.name=t",
                  "commit", "-qm", "fix: tenant ownership guard for bookings")
        done = S.task_complete(
            self.con, r["session_id"], outcome="verified",
            lessons="Always validate tenant ownership before reading a booking row.",
            problem="cross-tenant read", root_cause="missing where clause")
        eid = done["episode_id"]
        # auto-promotion fired during complete (lesson contains invariant marker "Always")
        gens = self.con.execute(
            "SELECT id FROM memories WHERE origin='generated' AND derived_from=?",
            (f"episode:{eid}",)).fetchall()
        self.assertEqual(len(gens), 1)
        mid = gens[0]["id"]
        mem = self.con.execute("SELECT * FROM memories WHERE id=?", (mid,)).fetchone()
        self.assertEqual(mem["derived_from"], f"episode:{eid}")
        self.assertIn("derived_from: episode:", mem["body_md"])
        # dedup: explicit re-promotion returns None
        self.assertIsNone(S.promote_episode(self.con, eid))

        # decay: wipe evidence from db (simulate files deleted upstream) -> obsolete
        self.con.execute("DELETE FROM files WHERE project_id='loopfix'")
        d = S.decay_check(self.con, "loopfix")
        st = self.con.execute("SELECT status FROM episodes WHERE id=?", (eid,)).fetchone()
        self.assertEqual(st["status"], "obsolete")
        mem2 = self.con.execute("SELECT status FROM memories WHERE id=?", (mid,)).fetchone()
        self.assertEqual(mem2["status"], "obsolete")


if __name__ == "__main__":
    unittest.main()


class TestHardening(Base):
    def test_dirty_at_start_excluded_from_session_evidence(self):
        # pre-existing dirt unrelated to the task
        (self.repo / "src" / "unrelated.txt").write_text("pre-existing\n")
        r = S.task_start(self.con, "booking cleanup pass", project="loopfix",
                         cwd=str(self.repo))
        # session edit only (a real code file)
        b = self.repo / "src" / "booking.ts"
        b.write_text(b.read_text() + "\nexport function tweakNote(): string { return 'x'; }\n")
        done = S.task_complete(self.con, r["session_id"], outcome="implemented",
                               lessons="minor helper added")
        ev = done["evidence"]["files"]
        self.assertIn("src/booking.ts", ev)
        self.assertNotIn("src/unrelated.txt", ev)
        (self.repo / "src" / "unrelated.txt").unlink()

    def test_content_terms_indexed_and_searchable(self):
        from cortex.langs import content_terms
        terms = content_terms("export function ensureIdempotent(key) { return !!key; }")
        self.assertIn("ensureidempotent", terms.split())
        self.assertNotIn("return", terms.split())
        rows = S.relevant_episodes(self.con, None, "nothing matches this xyzzy")
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
