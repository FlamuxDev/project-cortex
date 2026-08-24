---
cortex-generated: true
title: agent-core-aiagent-tool-orchestration
tags: [module]
---

# Agent Core (AIAgent + tool orchestration)

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `run_agent.py,model_tools.py,toolsets.py,agent/transports/,agent/prompt_builder.py,agent/context_compressor.py,agent/prompt_caching.py,agent/credential_pool.py`

purpose: synchronous LLM tool-calling loop, context compression, prompt caching, credential routing.
path_prefixes: run_agent.py, model_tools.py, toolsets.py, agent/transports/, agent/prompt_builder.py, agent/context_compressor.py, agent/prompt_caching.py, agent/credential_pool.py
key_files: run_agent.py (14.7k LOC), model_tools.py, toolsets.py, agent/auxiliary_client.py (side-LLM task routing)
entrypoints: run_agent:main (`safa-agent`), imported by every other surface
responsibilities: chat-completions/responses/codex/gemini transports; tool schema collection & dispatch; iteration/budget limits; interrupt handling; trajectory saving (research)
invariants: prompt caching must not break (no mid-conversation context/toolset changes except during compression); handlers return JSON strings; agent-level tools (todo/memory) intercepted pre-dispatch; `_last_resolved_tool_names` is a process-global saved/restored around subagents
pitfalls: cross-tool references hardcoded in schema descriptions cause hallucinated calls (must be dynamic in get_tool_definitions); cache-breaking edits cost real money
confidence: high

## Files (20+)

- `agent/context_compressor.py`
- `agent/credential_pool.py`
- `agent/prompt_builder.py`
- `agent/prompt_caching.py`
- `agent/transports/__init__.py`
- `agent/transports/anthropic.py`
- `agent/transports/base.py`
- `agent/transports/bedrock.py`
- `agent/transports/chat_completions.py`
- `agent/transports/codex.py`
- `agent/transports/types.py`
- `model_tools.py`
- `run_agent.py`
- `tests/agent/transports/__init__.py`
- `tests/agent/transports/test_bedrock_transport.py`
- `tests/agent/transports/test_chat_completions.py`
- `tests/agent/transports/test_codex_transport.py`
- `tests/agent/transports/test_transport.py`
- `tests/agent/transports/test_types.py`
- `toolsets.py`
