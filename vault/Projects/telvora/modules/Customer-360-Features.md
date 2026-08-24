---
cortex-generated: true
title: customer-360-features
tags: [module]
---

# Customer 360 + features

**Project:** [[telvora]] | **Confidence:** verified | **verified@** `7423f040ed46`
**Owns:** `services/core-api/internal/{customer360,features}`

purpose: unified person view (***REDACTED-B64*** history) and the windowed feature platform feeding models/decisions
path_prefixes: services/core-api/internal/{customer360,features}
key_files: internal/customer360/store.go; internal/features/{compute,snapshot}.go (compute_key closed registry; FilesystemSnapshotStore stands in for S3 Parquet)
entrypoints: GET customers/{id}, POST customers/{id}/reveal-pii, features definitions/recompute/values/snapshot
responsibilities: masked-by-default reads; leakage-safe windowed features with freshness flags; parity + leakage tests exist (features/parity_test.go, leakage_test.go)
invariants: reveal=false paths are what agents/AI see (llm/tools.go enforces); feature freshness degradation must surface, not fail (decisions/store.go buildContextSnapshot)
pitfalls: snapshot store is filesystem-local — multi-instance prod needs EFS (wired in CDK platform-stack.ts) 
confidence: verified

