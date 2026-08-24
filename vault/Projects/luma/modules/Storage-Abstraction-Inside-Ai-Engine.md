---
cortex-generated: true
title: storage-abstraction-inside-ai-engine
tags: [module]
---

# storage abstraction inside ai-engine

**Project:** [[luma]] | **Confidence:** inferred | **verified@** `da7bced5651b`
**Owns:** `ai-engine/src/data/`

purpose: single data-access interface making storage a deployment choice; every multi-row atomic unit maps to exactly one port operation.
path_prefixes: ai-engine/src/data/
key_files: src/data/port.js, src/data/backend-data-source.js, src/data/prisma-data-source.js, src/data/http-client.js
entrypoints: getDataSource() from src/data/index.js
responsibilities: CAS ops return booleans instead of throwing (lost races are normal); bearer auth, bounded retries for idempotent calls only.
invariants: one request = one transaction on the backend adapter; `(workerId, leaseGeneration)` fencing token verified on renew/settle to stop zombie workers.
pitfalls: HTTP cannot span transactions — this forces coarse non-CRUD endpoints (documented tradeoff).
confidence: high

## Files (11+)

- `ai-engine/src/data/backend-data-source.js`
- `ai-engine/src/data/backend-data-source.test.js`
- `ai-engine/src/data/errors.js`
- `ai-engine/src/data/http-client.js`
- `ai-engine/src/data/http-client.test.js`
- `ai-engine/src/data/index.js`
- `ai-engine/src/data/index.test.js`
- `ai-engine/src/data/port.js`
- `ai-engine/src/data/prisma-data-source.js`
- `ai-engine/src/data/prisma-data-source.test.js`
- `ai-engine/src/data/test-double.js`

## API surface

- `GET knuth`
- `GET brooks`
- `GET /api/agent-runs`
- `PATCH /api/agent-runs/1`
- `POST /api/agent-messages`
- `GET /api/blueprints/missing`
- `PATCH /api/blueprints/1`
- `GET /api/agent-runs/1`
