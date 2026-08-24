---
cortex-generated: true
title: express-rest-service
tags: [module]
---

# Express REST service

**Project:** [[luma]] | **Confidence:** inferred | **verified@** `da7bced5651b`
**Owns:** `backend-luma/src/`

purpose: client-facing API: auth (JWT access+refresh, email verification, password reset), users/roles, admin & superadmin surfaces, blueprints CRUD + retry/cancel, sections, diagrams, agent runs/messages (client view), PDF exports (pdfkit), audit/security logs, SSE event stream, and the fenced `/api/worker/v1` surface.
path_prefixes: backend-luma/src/
key_files: src/app.js, src/loaders/routes.loader.js, src/routes/blueprint.routes.js, src/routes/worker.routes.js, src/services/blueprintEvent.service.js
entrypoints: src/server.js (nodemon/pm2/docker)
responsibilities: validation (express-validator + joi), rate limiting, helmet/CORS/compression, i18n locales, swagger docs, Sequelize migrations/seeders.
invariants: worker surface must not be merged with client-facing endpoints — it carries lease fencing + transactional guarantees (`worker.routes.js:6-11`).
pitfalls: `.env` holds real secrets locally (gitignored); Redis role beyond rate limiting not fully traced [uncertain].
confidence: high

## Files (40+)

- `backend-luma/src/app.js`
- `backend-luma/src/config/config.js`
- `backend-luma/src/config/database.js`
- `backend-luma/src/config/index.js`
- `backend-luma/src/config/logger.js`
- `backend-luma/src/config/postgresClient.js`
- `backend-luma/src/config/swagger.js`
- `backend-luma/src/controllers/admin.controller.js`
- `backend-luma/src/controllers/agent.controller.js`
- `backend-luma/src/controllers/agentMessage.controller.js`
- `backend-luma/src/controllers/agentRun.controller.js`
- `backend-luma/src/controllers/auth.controller.js`
- `backend-luma/src/controllers/blueprint.controller.js`
- `backend-luma/src/controllers/blueprintChat.controller.js`
- `backend-luma/src/controllers/blueprintEvent.controller.js`
- `backend-luma/src/controllers/diagram.controller.js`
- `backend-luma/src/controllers/exportFile.controller.js`
- `backend-luma/src/controllers/passwordReset.controller.js`
- `backend-luma/src/controllers/section.controller.js`
- `backend-luma/src/controllers/superadmin.controller.js`
- `backend-luma/src/controllers/user.controller.js`
- `backend-luma/src/controllers/worker.controller.js`
- `backend-luma/src/loaders/database.loader.js`
- `backend-luma/src/loaders/express.loader.js`
- `backend-luma/src/loaders/routes.loader.js`

## API surface

- `USE /api-docs`
- `USE /api`
- `USE /api/worker/v1`
- `USE /api/agent-messages`
- `USE /api/agent-runs`
- `USE /api/blueprints`
- `USE /api/super-admin`
- `USE /api/admin`
- `USE /api/users`
- `USE /api/auth`
- `GET /health`
- `GET /`
- `GET x-rate-limit-test`
- `GET /blueprints`
- `GET /logs`
