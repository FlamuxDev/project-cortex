---
cortex-generated: true
title: filesystem-boundary-approval
tags: [module]
---

# Filesystem boundary & approval

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `safa_sandbox/,safa_privacy/,tools/path_security.py,tools/approval.py,agent/file_safety.py,tools/checkpoint_manager.py`

purpose: guarantee the agent cannot touch anything outside its workspace; human-in-the-loop for dangerous ops.
path_prefixes: safa_sandbox/, safa_privacy/, tools/path_security.py, tools/approval.py, agent/file_safety.py, tools/checkpoint_manager.py
key_files: safa_sandbox/pathguard.py, safa_sandbox/runtime.py, safa_sandbox/config.py
entrypoints: active in every tool call path (validator before execution)
responsibilities: write_root enforcement (~/.safa/workspace), read allowlist, trash soft-delete, command approval patterns, DM pairing for messaging
invariants: launch-blocking per docs — ship OS-level isolation AND app-layer guard together (doc 05); zero-egress mandate verified by packet capture (doc 12)
confidence: medium-high (app-layer code confirmed; OS-level enforcement details not read)

## Files (17+)

- `agent/file_safety.py`
- `safa_privacy/__init__.py`
- `safa_sandbox/__init__.py`
- `safa_sandbox/config.py`
- `safa_sandbox/pathguard.py`
- `safa_sandbox/runtime.py`
- `tests/safa_privacy/__init__.py`
- `tests/safa_privacy/test_no_forbidden_egress.py`
- `tests/safa_privacy/test_telemetry_failclosed.py`
- `tests/safa_sandbox/__init__.py`
- `tests/safa_sandbox/test_file_safety_integration.py`
- `tests/safa_sandbox/test_onboarding.py`
- `tests/safa_sandbox/test_pathguard.py`
- `tests/safa_sandbox/test_runtime.py`
- `tools/approval.py`
- `tools/checkpoint_manager.py`
- `tools/path_security.py`
