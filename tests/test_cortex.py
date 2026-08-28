"""Project Cortex test suite (stdlib unittest).

Run: .venv/bin/python -m pytest tests -q   OR   .venv/bin/python -m unittest discover tests
"""
from __future__ import annotations
import json, pathlib, sqlite3, subprocess, sys, tempfile, textwrap, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cortex import extractors, langs, search          # noqa: E402
from cortex.contextpack import context, impact        # noqa: E402


def make_fixture_repo(base: pathlib.Path) -> pathlib.Path:
    """Tiny fake project with ts+py+sql+git history."""
    p = base / "fixture"
    src = p / "src"
    src.mkdir(parents=True)
    (src / "auth.ts").write_text(textwrap.dedent("""
        import { db } from './db'
        export interface Session { userId: string; tenantId: string }
        export class AuthService {
          async login(email: string): Promise<Session> {
            return db.query('select * from users where email=$1')
          }
        }
        export function requireSession(s?: Session): Session {
          if (!s) throw new Error('unauthorized');
          return s;
        }
    """))
    (src / "db.ts").write_text("export const db = { query: async (_q: string) => [] };\n")
    tests = p / "src" / "__tests__"
    tests.mkdir()
    (tests / "auth.test.ts").write_text(
        "import { AuthService } from '../auth';\n"
        "test('login returns session', () => {});\n")
    (p / "schema.sql").write_text(
        "CREATE TABLE users (id uuid primary key, email text unique);\n"
        "CREATE POLICY tenant_isolation ON users USING (tenant_id = current_setting('app.tenant'));\n")
    (p / "main.py").write_text(textwrap.dedent("""
        '''Entry point.'''
        from helpers import format_money
        class Invoice:
            def total(self, cents: int) -> int:
                return cents
        def run():
            print(format_money(5))
    """))
    (p / "helpers.py").write_text("def format_money(cents):\n    return f'{cents/100:.2f}'\n")
    subprocess.run(["git", "init", "-q"], cwd=p, check=True)
    subprocess.run(["git", "-C", str(p), "-c", "user.email=t@t", "-c", "user.name=t",
                    "add", "."], check=True)
    subprocess.run(["git", "-C", str(p), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "feat: initial auth and invoicing"], check=True)
    return p


class TestLangs(unittest.TestCase):
    def test_redaction(self):
        self.assertNotIn("sk-abcdefghij0123456789", langs.redact("key sk-abcdefghij0123456789"))
        self.assertIn("REDACTED", langs.redact("password: 'hunter22'"))
        pem = langs.redact("-----BEGIN RSA PRIVATE KEY-----\nMIIEabc\n-----END RSA PRIVATE KEY-----")
        self.assertNotIn("MIIEabc", pem)

    def test_test_detection(self):
        self.assertTrue(langs.is_test("src/__tests__/a.test.ts"))
        self.assertTrue(langs.is_test("services/x/foo_test.go"))
        self.assertFalse(langs.is_test("src/auth.ts"))


