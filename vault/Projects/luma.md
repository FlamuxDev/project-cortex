---
cortex-generated: true
title: luma
tags: [project]
---

# Luma

**Path:** `/home/aboud/Dev/Luma`  
**Kind:** app | **Languages:** .js,.jsx,.mjs,.sql | **Frameworks:** None

**HEAD:** `da7bced5651b` | **Brain:** `da7bced5651b` | FRESH

| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |
|---|---|---|---|---|---|---|---|---|
| 477 | 1324 | 7 | 4 | 362 | 65 | 146 | 9 | 15 (0 stale) |

## Examiner pages
- [[luma/API Surface|API Surface]]
- [[luma/Code Map|Code Map]]
- [[luma/Database|Database]]
- [[luma/Flows|Flows]]
- [[luma/History & Hotspots|History & Hotspots]]
- [[luma/Test Map|Test Map]]

## Pitfalls & rules (memories)
- Historical lessons [verified]
- Risks & technical debt [verified]

## Modules
- [[luma/modules/Agent-Orchestration-Engine|Agent orchestration engine]] — background worker that claims generation jobs, materializes one AgentRun per council agent, executes [inferred]
- [[luma/modules/Evaluation-Benchmarks|evaluation & benchmarks]] — mutation-suite evaluator, injection corpus (prompt-injection resistance), regression runner with run [inferred]
- [[luma/modules/Express-Rest-Service|Express REST service]] — client-facing API: auth (JWT access+refresh, email verification, password reset), users/roles, admin [inferred]
- [[luma/modules/Integration-Boundary-Prompt-Assets|integration boundary + prompt assets]] — machine-readable worker/backend contract and versioned prompt blocks/checks/drafts for the agent cou [inferred]
- [[luma/modules/React-Client|React client]] — landing page, auth flows (register/login/verify/reset), workspace dashboard, live blueprint creation [inferred]
- [[luma/modules/Shared-Postgresql-Schema|shared PostgreSQL schema]] — canonical platform schema owned by BE team; ai-engine keeps a runnable worker-scoped subset (`ai-eng [inferred]
- [[luma/modules/Storage-Abstraction-Inside-Ai-Engine|storage abstraction inside ai-engine]] — single data-access interface making storage a deployment choice; every multi-row atomic unit maps to [inferred]

## Flows
- **Blueprint generation (end-to-end)** — user submits idea on /new-blueprint (frontend) → POST /api/blueprints creates Blueprint (+BlueprintSettings) and a `gene
- **Live progress streaming (SSE)** — frontend opens EventSource on GET /api/blueprints/:id/events after starting generation.
- **Stale-job recovery** — worker heartbeat/lease expiry or explicit recover endpoint.
- **Auth lifecycle** — register/login/logout, refresh tokens, email verify, password reset.

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- luma: overview [verified]
- Tests & commands [verified]
