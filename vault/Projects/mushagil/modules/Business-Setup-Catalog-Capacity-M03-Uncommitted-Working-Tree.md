---
cortex-generated: true
title: business-setup-catalog-capacity-m03-uncommitted-working-tree
tags: [module]
---

# Business Setup, Catalog & Capacity (M03, uncommitted working tree)

**Project:** [[mushagil]] | **Confidence:** inferred | **verified@** `638838aad84d`
**Owns:** `packages/modules/business-capacity,apps/api/src/business,apps/api/src/catalog,packages/database/src/schema/business.schema.ts + catalog.schema.ts,apps/web components BusinessProfileScreen/LocationsScreen/KnowledgeScreen/PoliciesScreen/ServicesScreen/StaffScreen/ResourcesScreen/ReadinessScreen/OnboardingScreen/IndustryScreen`

purpose: deterministic Beauty business truth — profile, locations/hours/closures, booking policy, knowledge, onboarding, publish/readiness, services/versions/pricing, skills, staff/schedules/time-off, resources/blocks, offering resolution.
path_prefixes: packages/modules/business-capacity, apps/api/src/business, apps/api/src/catalog, packages/database/src/schema/business.schema.ts + catalog.schema.ts, apps/web components ***REDACTED-B64***
key_files: src/application/publication-service.ts (builds whole-truth JSONB snapshot + hash), src/application/published-truth-service.ts (reads ONLY business_publication — ADR 0004), src/application/offering-resolution-service.ts (deterministic price/duration/intake/staff/resource resolution against published truth), src/application/readiness-service.ts, src/domain/{pricing,duration,intake,capacity,eligibility,opening-hours,week-time,state-machines,knowledge-truth,impact,readiness}.ts, src/infrastructure/keyset-pagination.ts
entrypoints: ~50 REST routes under /v1/business/** (profile, readiness, publish, publications, knowledge, locations+hours+closures, packs install/migrate/rollback, policies draft/publish, onboarding advance/complete) and /v1/catalog/** (services, offerings/resolve, skills, staff incl. schedule/time-off, resources incl. capacity/blocks/archive-impact) — see APIS table
responsibilities: draft→publish lifecycle where publishing writes an append-only self-contained business_publication JSONB document (canonical hash + readiness evaluation) and refuses while any BLOCKING readiness item exists; per-aggregate versioning (service_version, booking_policy, knowledge_entry) referenced by publication.
invariants: availability/resolution reads published snapshots only — drafts can never leak to customers/AI; optimistic versioning with If-Match required on updates (apps/api/src/business/shared/if-match.ts returns 422 when missing); overlap-free weekly hours enforced by GiST exclusion constraints on derived int4range week-minute segments [0,10080), overnight written as two segments (ADR 0005); absolute intervals use tstzrange exclusion constraints, time-off partial on status='APPROVED'; quote-required pricing never fabricates fixed price; archive/capacity-reduction return impact previews.
pitfalls: day_of_week is ISO order 0=Monday…6=Sunday, NOT JS getDay() (ADR 0005); segments are derived state replaced wholesale with their parent rule, never edited in place; effectivity-dated schedules deliberately not modelled (would break single-exclusion guarantee); raw parameterized SQL used in infrastructure/raw-tenant-read.ts rather than full Drizzle coverage — cross-schema joins possible in principle, review must keep enforcing module boundaries (ADR 0003 consequences).
confidence: verified (code+tests read directly; module not yet marked DONE in MODULES.md)

