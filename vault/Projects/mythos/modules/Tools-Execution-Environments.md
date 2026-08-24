---
cortex-generated: true
title: tools-execution-environments
tags: [module]
---

# Tools & execution environments

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `tools/,tools/environments/`

purpose: 40+ built-in tools and seven terminal backends where shell/file/browser work executes.
path_prefixes: tools/, tools/environments/
key_files: tools/registry.py (zero-dep import root), tools/environments/ (local, docker, ssh, singularity, modal, daytona, vercel sandbox), tools/browser_tool.py + browser_supervisor.py + browser_cdp_tool.py, tools/delegate_tool.py, tools/file_operations.py, tools/approval.py, tools/mcp_tool.py, tools/code_execution_tool.py
entrypoints: invoked via handle_function_call from any surface
responsibilities: schema registration at import time; availability checks (check_fn/requires_env); background processes with notify_on_complete; browser self-healing (silent daemon-respawn detection + re-navigate, git 62cfac3/481cc72)
invariants: a registered tool is only exposed if its name appears in a toolset; state paths must use get_safa_home(); schemas generated after profile override
pitfalls: dead code wired into live paths without E2E validation (documented incident class)
confidence: high

## Files (40+)

- `tests/tools/__init__.py`
- `tests/tools/test_accretion_caps.py`
- `tests/tools/test_ansi_strip.py`
- `tests/tools/test_approval.py`
- `tests/tools/test_approval_heartbeat.py`
- `tests/tools/test_approval_plugin_hooks.py`
- `tests/tools/test_base_environment.py`
- `tests/tools/test_browser_autorecover.py`
- `tests/tools/test_browser_camofox.py`
- `tests/tools/test_browser_camofox_persistence.py`
- `tests/tools/test_browser_camofox_state.py`
- `tests/tools/test_browser_cdp_override.py`
- `tests/tools/test_browser_cdp_tool.py`
- `tests/tools/test_browser_chromium_check.py`
- `tests/tools/test_browser_cleanup.py`
- `tests/tools/test_browser_click_scroll.py`
- `tests/tools/test_browser_cloud_fallback.py`
- `tests/tools/test_browser_console.py`
- `tests/tools/test_browser_content_none_guard.py`
- `tests/tools/test_browser_hardening.py`
- `tests/tools/test_browser_homebrew_paths.py`
- `tests/tools/test_browser_hybrid_routing.py`
- `tests/tools/test_browser_lightpanda.py`
- `tests/tools/test_browser_orphan_reaper.py`
- `tests/tools/test_browser_secret_exfil.py`
