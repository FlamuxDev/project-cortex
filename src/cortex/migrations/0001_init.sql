-- Project Cortex schema v1
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS schema_migrations (
  version INTEGER PRIMARY KEY,
  applied_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY,                -- slug e.g. 'myapp'
  name TEXT NOT NULL,
  path TEXT NOT NULL UNIQUE,
  kind TEXT,                          -- monorepo|app|service|library|scripts|docs
  languages TEXT,                     -- csv of top langs
  frameworks TEXT,                    -- csv
  package_managers TEXT,
  git_head TEXT,                      -- HEAD at last full index
  indexed_commit TEXT,                -- commit the brain is verified against
  dirty_files INTEGER DEFAULT 0,
  last_indexed_at TEXT,
  status TEXT DEFAULT 'active'        -- active|archived|error
);

CREATE TABLE IF NOT EXISTS files (
  project_id TEXT NOT NULL REFERENCES projects(id),
  path TEXT NOT NULL,                 -- relative to project root
  lang TEXT,
  ext TEXT,
  loc INTEGER DEFAULT 0,
  hash TEXT,                          -- sha1 of content at index time
  importance REAL DEFAULT 0.0,
  is_test INTEGER DEFAULT 0,
  is_entry INTEGER DEFAULT 0,
  PRIMARY KEY (project_id, path)
);
CREATE INDEX IF NOT EXISTS idx_files_lang ON files(project_id, lang);

CREATE TABLE IF NOT EXISTS symbols (
  id INTEGER PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id),
  path TEXT NOT NULL,
  name TEXT NOT NULL,
  kind TEXT NOT NULL,                 -- function|method|class|interface|type|struct|const|route|component
  parent TEXT,
  line_start INTEGER, line_end INTEGER,
  signature TEXT,
  doc TEXT,
  exported INTEGER DEFAULT 0,
  importance REAL DEFAULT 0.0
);
CREATE INDEX IF NOT EXISTS idx_sym_proj_name ON symbols(project_id, name);
CREATE INDEX IF NOT EXISTS idx_sym_path ON symbols(project_id, path);

CREATE TABLE IF NOT EXISTS refs (        -- symbol-level edges from static analysis + import graph
  project_id TEXT NOT NULL,
  src_path TEXT NOT NULL,             -- file containing the reference
  src_symbol TEXT,                    -- qualified name or NULL=file-level
  dst_name TEXT NOT NULL,             -- referenced identifier / module spec
  dst_path TEXT,                      -- resolved target file if known
  kind TEXT NOT NULL,                 -- import|call|extends|implements|use
  line INTEGER
);
CREATE INDEX IF NOT EXISTS idx_refs_src ON refs(project_id, src_path);
CREATE INDEX IF NOT EXISTS idx_refs_dst ON refs(project_id, dst_path);
CREATE INDEX IF NOT EXISTS idx_refs_name ON refs(project_id, dst_name);

CREATE TABLE IF NOT EXISTS modules (
  id TEXT PRIMARY KEY,                -- '<project>:<module-slug>'
  project_id TEXT NOT NULL,
  name TEXT NOT NULL,
  slug TEXT NOT NULL,
  path_prefixes TEXT,                 -- csv of dirs owned
  purpose TEXT,
  body_md TEXT,                       -- compact module memory (yaml+md)
  confidence TEXT DEFAULT 'inferred', -- verified|strongly_inferred|inferred|uncertain
  verified_at_commit TEXT,
  updated_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS module_files (
  module_id TEXT NOT NULL REFERENCES modules(id),
  project_id TEXT NOT NULL,
  path TEXT NOT NULL,
  PRIMARY KEY (module_id, path)
);

CREATE TABLE IF NOT EXISTS apis (
  id INTEGER PRIMARY KEY,
  project_id TEXT NOT NULL,
  method TEXT, route TEXT,
  handler_path TEXT, handler_symbol TEXT,
  auth TEXT, notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_apis_proj ON apis(project_id);

CREATE TABLE IF NOT EXISTS db_entities (
  id INTEGER PRIMARY KEY,
  project_id TEXT NOT NULL,
  name TEXT NOT NULL,
  kind TEXT,                          -- table|view|type|function|migration|bucket|queue|vector_store
  file_path TEXT,
  summary TEXT,
  columns_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_db_proj ON db_entities(project_id, name);

CREATE TABLE IF NOT EXISTS tests (
  id INTEGER PRIMARY KEY,
  project_id TEXT NOT NULL,
  path TEXT NOT NULL,
  name TEXT,
  kind TEXT,                          -- unit|integration|e2e
  targets_json TEXT                   -- [{path|symbol}] code under test
);

CREATE TABLE IF NOT EXISTS flows (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  name TEXT NOT NULL,
  trigger TEXT,
  steps_md TEXT,
  files_json TEXT,
  confidence TEXT DEFAULT 'inferred'
);

CREATE TABLE IF NOT EXISTS memories (
  id INTEGER PRIMARY KEY,
  project_id TEXT,                    -- NULL = global memory
  scope TEXT NOT NULL,                -- project|module|architecture|business_rule|pitfall|integration|global
  title TEXT NOT NULL,
  body_md TEXT NOT NULL,
  confidence TEXT DEFAULT 'inferred',
  origin TEXT DEFAULT 'generated',    -- generated|delegate|curated|user|git
  source_files_json TEXT,             -- provenance
  evidence_json TEXT,                 -- [{type:path|test|commit, ref}]
  verified_at_commit TEXT,
  stale INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_mem_proj ON memories(project_id, scope);

CREATE TABLE IF NOT EXISTS decisions (
  id INTEGER PRIMARY KEY,
  project_id TEXT,
  title TEXT NOT NULL,
  context TEXT, decision TEXT, consequences TEXT,
  date TEXT, commit_sha TEXT, source TEXT, confidence TEXT DEFAULT 'inferred'
);

CREATE TABLE IF NOT EXISTS episodes (
  id INTEGER PRIMARY KEY,
  project_id TEXT,
  task TEXT NOT NULL, problem TEXT, root_cause TEXT,
  files_modified_json TEXT, solution TEXT, failed_approaches TEXT,
  lessons TEXT, commit_sha TEXT, created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS commits (
  project_id TEXT NOT NULL,
  sha TEXT NOT NULL,
  date TEXT, author TEXT, subject TEXT,
  category TEXT,                     -- fix|feat|refactor|migration|revert|chore|perf|docs
  PRIMARY KEY (project_id, sha)
);
CREATE TABLE IF NOT EXISTS commit_files (
  project_id TEXT NOT NULL, sha TEXT NOT NULL, path TEXT NOT NULL,
  PRIMARY KEY (project_id, sha, path)
);
CREATE INDEX IF NOT EXISTS idx_cf_path ON commit_files(project_id, path);

CREATE TABLE IF NOT EXISTS index_state (
  key TEXT PRIMARY KEY,
  value TEXT
);

-- FTS
CREATE VIRTUAL TABLE IF NOT EXISTS fts_symbols USING fts5(name, sig, doc, path);
CREATE VIRTUAL TABLE IF NOT EXISTS fts_memories USING fts5(title, body);
CREATE VIRTUAL TABLE IF NOT EXISTS fts_files USING fts5(path);
