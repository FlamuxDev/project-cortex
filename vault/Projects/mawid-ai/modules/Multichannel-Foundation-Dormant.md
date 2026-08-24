---
cortex-generated: true
title: multichannel-foundation-dormant
tags: [module]
---

# Multichannel foundation (dormant)

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `packages/backend/src/channels/,instagram/,messenger/`

purpose: shared Meta webhook plumbing for Messenger/Instagram alongside WhatsApp.
path_prefixes: packages/backend/src/channels/, instagram/, messenger/
key_files: meta-webhook.ts (+test), resolve-org.ts (page_id/instagram_account_id lookup), webhook-verify.ts, readiness.ts (public diagnostics), messenger/client.ts + instagram/client.ts (env-gated, currently not configured)
invariants: meta-channels orchestrator never replies before per-tenant page tokens + App Review land (see ai-meta-channels below); org routing columns exist but no token columns yet (scripts/018_meta_channels.sql)
confidence: high

## Files (10+)

- `apps/web/app/api/instagram/webhook/route.ts`
- `apps/web/app/api/messenger/webhook/route.ts`
- `packages/backend/src/channels/meta-webhook.test.ts`
- `packages/backend/src/channels/meta-webhook.ts`
- `packages/backend/src/channels/readiness.ts`
- `packages/backend/src/channels/resolve-org.ts`
- `packages/backend/src/channels/types.ts`
- `packages/backend/src/channels/webhook-verify.ts`
- `packages/backend/src/instagram/client.ts`
- `packages/backend/src/messenger/client.ts`

## API surface

- `GET hub.challenge`
- `GET hub.verify_token`
- `GET hub.mode`
- `GET /api/instagram/webhook`
- `POST /api/instagram/webhook`
- `GET /api/messenger/webhook`
- `POST /api/messenger/webhook`
