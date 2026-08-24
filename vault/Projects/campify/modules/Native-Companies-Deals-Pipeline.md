---
cortex-generated: true
title: native-companies-deals-pipeline
tags: [module]
---

# native companies/deals/pipeline

**Project:** [[campify]] | **Confidence:** strongly_inferred | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/crm`

purpose: native CRM (ADR-0013): companies, deals on per-workspace pipelines, activity timeline.
path_prefixes: packages/core/src/crm
key_files: packages/core/src/crm/repository.ts; migrations 0034
entrypoints: /v1/workspaces/:id/crm/* (companies, deals, stage, outcome, activities, stages)
responsibilities: deals reference contacts (single identity record — never restates name/email); default pipeline seeded by seed_default_pipeline().
invariants: contacts stays the single source of person identity.
confidence: strongly_inferred

