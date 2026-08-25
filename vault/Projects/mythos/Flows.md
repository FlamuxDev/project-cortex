---
cortex-generated: true
title: mythos flows
tags: [flows/project]
---

# mythos — Product Flows

End-to-end behaviors as verified from source. Files are the evidence trail.

## Chat turn with tool call (any surface)
**Trigger:** user message via CLI, TUI, dashboard WS, or gateway adapter.
*[[mythos]] · confidence: high*

trigger: user message via CLI, TUI, dashboard WS, or gateway adapter.
steps: surface → AIAgent.run_conversation → chat.completions.create(tools=schemas) → if tool_calls: handle_function_call (plugin pre/post hooks, sandbox validator, tool exec in terminal backend) → tool result appended → repeat until content-only response or budget/interrupt.
files: run_agent.py, model_tools.py, tools/registry.py, tools/environments/*
confidence: high

**Files:**
- `run_agent.py`
- `model_tools.py`
- `tools/registry.py`
- `tools/environments/*`

## Messaging gateway turn
**Trigger:** platform webhook/polling delivers message to bot.
*[[mythos]] · confidence: high*

trigger: platform webhook/polling delivers message to bot.
steps: adapter receives → guard 1 (base.py queues if session active) → guard 2 (run.py intercepts control commands) → session lookup → agent turn → delivery.py replies to platform; background-process completions trigger new turns via watcher.
files: gateway/run.py, gateway/platforms/base.py, gateway/session.py, gateway/delivery.py
confidence: high

**Files:**
- `gateway/run.py`
- `gateway/platforms/base.py`
- `gateway/session.py`
- `gateway/delivery.py`

## Cloud proxied inference
**Trigger:** agent issues chat-completions with bearer = Safa session token (device holds no provider keys).
*[[mythos]] · confidence: high*

trigger: agent issues chat-completions with bearer = Safa session token (device holds no provider keys).
steps: POST /v1/chat/completions → validate session → check quota/rate/concurrency → route upstream with server-side key → meter tokens (usage_event + counter RPC) → stream back; breach → 402/429 {code:"quota_exceeded"}; kill-switch hard-disables.
files: mythos-cloud/app/proxy.py, quota.py, upstream.py, db.py
confidence: high

**Files:**
- `mythos-cloud/app/proxy.py`
- `quota.py`
- `upstream.py`
- `db.py`

## Device-link auth
**Trigger:** fresh install login.
*[[mythos]] · confidence: medium*

trigger: fresh install login.
steps: device POST /auth/device/start (shows code) → user approves in web/app → device polls /auth/device/poll → approved → session token stored in ~/.safa/auth.json (0600).
files: mythos-cloud/app/auth.py, safa_cli/auth.py, mythos-docs/02-mythos-cloud-api.md
confidence: medium-high

**Files:**
- `mythos-cloud/app/auth.py`
- `safa_cli/auth.py`
- `mythos-docs/02-mythos-cloud-api.md`

## Cron job fire
**Trigger:** scheduler tick (file-locked).
*[[mythos]] · confidence: high*

trigger: scheduler tick (file-locked).
steps: due jobs selected → catchup/grace window math → spawn headless agent session (skip_memory, 3-min hard interrupt) → optional pre-run script stdout injected → output delivered to configured platforms → stored in dedicated cron session.
files: cron/scheduler.py, cron/jobs.py
confidence: high

**Files:**
- `cron/scheduler.py`
- `cron/jobs.py`

## Dashboard chat (PTY embed)
**Trigger:** user opens /chat in dashboard.
*[[mythos]] · confidence: high*

trigger: user opens /chat in dashboard.
steps: xterm.js connects /api/pty?token=… → server spawns `safa --tui` child via ptyprocess → raw byte frames both ways → resize escape applied via TIOCSWINSZ.
files: safa_cli/web_server.py (@app.websocket("/api/pty")), safa_cli/pty_bridge.py, web/src/pages/ChatPage.tsx
confidence: high

**Files:**
- `safa_cli/web_server.py (@app.websocket("/api/pty"))`
- `safa_cli/pty_bridge.py`
- `web/src/pages/ChatPage.tsx`
