---
cortex-generated: true
title: messaging-gateway
tags: [module]
---

# Messaging Gateway

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `gateway/`

purpose: one long-lived process bridging Telegram/Discord/Slack/WhatsApp/etc. to agent sessions.
path_prefixes: gateway/
key_files: gateway/run.py (15.4k LOC), gateway/session.py, gateway/platforms/base.py, gateway/status.py (scoped token locks), gateway/delivery.py, gateway/pairing.py (DM pairing), gateway/hooks.py + builtin_hooks/
entrypoints: `safa gateway setup|start`
responsibilities: per-chat sessions, message queuing while busy, /stop /new /queue /approve interception, background-process completion notifications, cross-platform conversation continuity, sticker/media handling
invariants: two sequential guards (adapter `_pending_messages` + runner) both must bypass approval/control commands; adapters holding unique credentials take acquire_scoped_lock(); cron deliveries land in separate cron sessions, not mirrored
pitfalls: new inline commands must bypass BOTH guards or race session lifecycle; MESSAGING_CWD removed (use terminal.cwd)
confidence: high

## Files (40+)

- `gateway/__init__.py`
- `gateway/builtin_hooks/__init__.py`
- `gateway/channel_directory.py`
- `gateway/config.py`
- `gateway/delivery.py`
- `gateway/display_config.py`
- `gateway/hooks.py`
- `gateway/mirror.py`
- `gateway/pairing.py`
- `gateway/platform_registry.py`
- `gateway/platforms/__init__.py`
- `gateway/platforms/_http_client_limits.py`
- `gateway/platforms/api_server.py`
- `gateway/platforms/base.py`
- `gateway/platforms/bluebubbles.py`
- `gateway/platforms/dingtalk.py`
- `gateway/platforms/discord.py`
- `gateway/platforms/email.py`
- `gateway/platforms/feishu.py`
- `gateway/platforms/feishu_comment.py`
- `gateway/platforms/feishu_comment_rules.py`
- `gateway/platforms/helpers.py`
- `gateway/platforms/homeassistant.py`
- `gateway/platforms/matrix.py`
- `gateway/platforms/mattermost.py`
