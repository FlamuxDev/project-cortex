---
cortex-generated: true
title: language-understanding-without-a-model
tags: [module]
---

# language understanding without a model

**Project:** [[test-ai]] | **Confidence:** inferred | **verified@** `ec5e16f84200`
**Owns:** `agent/arabic.py,agent/lang.py`

purpose: Arabic normalization, language detection, synonym/respelling tolerance.
path_prefixes: agent/arabic.py, agent/lang.py
key_files: agent/arabic.py (normalize), agent/lang.py
entrypoints: first stage of every turn
responsibilities: normalize alef/ya/taa-marbuta/diacritics parity with SQL `unaccent_ar` (audit checks equality on 4,220 names); detect language; guard gradations.
pitfalls: normalization drift between Python and SQL silently breaks name resolution — hence the standing audit.
confidence: high

## Files (2+)

- `agent/arabic.py`
- `agent/lang.py`
