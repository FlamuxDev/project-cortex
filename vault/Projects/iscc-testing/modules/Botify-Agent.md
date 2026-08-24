---
cortex-generated: true
title: botify-agent
tags: [module]
---

# botify_agent

**Project:** [[iscc-testing]] | **Confidence:** inferred | **verified@** `96dc8874d12b`
**Owns:** `botify_agent/`

purpose: Floating AI chat widget whose tool calls execute as the logged-in employee, not a shared integration account.
path_prefixes: botify_agent/
key_files: controllers/main.py, models/botify_security.py, static/src/js/botify_widget.js, tests/test_identity.py, tests/test_rpc_permissions.py
entrypoints: `/botify_agent/identity` (auth="user"), `/botify_agent/rpc` (HMAC-signed, allowlisted methods)
responsibilities: mint 120s single-use HS256 identity assertion server-side; execute Botify calls under `with_user(uid)` (su=False) so ACLs/record rules/company scope apply; method allowlist (READ/WRITE/ACTION sets) with hard FORBIDDEN set (`unlink`, `sudo`, `with_user`, `browse`, `_`-prefixed) and MAX_LIMIT=200.
invariants: browser never names the user; endpoint must be safe on its own terms (auth="none"); deletion is "a decision, not an oversight".
pitfalls: mirrors SAFE_ACTION_METHODS in a TypeScript backend ("keep the two in step") — a manual cross-repo contract.
confidence: high

## Files (12+)

- `botify_agent/__init__.py`
- `botify_agent/__manifest__.py`
- `botify_agent/controllers/__init__.py`
- `botify_agent/controllers/main.py`
- `botify_agent/models/__init__.py`
- `botify_agent/models/botify_security.py`
- `botify_agent/models/res_config_settings.py`
- `botify_agent/static/src/js/botify_client_action.js`
- `botify_agent/static/src/js/botify_widget.js`
- `botify_agent/tests/__init__.py`
- `botify_agent/tests/test_identity.py`
- `botify_agent/tests/test_rpc_permissions.py`
