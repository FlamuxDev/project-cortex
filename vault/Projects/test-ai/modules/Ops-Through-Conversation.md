---
cortex-generated: true
title: ops-through-conversation
tags: [module]
---

# ops-through-conversation

**Project:** [[test-ai]] | **Confidence:** inferred | **verified@** `ec5e16f84200`
**Owns:** `agent/institution_verify.py`

purpose: Let staff verify institutions/teachers through WhatsApp flows backed by the Shamsieh admin API.
path_prefixes: agent/institution_verify.py
key_files: agent/institution_verify.py (login → JWT, pending_requests, create_upload_url → S3 put image, file_evidence, set_whatsapp_number, teacher verification)
entrypoints: triggered by intent phrases (wants_verify/wants_teacher_verify/menu/cancel)
responsibilities: evidence upload, WhatsApp number capture with phone normalization.
confidence: medium-high

## Files (1+)

- `agent/institution_verify.py`
