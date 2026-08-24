---
cortex-generated: true
title: botify-agent-protocol-v2
tags: [module]
---

# Botify Agent (protocol v2)

**Project:** [[shamsieh]] | **Confidence:** inferred | **verified@** `ad14342a33e9`
**Owns:** `botify_agent/`

purpose: Embed the external Botify AI assistant and let it act strictly as the requesting employee, via grant-based delegation.
path_prefixes: botify_agent/
key_files: controllers/main.py (/identity, /rpc), controllers/grant.py (/grant), models/botify_policy.py + botify_security.py, tests/test_pure_policy.py, tests/test_grant_and_rpc.py, tests/test_delegation_and_nonce.py
entrypoints: `/botify_agent/identity` (mints per-user delegation credential), `/botify_agent/grant` (single-use per-op grant, X-Botify-Grant header), `/botify_agent/rpc`
responsibilities: verify delegation proof + transport; enforce deny-by-default policy manifest incl. explicit operator decision to open `hr.payslip`/`hr.payslip.line` reads (commit 786781a1); company-scope escalation guard; nonce replay guard with UNIQUE(jti) created via raw ALTER TABLE because Odoo 19 ignores pre-19 `_sql_constraints`; per-tenant classification of this DB's custom models with writes default-off; voice-call button reusing the backend's `/api/widget/:agentId/elevenlabs/signed-url` with the session's identity token.
invariants: shared secret alone can never name a uid (protocol v2 breaking change, `botify_protocol_version: 2`); every RPC consumes its jti once; grant cannot exceed both the user's and delegation's companies.
pitfalls: version-coupled to the Botify backend ("older rebuilds cannot drive this addon"); grant route must stay write-capable (Odoo 17+ read-only cursor default caused ReadOnlySqlTransaction).
confidence: high

## Files (24+)

- `botify_agent/__init__.py`
- `botify_agent/__manifest__.py`
- `botify_agent/controllers/__init__.py`
- `botify_agent/controllers/_shared.py`
- `botify_agent/controllers/grant.py`
- `botify_agent/controllers/main.py`
- `botify_agent/models/__init__.py`
- `botify_agent/models/botify_canonical.py`
- `botify_agent/models/botify_delegation.py`
- `botify_agent/models/botify_nonce.py`
- `botify_agent/models/botify_policy.py`
- `botify_agent/models/botify_security.py`
- `botify_agent/models/res_config_settings.py`
- `botify_agent/static/src/js/botify_client_action.js`
- `botify_agent/static/src/js/botify_widget.js`
- `botify_agent/tests/__init__.py`
- `botify_agent/tests/_helpers.py`
- `botify_agent/tests/test_delegation_and_nonce.py`
- `botify_agent/tests/test_grant_and_rpc.py`
- `botify_agent/tests/test_identity.py`
- `botify_agent/tests/test_pure_canonical.py`
- `botify_agent/tests/test_pure_grant_security.py`
- `botify_agent/tests/test_pure_policy.py`
- `botify_agent/tests/test_rpc_permissions.py`
