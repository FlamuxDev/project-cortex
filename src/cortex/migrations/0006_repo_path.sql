-- Code may live in a subdirectory of a wrapper project directory.
-- Discovery computed repo_path but never persisted it, so every consumer resolved
-- file paths and git state against the project dir and silently missed.
ALTER TABLE projects ADD COLUMN repo_path TEXT;
UPDATE projects SET repo_path = path WHERE repo_path IS NULL;
