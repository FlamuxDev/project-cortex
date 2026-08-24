-- migrate: contentless fts -> regular fts (DELETE support)
DROP TABLE IF EXISTS fts_symbols;
DROP TABLE IF EXISTS fts_memories;
DROP TABLE IF EXISTS fts_files;
CREATE VIRTUAL TABLE fts_symbols USING fts5(name, sig, doc, path);
CREATE VIRTUAL TABLE fts_memories USING fts5(title, body);
CREATE VIRTUAL TABLE fts_files USING fts5(path);
