---
cortex-generated: true
title: connectors-ingestion-mapping-quality-identity-resolution
tags: [module]
---

# Connectors, ingestion, mapping, quality, identity resolution

**Project:** [[telvora]] | **Confidence:** verified | **verified@** `7423f040ed46`
**Owns:** `services/core-api/internal/{integrations,ingestion,mapping,dataquality,identity,telecom/simulator}`

purpose: get external telecom data in, map to canonical schema, quarantine bad rows, score quality, resolve duplicate identities
path_prefixes: services/core-api/internal/{integrations,ingestion,mapping,dataquality,identity,telecom/simulator}
key_files: internal/ingestion/{batch,api_pull,webhook,stream,worker,queue,rawstore,idempotency,retention,ssrf_guard}.go; internal/mapping/engine.go + engine_domains.go (8 source domains); internal/identity/{matching,merge,levenshtein}.go; internal/dataquality/{scores,detect via handler}.go; internal/telecom/simulator/generator.go (proven at 1M profiles)
entrypoints: POST integrations/{id}/batch|pull, public POST /api/v1/webhooks/{connectorId}, mapping dry-run/run, identity run-matching
responsibilities: idempotent batch/API/webhook/stream ingestion with DLQ + replay; versioned field mappings with dry-run; golden-record candidate preview/approve/reject with reversible merges; trust-rank policies per source; lineage graph
invariants: duplicate/replayed input is idempotent; malformed rows quarantine, never poison a run; a job without resolvable tenant is hard failure (ADR-002 §3)
pitfalls: SSRF guard is load-bearing for api_pull — do not bypass; simulator wipe is destructive (dedicated wipe.go + permission)
confidence: verified

## Files (40+)

- `apps/web/src/app/(protected)/[locale]/app/customers/identity-resolution/candidates/[id]/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/customers/identity-resolution/merges/[id]/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/customers/identity-resolution/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/integrations/[id]/mapping/page.tsx`
- `apps/web/src/app/api/tenant/identity/candidates/[id]/approve/route.ts`
- `apps/web/src/app/api/tenant/identity/candidates/[id]/reject/route.ts`
- `apps/web/src/app/api/tenant/identity/merges/[id]/reverse/route.ts`
- `apps/web/src/app/api/tenant/identity/run-matching/route.ts`
- `apps/web/src/app/api/tenant/integrations/[id]/mapping/dry-run/route.ts`
- `apps/web/src/app/api/tenant/integrations/[id]/mapping/run/route.ts`
- `apps/web/src/app/api/tenant/integrations/[id]/mapping/versions/[versionId]/activate/route.ts`
- `apps/web/src/app/api/tenant/integrations/[id]/mapping/versions/route.ts`
- `apps/web/src/lib/dataQuality.ts`
- `apps/web/src/lib/identity.ts`
- `apps/web/src/lib/mapping.ts`
- `e2e/tests/dataQuality.spec.ts`
- `e2e/tests/identity.spec.ts`
- `e2e/tests/ingestion.spec.ts`
- `e2e/tests/mapping.spec.ts`
- `services/core-api/internal/dataquality/golden_test.go`
- `services/core-api/internal/dataquality/handler.go`
- `services/core-api/internal/dataquality/incidents_test.go`
- `services/core-api/internal/dataquality/model.go`
- `services/core-api/internal/dataquality/rls_test.go`
- `services/core-api/internal/dataquality/scores.go`

## API surface

- `GET confirmText`
- `GET locale`
- `GET mappingVersionId`
- `GET rawObjectId`
- `GET columns`
- `POST /api/tenant/identity/run-matching`
- `POST /api/tenant/integrations/[id]/mapping/versions`
- `POST /api/tenant/integrations/[id]/mapping/dry-run`
- `POST /api/tenant/integrations/[id]/mapping/run`
- `POST /api/tenant/identity/candidates/[id]/approve`
- `POST /api/tenant/identity/candidates/[id]/reject`
- `POST /api/tenant/identity/merges/[id]/reverse`
- `POST /api/tenant/integrations/[id]/mapping/versions/[versionId]/activate`