class TestExtractors(unittest.TestCase):
    def test_ts_symbols_and_routes(self):
        r = extractors.extract_ts(textwrap.dedent('''
            import { x } from './x';
            export class Foo { bar() {} }
            export function baz(a: number) {}
            app.get('/health', handler);
            const Cmp = () => null;
        ''').encode(), 'ts', 'a.ts')
        names = {(s["name"], s["kind"]) for s in r["symbols"]}
        self.assertIn(("Foo", "class"), names)
        self.assertIn(("baz", "function"), names)
        self.assertIn(("bar", "method"), names)
        self.assertIn(("Cmp", "component"), names)
        self.assertIn(("./x",), [(rr["dst_name"],) for rr in r["refs"]])
        self.assertEqual(r["routes"][0]["route"], "/health")

    def test_nestjs_decorators(self):
        r = extractors.extract_ts(textwrap.dedent('''
            @Controller('knowledge')
            class KnowledgeController {
              @Get(':key') get() {}
              @Post() create() {}
            }
        ''').encode(), 'ts', 'k.ts')
        routes = sorted(rt["route"] for rt in r["routes"])
        self.assertEqual(routes, ["/knowledge", "/knowledge/:key"])

    def test_py(self):
        r = extractors.extract_py(textwrap.dedent('''
            from fastapi import APIRouter
            router = APIRouter()
            @router.get("/things")
            def list_things(): pass
            class A:
                def m(self): pass
        ''').encode(), 'a.py')
        kinds = {(s["name"], s["kind"]) for s in r["symbols"]}
        self.assertIn(("list_things", "function"), kinds)
        self.assertIn(("A", "class"), kinds)
        self.assertEqual(r["routes"][0]["route"], "/things")

    def test_sql(self):
        r = extractors.extract_sql(b"CREATE TABLE tenants(id uuid);\nCREATE POLICY rls ON tenants;", "s.sql")
        self.assertIn(("tenants", "table"), [(t["name"], t["kind"]) for t in r["tables"]])
        self.assertTrue(any(s["kind"] == "rls_policy" for s in r["symbols"]))

    def test_go(self):
        r = extractors.extract_go(b'''
            package main
            import "net/http"
            type Svc struct{}
            func (s *Svc) Do() {}
            func main() { http.HandleFunc("/x", nil) }
        ''', 'm.go')
        kinds = {(s["name"], s["kind"]) for s in r["symbols"]}
        self.assertIn(("Svc", "struct"), kinds)
        self.assertIn(("Do", "method"), kinds)


