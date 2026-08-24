---
cortex-generated: true
title: governed-agentic-layer
tags: [module]
---

# Governed agentic layer

**Project:** [[telvora]] | **Confidence:** verified | **verified@** `7423f040ed46`
**Owns:** `services/core-api/internal/llm`

purpose: LLM conversations (converse), per-tenant AI policy (allowed models pinned to simulator by default), typed read-only tool registry, redaction before provider calls, alert/RCA/campaign-architect drafting
path_prefixes: services/core-api/internal/llm
key_files: tools.go (BuildRegistry), runtime.go, redact.go, anthropic.go, simulator.go, registry.go
entrypoints: POST ai/converse, GET/PUT ai/policy
invariants: tools expose only the same masked/read paths as HTTP APIs (reveal=false hardcoded, tools.go comment); no arbitrary SQL/shell tools; adversarial test suite guards this (eval_test, redact_test, alert_tool_test)
confidence: verified

## Files (19+)

- `services/core-api/internal/llm/alert_tool_test.go`
- `services/core-api/internal/llm/anthropic.go`
- `services/core-api/internal/llm/anthropic_test.go`
- `services/core-api/internal/llm/campaign_architect_test.go`
- `services/core-api/internal/llm/eval_test.go`
- `services/core-api/internal/llm/handler.go`
- `services/core-api/internal/llm/model.go`
- `services/core-api/internal/llm/provider.go`
- `services/core-api/internal/llm/redact.go`
- `services/core-api/internal/llm/redact_test.go`
- `services/core-api/internal/llm/registry.go`
- `services/core-api/internal/llm/registry_test.go`
- `services/core-api/internal/llm/rls_test.go`
- `services/core-api/internal/llm/runtime.go`
- `services/core-api/internal/llm/simulator.go`
- `services/core-api/internal/llm/simulator_test.go`
- `services/core-api/internal/llm/store.go`
- `services/core-api/internal/llm/testutil_test.go`
- `services/core-api/internal/llm/tools.go`
