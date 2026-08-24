---
cortex-generated: true
title: shared-types-ci-deploy-tooling
tags: [module]
---

# Shared types, CI, deploy tooling

**Project:** [[chat-agent-saas]] | **Confidence:** verified | **verified@** `d5c6955acca7`
**Owns:** `packages/shared/src/,deploy/lib/,scripts/,.github/workflows/,ecosystem.config.cjs,deploy.sh`

purpose: cross-package constants/types (systemConfigKeys.ts, ORG_FEATURE_CATALOG); deploy scripts with guardrails.
path_prefixes: packages/shared/src/, deploy/lib/, scripts/, .github/workflows/, ecosystem.config.cjs, deploy.sh
key_files: shared/src/systemConfigKeys.ts, deploy/lib/{migration-guard,snapshot,health-check}.sh, scripts/logs.sh, scripts/eval-*.{mjs,cjs} (production eval harnesses), eslint flat config
entrypoints: npm scripts at root; bash scripts/logs.sh streams PM2 logs over SSH.
responsibilities: turbo task graph; CI quality job (pgvector+Redis services → prisma db push → turbo build lint test → test:e2e step) + docker build-only on master; manual deploys ship prebuilt artifacts with DROP-refusing migration guard, pre-deploy pg_dump snapshot, /api/ready health poll + rollback.
invariants: deploy.sh does NOT build (step-0 guard) nor install new deps on the server; SKIP_* env knobs documented bypasses.
pitfalls: turbo strict env needs globalPassThroughEnv entries (19b1df4); docker must copy prisma schema before npm ci (postinstall generates client — b538fcf).
confidence: verified

## Files (40+)

- `ecosystem.config.cjs`
- `packages/api/prisma/scripts/apply-preset.cjs`
- `packages/api/prisma/scripts/apply-preset.ts`
- `packages/api/prisma/scripts/create-platform-admin.ts`
- `packages/api/prisma/scripts/fix-domain.ts`
- `packages/api/prisma/scripts/init-ai-models.ts`
- `packages/api/prisma/scripts/inventory-drift.cjs`
- `packages/api/prisma/scripts/update-webhook-urls.ts`
- `packages/api/prisma/scripts/update-webhooks.ts`
- `packages/api/scripts/backfill-integrations.ts`
- `packages/api/scripts/copy-static-assets.js`
- `packages/api/scripts/dynatrace-demo.ts`
- `packages/api/scripts/enable-voice-custom-llm.ts`
- `packages/api/scripts/eval/rag-eval.ts`
- `packages/api/scripts/migrate-meta-byoa-to-embedded-signup.ts`
- `packages/api/scripts/splunk-demo.ts`
- `packages/api/scripts/verify-chatpath-prod.js`
- `packages/api/scripts/verify-identity-prod.js`
- `packages/shared/src/constants/index.ts`
- `packages/shared/src/constants/integrationCatalog.ts`
- `packages/shared/src/constants/models.ts`
- `packages/shared/src/constants/orgDefaults.ts`
- `packages/shared/src/constants/orgFeatures.ts`
- `packages/shared/src/constants/permissions.test.ts`
- `packages/shared/src/constants/permissions.ts`
