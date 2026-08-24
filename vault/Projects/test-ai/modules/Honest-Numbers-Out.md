---
cortex-generated: true
title: honest-numbers-out
tags: [module]
---

# honest numbers out

**Project:** [[test-ai]] | **Confidence:** inferred | **verified@** `ec5e16f84200`
**Owns:** `agent/facts.py,agent/answer.py,agent/suggestions.py`

purpose: Compute everything deterministically, render the answer from a fact sheet only, and reject invented figures.
path_prefixes: agent/facts.py, agent/answer.py, agent/suggestions.py
key_files: agent/facts.py (all arithmetic + coverage denominator), agent/answer.py (Gemini call #2 + output guard)
invariants: every number in output must trace to the fact sheet; "a measured zero is not a warning" — honest-looking zeros were a hunted bug class (1dc16c3, 699008b).
confidence: high

## Files (3+)

- `agent/answer.py`
- `agent/facts.py`
- `agent/suggestions.py`
