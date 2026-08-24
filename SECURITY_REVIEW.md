# Security Review

**Scope:** Project Cortex itself and its effect on the indexed repositories. Date: 2026-08-25.

## Threat model

Cortex is a local, single-user, read-only-over-repos system. Main risks:
secrets entering the knowledge base; cortex files leaking repo content; cortex being used
as an unintended write path into projects.

## Controls in place

1. **Secret redaction at insert time.** Every signature, docstring, commit subject, report body
   and memory passes `cortex.langs.redact()` before touching SQLite: API keys (`sk-…`), AWS keys,
   GitHub tokens/PATs, JWTs, PEM private key blocks, `password/secret/api_key/token = "…"` pairs,
   long base64 blobs → `***REDACTED***`. Tests assert this (`tests/test_cortex.py::test_redaction`).
2. **`~/Dev/pems` excluded at discovery.** A directory of SSH private keys sits next to the
   projects; it is hard-excluded (`discovery.EXCLUDED`) and never scanned.
3. **Read-only against projects.** The indexer opens files for reading and runs `git log/status/
   rev-parse`. No writes, no formatting, no dependency changes, no commits in project repos.
   Delegates were instructed read-only and confirmed compliance.
4. **No network.** Everything local: SQLite, tree-sitter, git, ripgrep.
5. **Generated-vault hygiene.** Vault notes are markdown derived from the same redacted DB;
   regeneration never overwrites non-cortex (human) files.
6. **Env var names, not values.** Reports/config references store names like
   `Requires DATABASE_URL`; values were never ingested (delegate instructions + redaction net).

## Residual risks (accepted, documented)

- Commit messages authored before this system could contain secrets; they pass through the same
  redaction, but regexes are not proof against novel formats. DB file itself lives in
  `~/project-cortex/data/` with normal user-file permissions — treat it as sensitive as your repos.
- `.env` files are not code extensions so they're not indexed; if a secret leaked into a source
  *string* it would still hit the redaction patterns above.
- MCP server binds stdio only — no network surface.

## Verification

```bash
cd ~/project-cortex && .venv/bin/python -m unittest tests.test_cortex.TestLangs.test_redaction
rg -l "sk-[A-Za-z0-9]{20}" data/cortex.db || echo "no raw api keys found"
```

(If you ever suspect contamination: delete `data/cortex.db*` and rebuild — everything is
regenerable from repos + reports.)
