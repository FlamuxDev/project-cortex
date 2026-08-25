-- Learning loop: task sessions, episode lifecycle, provenance
ALTER TABLE memories ADD COLUMN derived_from TEXT;          -- e.g. episode:12
ALTER TABLE memories ADD COLUMN status TEXT DEFAULT 'active'; -- active|superseded|obsolete|uncertain

CREATE TABLE IF NOT EXISTS task_sessions (
  id INTEGER PRIMARY KEY,
  project_id TEXT,
  task TEXT NOT NULL,
  started_at TEXT DEFAULT (datetime('now')),
  start_head TEXT,                    -- git HEAD when task started
  brain_freshness TEXT,               -- fresh|behind|dirty|no_git at start
  context_chars INTEGER,
  files_suggested_json TEXT,          -- primary files returned by context
  symbols_suggested_json TEXT,
  tests_suggested_json TEXT,
  impact_queries_json TEXT,           -- [{target, risk, ts}]
  files_touched_json TEXT,            -- filled at completion (git diff)
  outcome TEXT,                       -- implemented|tested|verified|failed|abandoned|partial
  end_head TEXT,
  completed_at TEXT,
  episode_id INTEGER REFERENCES episodes(id),
  metrics_json TEXT                   -- precision/recall/hit rates computed at completion
);

CREATE TABLE IF NOT EXISTS session_events (
  id INTEGER PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES task_sessions(id),
  kind TEXT NOT NULL,                 -- context|impact|update|complete
  detail TEXT,                        -- redacted target/args summary
  created_at TEXT DEFAULT (datetime('now'))
);

-- Episode lifecycle columns
ALTER TABLE episodes ADD COLUMN status TEXT DEFAULT 'active';      -- active|superseded|obsolete|uncertain
ALTER TABLE episodes ADD COLUMN outcome TEXT;                      -- implemented|tested|verified|failed|abandoned|partial
ALTER TABLE episodes ADD COLUMN confidence TEXT DEFAULT 'inferred';-- verified|strongly_inferred|inferred
ALTER TABLE episodes ADD COLUMN module_slugs_json TEXT;
ALTER TABLE episodes ADD COLUMN symbols_json TEXT;
ALTER TABLE episodes ADD COLUMN apis_json TEXT;
ALTER TABLE episodes ADD COLUMN db_entities_json TEXT;
ALTER TABLE episodes ADD COLUMN tests_run_json TEXT;
ALTER TABLE episodes ADD COLUMN invariants_json TEXT;
ALTER TABLE episodes ADD COLUMN pitfalls_json TEXT;
ALTER TABLE episodes ADD COLUMN evidence_files_json TEXT;
ALTER TABLE episodes ADD COLUMN parent_sha TEXT;
ALTER TABLE episodes ADD COLUMN superseded_by INTEGER REFERENCES episodes(id);
ALTER TABLE episodes ADD COLUMN session_id INTEGER REFERENCES task_sessions(id);
ALTER TABLE episodes ADD COLUMN metrics_json TEXT;

-- regular contentful FTS so episodes can be deleted/updated (see 0002 lesson)
CREATE VIRTUAL TABLE IF NOT EXISTS fts_episodes USING fts5(task, problem, root_cause, solution, lessons);
