---
cortex-generated: true
title: fastify-http-api
tags: [module]
---

# Fastify HTTP API

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `apps/api/`

purpose: serve the versioned REST contract; composition root wiring platform ports to module implementations.
path_prefixes: apps/api/
key_files: apps/api/src/app.ts, src/main.ts, src/health.ts (liveness vs readiness), src/openapi-dump.ts, src/jobs.ts
entrypoints: `pnpm dev:api`; buildApp() exported for integration tests
responsibilities: register pipeline + 22 module route plugins under /api/v1; SCIM at root; publish openapi.json publicly; empty-body-tolerant JSON parser; bodyLimit 5MB rejects oversized ingestion at edge.
invariants: this is the ONLY place knowing both platform and modules (ADR-001); every route declares permission/public/authenticated at boot; trustProxy on; requestIdHeader x-correlation-id.
pitfalls: Fastify default parser rejects empty JSON bodies (custom parser added after activation routes 400'd); logger:false avoids duplicate context-free log lines.
confidence: verified

## Files (19+)

- `apps/api/__tests__/api.int.test.ts`
- `apps/api/__tests__/campaigns.int.test.ts`
- `apps/api/__tests__/cross-tenant-permissions.int.test.ts`
- `apps/api/__tests__/decisioning.int.test.ts`
- `apps/api/__tests__/delivery-idempotency.int.test.ts`
- `apps/api/__tests__/erasure.int.test.ts`
- `apps/api/__tests__/identity.int.test.ts`
- `apps/api/__tests__/ingestion.int.test.ts`
- `apps/api/__tests__/ml.int.test.ts`
- `apps/api/__tests__/profile.int.test.ts`
- `apps/api/__tests__/rate-limiting.int.test.ts`
- `apps/api/__tests__/role-catalogue.int.test.ts`
- `apps/api/__tests__/scim.int.test.ts`
- `apps/api/__tests__/segments.int.test.ts`
- `apps/api/src/app.ts`
- `apps/api/src/health.ts`
- `apps/api/src/jobs.ts`
- `apps/api/src/main.ts`
- `apps/api/src/openapi-dump.ts`

## API surface

- `POST /api/v1/probe`
- `GET churn_probability`
- `GET campaign_response_rate_90d`
- `GET average_order_value`
- `GET days_since_last_purchase`
- `GET complaint_count_30d`
- `GET data_usage_7d`
- `GET revenue_90d`
- `GET revenue_30d`
- `GET /api/v1/openapi.json`
- `GET /ready`
- `GET /health`
- `GET /v1/workspaces/:workspaceId/audit`
- `DELETE /v1/workspaces/:workspaceId/lists/:listId/contacts/:id`
- `PUT /v1/workspaces/:workspaceId/lists/:listId/contacts/:id`
