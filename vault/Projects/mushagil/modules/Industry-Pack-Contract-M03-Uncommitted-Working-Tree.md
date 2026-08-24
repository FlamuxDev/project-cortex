---
cortex-generated: true
title: industry-pack-contract-m03-uncommitted-working-tree
tags: [module]
---

# Industry Pack Contract (M03, uncommitted working tree)

**Project:** [[mushagil]] | **Confidence:** inferred | **verified@** `638838aad84d`
**Owns:** `packages/modules/packs`

purpose: declarative versioned pack definitions (BEAUTY v1/v2 seeded), custom fields, install/migrate/rollback with hash pinning.
path_prefixes: packages/modules/packs
key_files: src/domain/pack-definition.ts (typed contract; parsePackDefinition is sole jsonb→typed gateway), src/domain/pack-hash.ts, src/domain/pack-migration-plan.ts, src/application/pack-installation-service.ts, src/infrastructure/pack-definition-repository.ts
entrypoints: /v1/business/packs routes (available/install/customizations/migrate/rollback/migrations)
responsibilities: packs configure terminology/custom fields/defaults without forking core; custom fields referenced by published truth are retained read-only rather than deleted (ADR 0004 consequence).
invariants: pack definition hash pinned at install; migration dry-run + rollback preserving published truth.
pitfalls: nothing may assume a jsonb `definition` value is well-formed without parsePackDefinition.
confidence: strongly_inferred (read directly, fewer dedicated tests than business-capacity)

