---
cortex-generated: true
title: website-lead-api
tags: [module]
---

# website_lead_api

**Project:** [[shamsieh]] | **Confidence:** inferred | **verified@** `ad14342a33e9`
**Owns:** `website_lead_api/`

purpose: Public JSON endpoint for external website contact forms to create CRM leads.
path_prefixes: website_lead_api/
key_files: controllers/*.py — POST `/api/website/lead` (auth='public', csrf=False, cors='*')
responsibilities: API-key validation, honeypot field, IP rate limiting, submission logging (`website.lead.submission.log` with ip/email/lead), multi-site/product form mapping, message escaped into Internal Notes.
invariants: honeypot returns fake success; every lead leaves a submission-log row.
confidence: high

## Files (7+)

- `website_lead_api/__init__.py`
- `website_lead_api/__manifest__.py`
- `website_lead_api/controllers/__init__.py`
- `website_lead_api/controllers/main.py`
- `website_lead_api/models/__init__.py`
- `website_lead_api/models/crm_lead.py`
- `website_lead_api/models/website_lead_submission_log.py`
