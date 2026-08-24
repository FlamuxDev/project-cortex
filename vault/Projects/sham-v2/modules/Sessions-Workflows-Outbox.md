---
cortex-generated: true
title: sessions-workflows-outbox
tags: [module]
---

# sessions, workflows, outbox

**Project:** [[sham-v2]] | **Confidence:** inferred | **verified@** `71fbe7ede70c`
**Owns:** `src/runtime/`

purpose: everything that must survive catalog swaps, in its own WAL SQLite DB.
path_prefixes: src/runtime/
key_files: runtime/db.js:30-141 (schema v1: sessions w/ optimistic revision counter, user_profiles, inbound_events, delivery_outbox, workflow_instances+workflow_events append-only audit); db.js:143-197 (additive repeatable migrations — add-missing-columns only, never drop); workflow-engine.js / teacher-verification.js / institution-verification.js
entrypoints: imported by server shutdown (saveAllSessions) and both workers
responsibilities: state derived from event history so audits answer "why did this instance reach this state"
invariants: catalog DB and runtime DB are separate files by design (runtime/db.js:1-15)
pitfalls: no data migration story across environments except manual SQLite copy after stop (documented in header comment)
confidence: high

## Files (7+)

- `src/runtime/db.js`
- `src/runtime/institution-verification.js`
- `src/runtime/outbox.js`
- `src/runtime/sessions.js`
- `src/runtime/teacher-verification.js`
- `src/runtime/workflow-engine.js`
- `src/runtime/workflows.js`
