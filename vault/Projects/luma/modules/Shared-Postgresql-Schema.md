---
cortex-generated: true
title: shared-postgresql-schema
tags: [module]
---

# shared PostgreSQL schema

**Project:** [[luma]] | **Confidence:** inferred | **verified@** `da7bced5651b`
**Owns:** `backend-luma/src/models/,backend-luma/src/migrations/,ai-engine/prisma/`

purpose: canonical platform schema owned by BE team; ai-engine keeps a runnable worker-scoped subset (`ai-engine/prisma/schema.prisma` header, Arabic comments).
path_prefixes: backend-luma/src/models/, backend-luma/src/migrations/, ai-engine/prisma/
key_files: ai-engine/prisma/schema.prisma, ai-engine/prisma/migrations/*/migration.sql (5), luma_backup.sql
entrypoints: `db:migrate*` scripts both sides
responsibilities: entities documented under DATABASE below; CHECK constraints added by manual BE migrations where Prisma can't express them.
invariants: migration history must never be gitignored again (see GIT LESSONS, 40632ac).
pitfalls: `blueprint_sections.status` model default `"completed"` is rejected by the DB CHECK (`generated|edited|approved`) — latent trap documented in schema.prisma:172-176.
confidence: high

## Files (40+)

- `ai-engine/prisma/migrations/20260801133000_baseline/migration.sql`
- `ai-engine/prisma/migrations/20260802105804_lease_ownership_fencing/migration.sql`
- `ai-engine/prisma/migrations/20260803120000_agent_run_generation_job_attribution/migration.sql`
- `ai-engine/prisma/migrations/20260804063600_blueprint_waiting_for_review_status/migration.sql`
- `ai-engine/prisma/migrations/20260805090000_align_with_backend_schema/migration.sql`
- `ai-engine/prisma/schema.prisma`
- `ai-engine/prisma/seed-drill.mjs`
- `ai-engine/prisma/seed.js`
- `backend-luma/src/migrations/20260726113447-create-user.js`
- `backend-luma/src/migrations/20260726124442-create-refresh-token.js`
- `backend-luma/src/migrations/20260727064331-create-role.js`
- `backend-luma/src/migrations/20260727064912-add-role-id-to-users.js`
- `backend-luma/src/migrations/20260727084733-add-deleted-at-to-users.js`
- `backend-luma/src/migrations/20260727084928-add-is-active-to-users.js`
- `backend-luma/src/migrations/20260729072002-create-notification.js`
- `backend-luma/src/migrations/20260729081443-create-system-settings.js`
- `backend-luma/src/migrations/20260729081707-create-audit-logs.js`
- `backend-luma/src/migrations/20260729082125-create-blueprints.js`
- `backend-luma/src/migrations/20260729082839-update-blueprints-table.js`
- `backend-luma/src/migrations/20260729083314-create-blueprint-settings.js`
- `backend-luma/src/migrations/20260729085543-create-export-file.js`
- `backend-luma/src/migrations/20260729090140-create-agent-definition.js`
- `backend-luma/src/migrations/20260729090801-create-agent-run.js`
- `backend-luma/src/migrations/20260729091010-create-blueprint-sections.js`
- `backend-luma/src/migrations/20260729091107-create-agent-message.js`
