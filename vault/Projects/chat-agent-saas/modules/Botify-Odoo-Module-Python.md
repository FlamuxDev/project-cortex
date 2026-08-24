---
cortex-generated: true
title: botify-odoo-module-python
tags: [module]
---

# Botify Odoo module (Python)

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** `integrations/odoo/botify_agent/,integrations/odoo/policy/`

purpose: in-Odoo addon providing signed nonce auth, delegation, policy enforcement at the source, so end-user mode enforces Odoo's own record rules.
path_prefixes: integrations/odoo/botify_agent/, integrations/odoo/policy/
key_files: __manifest__.py, controllers/, models/botify_policy.py, data/policy_manifest.json, security/, tests/
entrypoints: Odoo HTTP controllers called by packages/api/services/odoo.
responsibilities: nonce replay guard, delegation ledger w/ own expiry (c7a8cfc), deny-by-default manifest enforcement source-side, custom-model classification hooks (per-tenant policy 28203ba).
invariants: manifest version bumped on policy change (fcec602 → 2.1.0); Odoo 19 compat (res.users.groups_id removed — f4832d9; replay guard silently no-oping — 008eb05).
pitfalls: Odoo.sh "Test: Warning" build status noise (229749b); fixtures using removed fields fail on newer Odoo.
confidence: verified (structure), strongly_inferred (runtime behavior)

## Files (23+)

- `integrations/odoo/botify_agent/__init__.py`
- `integrations/odoo/botify_agent/__manifest__.py`
- `integrations/odoo/botify_agent/controllers/__init__.py`
- `integrations/odoo/botify_agent/controllers/_shared.py`
- `integrations/odoo/botify_agent/controllers/grant.py`
- `integrations/odoo/botify_agent/controllers/main.py`
- `integrations/odoo/botify_agent/models/__init__.py`
- `integrations/odoo/botify_agent/models/botify_canonical.py`
- `integrations/odoo/botify_agent/models/botify_delegation.py`
- `integrations/odoo/botify_agent/models/botify_nonce.py`
- `integrations/odoo/botify_agent/models/botify_policy.py`
- `integrations/odoo/botify_agent/models/botify_security.py`
- `integrations/odoo/botify_agent/models/res_config_settings.py`
- `integrations/odoo/botify_agent/static/src/js/botify_client_action.js`
- `integrations/odoo/botify_agent/tests/__init__.py`
- `integrations/odoo/botify_agent/tests/_helpers.py`
- `integrations/odoo/botify_agent/tests/test_delegation_and_nonce.py`
- `integrations/odoo/botify_agent/tests/test_grant_and_rpc.py`
- `integrations/odoo/botify_agent/tests/test_identity.py`
- `integrations/odoo/botify_agent/tests/test_pure_canonical.py`
- `integrations/odoo/botify_agent/tests/test_pure_grant_security.py`
- `integrations/odoo/botify_agent/tests/test_pure_policy.py`
- `integrations/odoo/botify_agent/tests/test_rpc_permissions.py`
