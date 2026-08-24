---
cortex-generated: true
title: ink-tui-json-rpc-gateway
tags: [module]
---

# Ink TUI + JSON-RPC gateway

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `ui-tui/,tui_gateway/`

purpose: full terminal replacement UI; TypeScript renders, Python computes.
path_prefixes: ui-tui/, tui_gateway/
key_files: ui-tui/src/app.tsx, entry.tsx, gatewayClient.ts; tui_gateway/server.py (method/event catalog)
entrypoints: `safa --tui`; also embedded in dashboard via PTY
responsibilities: streaming transcript, approvals/clarify/sudo prompts, session picker, slash-command worker subprocess (_SlashWorker)
invariants: transport = newline-delimited JSON-RPC over stdio; do NOT re-implement chat surfaces in React for the dashboard — extend Ink
confidence: high

## Files (40+)

- `tests/tui_gateway/__init__.py`
- `tests/tui_gateway/test_entry_sys_path.py`
- `tests/tui_gateway/test_goal_command.py`
- `tests/tui_gateway/test_make_agent_provider.py`
- `tests/tui_gateway/test_protocol.py`
- `tests/tui_gateway/test_render.py`
- `tests/tui_gateway/test_review_summary_callback.py`
- `tui_gateway/__init__.py`
- `tui_gateway/entry.py`
- `tui_gateway/event_publisher.py`
- `tui_gateway/render.py`
- `tui_gateway/server.py`
- `tui_gateway/slash_worker.py`
- `tui_gateway/transport.py`
- `tui_gateway/ws.py`
- `ui-tui/babel.compiler.config.cjs`
- `ui-tui/eslint.config.mjs`
- `ui-tui/packages/mythos-ink/ambient.d.ts`
- `ui-tui/packages/mythos-ink/index.d.ts`
- `ui-tui/packages/mythos-ink/index.js`
- `ui-tui/packages/mythos-ink/src/bootstrap/state.ts`
- `ui-tui/packages/mythos-ink/src/entry-exports.ts`
- `ui-tui/packages/mythos-ink/src/hooks/use-stderr.ts`
- `ui-tui/packages/mythos-ink/src/hooks/use-stdout.ts`
- `ui-tui/packages/mythos-ink/src/ink/Ansi.tsx`

## API surface

- `GET d`
- `GET c`
- `GET b`
- `GET a`
