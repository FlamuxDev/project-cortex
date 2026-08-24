---
cortex-generated: true
title: contact-profiles-fields-tags-lists
tags: [module]
---

# contact profiles, fields, tags, lists

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/contacts`

purpose: canonical person record + custom fields/tags/lists, normalization of emails/phones.
path_prefixes: packages/core/src/contacts
key_files: packages/core/src/contacts/repository.ts, normalize.ts
entrypoints: /v1/workspaces/:id/contacts* routes; import commit path
responsibilities: create/get/delete/list console with paging; normalization (lowercase email, phone E.164-ish) feeding dedupe and suppression matching.
invariants: dedupe on normalized destination; deleteContact writes audit.
pitfalls: paging past page 1 requires `data:export` permission — deep paging IS an export (apps/api/src/app.ts:897).
confidence: verified

