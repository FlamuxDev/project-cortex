---
cortex-generated: true
title: sham-v2
tags: [project]
---

# sham-v2

**Path:** `/home/aboud/Dev/sham-v2`  
**Kind:** app | **Languages:** .js,.cjs,.sql | **Frameworks:** None

**HEAD:** `71fbe7ede70c` | **Brain:** `71fbe7ede70c` | FRESH

| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |
|---|---|---|---|---|---|---|---|---|
| 71 | 516 | 7 | 4 | 38 | 93 | 12 | 7 | 15 (0 stale) |

## Examiner pages
- [[sham-v2/API Surface|API Surface]]
- [[sham-v2/Code Map|Code Map]]
- [[sham-v2/Database|Database]]
- [[sham-v2/Flows|Flows]]
- [[sham-v2/History & Hotspots|History & Hotspots]]
- [[sham-v2/Test Map|Test Map]]

## Pitfalls & rules (memories)
- Historical lessons [verified]
- Risks & technical debt [verified]

## Modules
- [[sham-v2/modules/Api-Surface|API surface]] — thin REST adapter; session hygiene; admin-only SQL disclosure. [inferred]
- [[sham-v2/modules/Ask-Pipeline|ask() pipeline]] — one path from any channel's question to a grounded Arabic answer. [inferred]
- [[sham-v2/modules/Catalog-Generations-Semantic-Layer|catalog generations & semantic layer]] — build immutable readonly SQLite catalogs from PGDMP backups; describe every column to the model. [inferred]
- [[sham-v2/modules/Meta-Webhook-Queue-Worker|Meta webhook + queue worker]] — receive, dedupe, and answer WhatsApp traffic; media/voice support. [inferred]
- [[sham-v2/modules/Pgdmp-Import-Pipeline-Accuracy-Harness|PGDMP import pipeline & accuracy harness]] — rebuild catalogs from S3-fetched backups nightly; measure answer correctness continuously. [inferred]
- [[sham-v2/modules/Query-Validation-Sandboxed-Execution|query validation & sandboxed execution]] — reject unsafe/wrong SQL before execution; run it isolated. [inferred]
- [[sham-v2/modules/Sessions-Workflows-Outbox|sessions, workflows, outbox]] — everything that must survive catalog swaps, in its own WAL SQLite DB. [inferred]

## Flows
- **API chat question** — POST /api/chat {message, session_id?, allow_contact?, user?}.
- **WhatsApp inbound message** — Meta webhook POST.
- **Catalog sync / generation swap** — cron scheduler pulls PGDMP backup (or manual `npm run sync`).
- **Guided school search (API only)** — parent mentions child + school intent (regex-gated, index.js:208-215).

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- sham-v2: overview [verified]
- Tests & commands [verified]
