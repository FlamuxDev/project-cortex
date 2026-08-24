---
cortex-generated: true
title: deterministic-domain-routing-entity-resolution
tags: [module]
---

# deterministic domain routing + entity resolution

**Project:** [[test-ai]] | **Confidence:** inferred | **verified@** `ec5e16f84200`
**Owns:** `agent/router.py,agent/resolve.py,agent/country.py,catalog/aliases.yaml,catalog/geo.yaml`

purpose: Map a question to one of 8 domains and resolve mentioned places/institutions with thresholds instead of guessing.
path_prefixes: agent/router.py, agent/resolve.py, agent/country.py, catalog/aliases.yaml, catalog/geo.yaml
key_files: agent/resolve.py (threshold 0.75, margin 0.10 → KNOWN_ABSENT / NOT_FOUND / AMBIGUOUS), agent/country.py (country via user.countryId → proxy header → server-side IP lookup → unscoped-by-design)
entrypoints: stages 2–3 of the pipeline
invariants: "non-scoped search is not an error, it's a deliberate default" (API.md); empty answers must say where the thing is (e8685eb).
confidence: high

## Files (3+)

- `agent/country.py`
- `agent/resolve.py`
- `agent/router.py`
