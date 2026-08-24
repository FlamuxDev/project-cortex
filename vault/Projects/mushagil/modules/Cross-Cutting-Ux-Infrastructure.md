---
cortex-generated: true
title: cross-cutting-ux-infrastructure
tags: [module]
---

# Cross-Cutting UX Infrastructure

**Project:** [[mushagil]] | **Confidence:** verified | **verified@** `638838aad84d`
**Owns:** `packages/observability,packages/i18n,packages/ui`

purpose: structured logging w/ redaction; ar/en catalogs + formatting; accessible RTL-safe UI primitives.
path_prefixes: packages/observability, packages/i18n, packages/ui
key_files: observability/src (pino logger, redaction); i18n/src/catalogs/ar.ts (source of truth) + en.ts, i18n/src/format; ui/src/primitives/* (19 primitives incl. new Tabs/Textarea/TimeField), ui/src/tokens, ui/src/lint
entrypoints: getLogger(); catalog/format helpers; primitive components consumed by apps/web
responsibilities: secret/log redaction; Arabic-first catalogs with numbers/dates/money formatting helpers; logical-CSS primitives (no left/right).
invariants: Arabic catalog is key source of truth; feature code may not import Radix directly (dependency-cruiser rule).
pitfalls: edge middleware (apps/web/middleware.ts) carries an inline fallback because @mushagil/i18n may be unbuilt during dev — transient-state workaround noted in file header.
confidence: verified

