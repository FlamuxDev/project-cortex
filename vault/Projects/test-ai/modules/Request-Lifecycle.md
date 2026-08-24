---
cortex-generated: true
title: request-lifecycle
tags: [module]
---

# request lifecycle

**Project:** [[test-ai]] | **Confidence:** inferred | **verified@** `ec5e16f84200`
**Owns:** `agent/pipeline.py,agent/session.py,agent/intake.py,agent/smalltalk.py`

purpose: Orchestrate one turn end-to-end with outcome classification (answered/smalltalk/refused/clarified/plan_failed).
path_prefixes: agent/pipeline.py, agent/session.py, agent/intake.py, agent/smalltalk.py
key_files: agent/pipeline.py (Agent.ask, TurnResult)
entrypoints: called by api.py, cli.py, whatsapp.py, voice.py
responsibilities: session context carrying location/country/last entities; clarification handling; timings + token usage capture.
invariants: two Gemini calls max on normal path; zero-model fast path preserved.
confidence: high

## Files (4+)

- `agent/intake.py`
- `agent/pipeline.py`
- `agent/session.py`
- `agent/smalltalk.py`
