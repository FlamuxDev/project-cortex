---
cortex-generated: true
title: go-modular-monolith-all-domains
tags: [module]
---

# Go modular monolith (all domains)

**Project:** [[telvora]] | **Confidence:** verified | **verified@** `7423f040ed46`
**Owns:** `services/core-api/cmd/*,services/core-api/internal/*`

purpose: every REST endpoint, background worker, and domain rule for the platform
path_prefixes: services/core-api/cmd/*, services/core-api/internal/*
key_files: cmd/server/main.go (composition root + all routes), cmd/migrate/main.go (+ bootstrap.go seed.go), internal/db/{db,context,url}.go, internal/httputil/httputil.go
entrypoints: `go run ./cmd/server` (:8080), `go run ./cmd/migrate up|seed|bootstrap-up`
responsibilities: DI of ~30 store/handler pairs; correlation middleware; dual-pool DB access; worker lifecycle
invariants: runtime DB roles are NOSUPERUSER NOBYPASSRLS; tenant context set ONLY via db.WithTenantContext after server-side membership resolution; module storage is private — cross-module access only via exported Store methods (ADR-0001)
pitfalls: net/http ServeMux pattern ambiguity — sibling `{id}/versions` vs top-level `{resource}-versions` collections (see main.go:462-483 comments); adding a route without updating packages/contracts breaks contract sync [inferred]
confidence: verified

