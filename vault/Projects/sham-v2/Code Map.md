---
cortex-generated: true
title: sham-v2 code map
tags: [codemap/project]
---

# sham-v2 — Code Map

## Directory layout (indexed files)

- `src/` — 53 files
- `test/` — 12 files
- `scripts/` — 3 files
- `ecosystem.config.cjs/` — 1 files
- `eslint.config.js/` — 1 files
- `storage/` — 1 files

## Entry points

- `src/agent/index.js`
- `src/server.js`

## Most-connected symbols (fan-in leaders)

| Symbol | Kind | Location |
|---|---|---|
| `inc` | function | `src/core/metrics.js:10` |
| `validateSql` | function | `src/agent/guard.js:317` |
| `advanceGuidedSchool` | function | `src/agent/guided.js:277` |
| `detectEntityKey` | function | `src/agent/clarify.js:30` |
| `normalizeText` | function | `src/core/arabic.js:21` |
| `decideClarification` | function | `src/agent/clarify.js:72` |
| `detectRankingIntent` | function | `src/agent/ranking.js:109` |
| `toJson` | function | `src/db/catalog.js:65` |
| `toJson` | function | `src/runtime/db.js:205` |
| `renderAnswer` | function | `src/agent/render.js:109` |
| `repairHint` | function | `src/agent/guard.js:450` |
| `isApiGuidedSchoolRequest` | function | `src/agent/index.js:212` |
| `renderOutOfScope` | function | `src/agent/render.js:183` |
| `request` | function | `src/integrations/shamsi-admin.js:91` |
| `transition` | function | `src/runtime/workflow-engine.js:171` |
| `startGuidedSchool` | function | `src/agent/guided.js:269` |
| `verifyTextGrounded` | function | `src/agent/humanize.js:164` |
| `normalizePhone` | function | `src/core/phone.js:2` |
| `fromJson` | function | `src/db/catalog.js:66` |
| `fromJson` | function | `src/runtime/db.js:213` |
| `isGuidedSchoolIntent` | function | `src/agent/guided.js:329` |
| `serializeGuidedSchoolState` | function | `src/agent/guided.js:309` |
| `ask` | function | `src/agent/index.js:350` |
| `buildRankingSql` | function | `src/agent/ranking.js:192` |
| `enqueue` | function | `src/runtime/outbox.js:43` |
| `runSql` | function | `src/agent/execute.js:130` |
| `deserializeGuidedSchoolState` | function | `src/agent/guided.js:314` |
| `renderFailure` | function | `src/agent/render.js:213` |
| `renderClarification` | function | `src/agent/render.js:204` |
| `classifyColumn` | function | `src/db/semantics.js:79` |

## Highest-importance files

- `src/sync/import-backup.js` (484 loc)
- `src/app.js` (83 loc)
- `src/config/env.js` (128 loc)
- `src/config/logger.js` (48 loc)
- `src/agent/index.js` (587 loc)
- `src/db/semantics.js` (919 loc)
- `src/agent/guard.js` (519 loc)
- `src/core/metrics.js` (63 loc)
- `src/db/schema.js` (466 loc)
- `src/core/arabic.js` (47 loc)
- `src/db/mirror.js` (373 loc)
- `src/agent/render.js` (221 loc)
- `src/db/catalog.js` (165 loc)
- `src/agent/clarify.js` (91 loc)
- `src/channels/http/middlewares.js` (93 loc)
- `src/core/sql-functions.js` (50 loc)
- `src/runtime/db.js` (225 loc)
- `src/server.js` (85 loc)
- `src/agent/execute.js` (187 loc)
- `src/agent/guided.js` (338 loc)
- `src/channels/whatsapp/delivery.js` (64 loc)
- `src/channels/whatsapp/webhook.js` (56 loc)
- `src/runtime/outbox.js` (148 loc)
- `src/runtime/sessions.js` (199 loc)
- `src/agent/prompt.js` (175 loc)