class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = make_fixture_repo(pathlib.Path(cls.tmp.name))
        # index fixture as its own project row (bypass discovery for isolation)
        cls.con = sqlite3.connect(":memory:")
        cls.con.row_factory = sqlite3.Row
        cls.con.execute("PRAGMA foreign_keys=ON")
        from cortex.db import migrate
        migrate(cls.con)
        from cortex.indexer import index_project
        proj = {"id": "fixture", "name": "fixture", "path": str(cls.repo),
                "repo_path": str(cls.repo), "git_head": subprocess.run(
                    ["git", "-C", str(cls.repo), "rev-parse", "HEAD"],
                    capture_output=True, text=True).stdout.strip(),
                "top_exts": ".ts,.py,.sql", "kind": "app"}
        cls.stats = index_project(cls.con, proj, full=True)

    @classmethod
    def tearDownClass(cls):
        cls.con.close()
        cls.tmp.cleanup()

    def test_counts(self):
        s = self.stats
        self.assertGreaterEqual(s["files"], 6)
        self.assertGreaterEqual(s["symbols"], 8)
        self.assertGreaterEqual(s["tables"], 1)

    def test_symbols_queryable(self):
        rows = search.search_symbols(self.con, "fixture", "session login", limit=5)
        self.assertTrue(any("auth.ts" in r["path"] for r in rows))
        exact = self.con.execute(
            "SELECT path FROM symbols WHERE project_id='fixture' AND name='AuthService'").fetchone()
        self.assertIsNotNone(exact)

    def test_import_resolution(self):
        edge = self.con.execute("""SELECT dst_path FROM refs WHERE project_id='fixture'
                                   AND kind='import' AND dst_name='./db'""").fetchone()
        self.assertIsNotNone(edge)
        if edge["dst_path"]:
            self.assertEqual(edge["dst_path"], "src/db.ts")

    def test_python_src_layout_import_resolution(self):
        from cortex.indexer import resolve_import
        files = {"src/cortex/db.py", "src/cortex/__init__.py", "tests/test_db.py"}
        self.assertEqual(resolve_import("cortex.db.connect", "tests/test_db.py", files, "p"),
                         "src/cortex/db.py")

    def test_test_mapping(self):
        t = self.con.execute("SELECT targets_json FROM tests WHERE path LIKE '%auth.test%'").fetchone()
        self.assertIsNotNone(t)
        self.assertIn("src/auth.ts", json.loads(t["targets_json"]))

    def test_rls_captured(self):
        n = self.con.execute("""SELECT COUNT(*) c FROM symbols WHERE project_id='fixture'
                                AND kind='rls_policy'""").fetchone()["c"]
        self.assertGreaterEqual(n, 1)

    def test_context_packet(self):
        r = context(self.con, "fix unauthorized login session handling", project_id="fixture", budget=2000)
        self.assertIn("PRIMARY FILES", r["packet"])
        self.assertIn("auth.ts", r["packet"])
        self.assertLessEqual(r["tokens_est"], 2000)

    def test_impact(self):
        r = impact(self.con, "src/auth.ts", project_id="fixture")
        self.assertEqual(r["project"], "fixture")
        self.assertIn("src/auth.ts", r["targets"])
        self.assertTrue(any("__tests__" in t or "auth" in t for t in r["tests"]))

    def test_incremental_update_detects_change(self):
        auth = self.repo / "src" / "auth.ts"
        original = auth.read_text()
        try:
            auth.write_text(original + "\nexport function newThing() { return 1 }\n")
            subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(self.repo), "-c", "user.email=t@t", "-c", "user.name=t",
                            "commit", "-qm", "feat: add newThing"], check=True)
            # register fixture in projects table already done; craft proj dict
            proj = {"id": "fixture", "name": "fixture", "path": str(self.repo),
                    "repo_path": str(self.repo), "git_head": subprocess.run(
                        ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
                        capture_output=True, text=True).stdout.strip(),
                    "top_exts": ".ts", "kind": "app"}
            stats = indexer_update(self.con, proj)
            self.assertGreaterEqual(stats.get("changed", 0), 1)
            row = self.con.execute(
                "SELECT COUNT(*) c FROM symbols WHERE name='newThing' AND project_id='fixture'").fetchone()
            self.assertGreaterEqual(row["c"], 1)
        finally:
            auth.write_text(original)

    def test_stale_memory_flagging(self):
        """Isolated fixture: incremental must flag memories touching changed paths."""
        tmp2 = tempfile.TemporaryDirectory()
        try:
            repo2 = make_fixture_repo(pathlib.Path(tmp2.name))
            con2 = sqlite3.connect(":memory:")
            con2.row_factory = sqlite3.Row
            from cortex.db import migrate
            migrate(con2)
            con2.execute("""INSERT INTO memories(project_id,scope,title,body_md,source_files_json)
                            VALUES ('fixture','module','M','uses auth','["src/auth.ts"]')""")
            from cortex.indexer import _incremental
            from cortex.discovery import scan_file_tree
            files = scan_file_tree(repo2)
            auth = repo2 / "src" / "auth.ts"
            original = auth.read_text()
            auth.write_text(original + "\n// touch\n")
            _incremental(con2, "fixture", repo2, files, set(files), None, None)
            stale = con2.execute("SELECT stale FROM memories WHERE title='M'").fetchone()[0]
            self.assertEqual(stale, 1)
        finally:
            con2.close()
            tmp2.cleanup()


def indexer_update(con, proj):
    from cortex.indexer import index_project
    return index_project(con, proj, full=False)


class TestMcpServer(unittest.TestCase):
    def test_protocol_roundtrip(self):
        from cortex.mcp_server import handle
        init = handle({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertIn("serverInfo", init["result"])
        tools = handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = {t["name"] for t in tools["result"]["tools"]}
        self.assertIn("cortex_context", names)
        self.assertIn("cortex_impact", names)
        self.assertIn("cortex_architecture", names)
        self.assertIn("cortex_preflight", names)
        context_tool = next(t for t in tools["result"]["tools"]
                            if t["name"] == "cortex_context")
        self.assertEqual(context_tool["inputSchema"]["properties"]["refresh"]["enum"],
                         ["auto", "never", "force"])
        call = handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                       "params": {"name": "cortex_search",
                                  "arguments": {"query": "auth session", "project": "fixture"}}})
        self.assertIn("content", call["result"])

    def test_unknown_tool(self):
        from cortex.mcp_server import handle
        r = handle({"jsonrpc": "2.0", "id": 9, "method": "tools/call",
                    "params": {"name": "nope", "arguments": {}}})
        self.assertIn("error", r)


if __name__ == "__main__":
    unittest.main(verbosity=1)
