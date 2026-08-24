---
cortex-generated: true
title: plugins-model-providers
tags: [module]
---

# Plugins & model providers

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `plugins/,providers/,safa_cli/plugins.py`

purpose: extensibility without core edits; every inference backend is a swappable plugin.
path_prefixes: plugins/, providers/, safa_cli/plugins.py
key_files: safa_cli/plugins.py (PluginManager: ~/.safa/plugins, ./.safa/plugins, pip entry points; hooks pre/post_tool_call, pre/post_llm_call, session start/end; ctx.register_tool/register_cli_command), providers/__init__.py (lazy provider discovery, last-writer-wins), plugins/memory/<provider>/, plugins/model-providers/<name>/
entrypoints: discovered on model_tools import (general) or first get_provider_profile call (model-providers)
responsibilities: lifecycle hooks, extra tools/CLI commands, image-gen & context-engine provider dirs follow same ABC+orchestrator pattern
invariants: plugins MUST NOT modify core files — extend the generic surface instead (rule attributed Teknium May 2026; PR #5295 removed hardcoded honcho argparse); PluginManager records but does not import kind:model-provider manifests (double-instantiation)
pitfalls: discover_plugins() only runs as a side effect of importing model_tools.py
confidence: high

## Files (40+)

- `plugins/__init__.py`
- `plugins/context_engine/__init__.py`
- `plugins/disk-cleanup/__init__.py`
- `plugins/disk-cleanup/disk_cleanup.py`
- `plugins/example-dashboard/dashboard/plugin_api.py`
- `plugins/google_meet/__init__.py`
- `plugins/google_meet/audio_bridge.py`
- `plugins/google_meet/cli.py`
- `plugins/google_meet/meet_bot.py`
- `plugins/google_meet/node/__init__.py`
- `plugins/google_meet/node/cli.py`
- `plugins/google_meet/node/client.py`
- `plugins/google_meet/node/protocol.py`
- `plugins/google_meet/node/registry.py`
- `plugins/google_meet/node/server.py`
- `plugins/google_meet/process_manager.py`
- `plugins/google_meet/realtime/__init__.py`
- `plugins/google_meet/realtime/openai_client.py`
- `plugins/google_meet/tools.py`
- `plugins/image_gen/openai-codex/__init__.py`
- `plugins/image_gen/openai/__init__.py`
- `plugins/image_gen/xai/__init__.py`
- `plugins/kanban/dashboard/plugin_api.py`
- `plugins/memory/__init__.py`
- `plugins/memory/byterover/__init__.py`

## API surface

- `GET /hello`
- `GET /board`
- `GET /tasks/{task_id}`
- `POST /tasks`
- `PATCH /tasks/{task_id}`
- `POST /tasks/{task_id}/comments`
- `POST /links`
- `DELETE /links`
- `POST /tasks/bulk`
- `GET /diagnostics`
- `POST /tasks/{task_id}/reclaim`
- `POST /tasks/{task_id}/reassign`
- `GET /config`
- `GET /home-channels`
- `POST /tasks/{task_id}/home-subscribe/{platform}`
