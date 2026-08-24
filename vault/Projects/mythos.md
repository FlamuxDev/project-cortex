---
cortex-generated: true
title: mythos
tags: [project]
---

# mythos

**Path:** `/home/aboud/Dev/mythos`  
**Kind:** app | **Languages:** .py,.ts,.tsx,.js | **Frameworks:** None

**HEAD:** `15e9faf0b5db` | **Brain:** `15e9faf0b5db` | FRESH

| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |
|---|---|---|---|---|---|---|---|---|
| 2022 | 47934 | 15 | 6 | 144 | 33 | 1090 | 9 | 23 (0 stale) |

## Modules
- [[mythos/modules/Agent-Core-Aiagent-Tool-Orchestration|Agent Core (AIAgent + tool orchestration)]] — synchronous LLM tool-calling loop, context compression, prompt caching, credential routing. [inferred]
- [[mythos/modules/Batch-Generation-Rl-Environments|Batch generation & RL environments]] — trajectory generation/compression and Atropos RL training envs (research heritage from Hermes). [inferred]
- [[mythos/modules/Documentation-Web-Presence|Documentation & web presence]] — user/developer docs (Docusaurus), marketing/install site, and the internal AI-authored build-spec pa [inferred]
- [[mythos/modules/Filesystem-Boundary-Approval|Filesystem boundary & approval]] — guarantee the agent cannot touch anything outside its workspace; human-in-the-loop for dangerous ops [inferred]
- [[mythos/modules/Google-Microsoft-Account-Integrations|Google/Microsoft account integrations]] — first-class calendar/email/tasks/drive/contacts tools with OAuth. [inferred]
- [[mythos/modules/Ink-Tui-Json-Rpc-Gateway|Ink TUI + JSON-RPC gateway]] — full terminal replacement UI; TypeScript renders, Python computes. [inferred]
- [[mythos/modules/Local-Web-Dashboard-Api|Local web dashboard + API]] — localhost SPA managing config/sessions/skills/cron/plugins/profiles/analytics + chat via embedded TU [inferred]
- [[mythos/modules/Messaging-Gateway|Messaging Gateway]] — one long-lived process bridging Telegram/Discord/Slack/WhatsApp/etc. to agent sessions. [inferred]
- [[mythos/modules/Multi-Agent-Work-Board|Multi-agent work board]] — durable SQLite board coordinating multiple profiles/worker agents. [inferred]
- [[mythos/modules/Operator-Run-Saas-Backend|Operator-run SaaS backend]] — the ONLY internet endpoint devices talk to — inference proxy, metering, quota/credits, billing, auth [inferred]
- [[mythos/modules/Plugins-Model-Providers|Plugins & model providers]] — extensibility without core edits; every inference backend is a swappable plugin. [inferred]
- [[mythos/modules/Scheduled-Jobs|Scheduled jobs]] — natural-language scheduled automations delivered to any platform. [inferred]
- [[mythos/modules/Skills-Curator-Memory-The-Learning-Loop|Skills, curator, memory (the "learning loop")]] — procedural memory — agent-created skills that self-improve; persistent curated memory; protected ups [inferred]
- [[mythos/modules/Terminal-Cli-Subcommand-Framework|Terminal CLI + subcommand framework]] — interactive prompt_toolkit/Rich chat UI, slash commands, setup wizard, config, all `safa <verb>` sub [inferred]
- [[mythos/modules/Tools-Execution-Environments|Tools & execution environments]] — 40+ built-in tools and seven terminal backends where shell/file/browser work executes. [inferred]

## Flows
- **Chat turn with tool call (any surface)** — user message via CLI, TUI, dashboard WS, or gateway adapter.
- **Messaging gateway turn** — platform webhook/polling delivers message to bot.
- **Cloud proxied inference** — agent issues chat-completions with bearer = Safa session token (device holds no provider keys).
- **Device-link auth** — fresh install login.
- **Cron job fire** — scheduler tick (file-locked).
- **Dashboard chat (PTY embed)** — user opens /chat in dashboard.

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- mythos: overview [verified]
- Tests & commands [verified]
