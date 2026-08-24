"""SQLite database layer with migration runner."""
import sqlite3, pathlib, importlib.resources

MIGRATIONS_DIR = pathlib.Path(__file__).parent / "migrations"
CORTEX_ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_DB = CORTEX_ROOT / "data" / "cortex.db"


def connect(db_path: pathlib.Path | str | None = None) -> sqlite3.Connection:
    p = pathlib.Path(db_path or DEFAULT_DB)
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA journal_mode=WAL")
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


def state_get(con, key, default=None):
    row = con.execute("SELECT value FROM index_state WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def state_set(con, key, value):
    con.execute(
        "INSERT INTO index_state(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )
    con.commit()
