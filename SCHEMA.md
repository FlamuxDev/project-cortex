# Schema

SQLite, migrations in `src/cortex/migrations/`, applied automatically on connect.

## Entity overview

| Table | Purpose | Key columns |
|---|---|---|
| `projects` | indexed repos | id, path, kind, languages, git_head, **indexed_commit**, dirty_files |
| `files` | every code file | (project_id,path) PK, lang, loc, **hash** (sha1@index), importance, is_test, is_entry |
| `symbols` | classes/functions/methods/components/routes/sql-objects | name, kind, parent, line range, signature†, doc†, exported, importance |
| `refs` | edges: import / call / use | src_path → dst_name (+resolved dst_path), kind, line |
| `modules` | module memories | slug, path_prefixes, purpose, body_md, confidence, verified_at_commit |
| `module_files` | module→file ownership | from path_prefixes at ingest time |
| `apis` | HTTP surface | method, route, handler_path/symbol, direction(server/client) |
| `db_entities` | tables/views/types/policies/buckets | name, kind, file_path |
| `tests` | test files + targets | kind(unit/integration/e2e), targets_json (imports-derived) |
| `flows` | end-to-end product flows | trigger, steps_md, files_json, confidence |
| `memories` | the semantic brain | scope(project/module/architecture/pitfall/history/business_rule/global/uncertain), body_md†, confidence, origin(delegate/curated/generated), source_files_json†, verified_at_commit, **stale** flag |
| `decisions` | ADR-like entries | title/context/consequences, commit_sha, source |
| `episodes` | task post-mortems (schema ready, fed by future use) | task/problem/root_cause/files/solution/lessons/commit |
| `commits`,`commit_files` | mined history | sha, date, subject†, category(fix/feat/…) + per-file mapping |
| `fts_symbols`,`fts_files`,`fts_memories` | FTS5 indexes | rebuilt per-project on index; memories wholesale |

† secret-redacted on insert (`langs.redact`).

## Freshness contract

```
projects.git_head        HEAD at last index run
projects.indexed_commit  commit the brain is verified against
files.hash               content hash — incremental update diffs this
memories.stale           set when evidence/source paths change after ingest
live query               recomputes HEAD/dirty/behind-count via git at call time
```

## Migrations

0001 initial schema · 0002 FTS5 contentless→regular (DELETE support) · 0003 apis.direction.
Runner: `cortex.db.migrate()` — numbered files, tracked in `schema_migrations`.
