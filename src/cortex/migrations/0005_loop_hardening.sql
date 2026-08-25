-- Learning loop hardening: dirty-at-start snapshot + file content terms
ALTER TABLE task_sessions ADD COLUMN dirty_at_start_json TEXT;

DROP TABLE IF EXISTS fts_files;
CREATE VIRTUAL TABLE fts_files USING fts5(path, terms);
