---
cortex-generated: true
title: nightly-data-swap
tags: [module]
---

# nightly data swap

**Project:** [[test-ai]] | **Confidence:** inferred | **verified@** `ec5e16f84200`
**Owns:** `agent/refresh.py,deploy/`

purpose: Restore the freshest verified directory dump from S3 without ever applying the same file twice.
path_prefixes: agent/refresh.py, deploy/
key_files: agent/refresh.py (_sign/_signed_headers SigV4, select_backup age+size+ETag+name-pattern guards, restore_into scratch, verify counts, apply_views, swap), deploy/shamsieh-refresh.timer
entrypoints: `python -m agent.refresh` (systemd oneshot, Persistent=true timer)
invariants: idempotent via ETag comparison against last applied; never creates the DB implicitly; four retries then page.
confidence: high

## Files (1+)

- `agent/refresh.py`
