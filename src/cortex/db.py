"""SQLite database layer with migration runner."""
import sqlite3, pathlib, os

MIGRATIONS_DIR = pathlib.Path(__file__).parent / "migrations"
# Legacy location: the DB used to live inside the source checkout. That breaks
# `pipx install` (the brain lands inside the venv and dies on upgrade), so the
# default is now the per-user state dir — legacy paths are still honoured below.
LEGACY_DB = pathlib.Path(__file__).resolve().parents[2] / "data" / "cortex.db"


def cortex_home() -> pathlib.Path:
    """Per-user state dir: data/ + config.json. Override with CORTEX_HOME."""
    return pathlib.Path(os.environ.get("CORTEX_HOME", "~/.cortex")).expanduser()


def _is_populated(p: pathlib.Path) -> bool:
    """True if this file is a cortex brain with at least one indexed project."""
    if not p.exists():
        return False
    try:
        con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
        try:
            return con.execute("SELECT COUNT(*) FROM projects").fetchone()[0] > 0
        finally:
            con.close()
    except sqlite3.Error:  # missing table, not a DB, unreadable
        return False


def default_db() -> pathlib.Path:
    """Resolve the brain path: explicit env > user state dir > legacy checkout.

    A bare `cortex` call auto-creates an empty DB at the home path, so emptiness —
    not absence — is what must not shadow a populated pre-0.3 checkout brain.
    """
    env = os.environ.get("CORTEX_DATA_DIR")
    if env:
        return pathlib.Path(env).expanduser()
    home_db = cortex_home() / "data" / "cortex.db"
    if not _is_populated(home_db) and _is_populated(LEGACY_DB):
        return LEGACY_DB
    return home_db


def connect(db_path: pathlib.Path | str | None = None) -> sqlite3.Connection:
    p = pathlib.Path(db_path or default_db())
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA busy_timeout=30000")
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    migrate(con)
    return con


def migrate(con: sqlite3.Connection):
    con.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, applied_at TEXT DEFAULT (datetime('now')))"
    )
    done = {r[0] for r in con.execute("SELECT version FROM schema_migrations")}
    for f in sorted(MIGRATIONS_DIR.glob("*.sql")):
        version = int(f.stem.split("_")[0])
        if version in done:
            continue
        con.executescript(f.read_text())
        con.execute("INSERT INTO schema_migrations(version) VALUES (?)", (version,))
        con.commit()


def code_root(project_row) -> str:
    """Directory the project's indexed file paths are relative to.

    Usually the project dir, but code may sit in a subdirectory (repo_path).
    Falls back to path for rows written before migration 0006.
    """
    try:
        return project_row["repo_path"] or project_row["path"]
    except (IndexError, KeyError):
        return project_row["path"]


def state_get(con, key, default=None):
    row = con.execute("SELECT value FROM index_state WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def state_set(con, key, value):
    con.execute(
        "INSERT INTO index_state(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )
    con.commit()
