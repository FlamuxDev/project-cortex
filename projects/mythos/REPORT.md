# CORTEX REPORT — mythos

## META
project_id: mythos
root: /home/aboud/Dev/mythos
kind: monorepo — AI agent product (local Python agent + messaging gateway + web dashboard + SaaS cloud backend + docs sites)
languages: Python (~1570 files, primary), TypeScript/TSX (~287: dashboard SPA, Ink TUI, marketing site), SQL (migrations), YAML/XSD (skills, schemas), Shell/Nix
frameworks: openai+anthropic SDKs, FastAPI+uvicorn (dashboard API, cloud), Rich+prompt_toolkit (CLI), React 19+Vite (web/, mythos-web/), Ink (ui-tui), Docusaurus (website/), Stripe (cloud billing), Supabase→Neon Postgres (cloud DB)
package_managers: uv (uv.lock), pip/setuptools (pyproject.toml extras: modal/daytona/vercel/messaging/matrix/voice/web/rl/all…), npm (web/, ui-tui/, mythos-web/, website/), nix (flake.nix)
test_frameworks: pytest (+pytest-xdist/-asyncio/-cov, marker `integration` excluded by default) via scripts/run_tests.sh; vitest (ui-tui); plain pytest (mythos-cloud/tests)
deployment: single-device install one-liner (scripts/install.sh, Termux/macOS/Linux); Docker (Dockerfile + docker-compose.yml: gateway + dashboard services); wheel shipped to own VPS via scripts/deploy.sh with stamped builds ("ship build <ts>", silent-update rollout %); mythos-cloud/ on Vercel (ASGI entry index.py, maxDuration=60) and/or VPS; GitHub Actions: tests, lint, docker-publish, deploy-site (Vercel hook), supply-chain-audit, osv-scanner

## OVERVIEW
`mythos` is the working directory of **Safa Agent** — a self-improving personal AI assistant (MIT, by "Shamsieh Technology Services"). Git evidence shows lineage: commit 027c668 *"Mythos — web-first SaaS fork of Hermes Agent (initial import)"* forked NousResearch's Hermes Agent v0.13.0; it was then deeply renamed mythos→safa (b744782, with a corruption incident dcf5166/d2db7d2). SHIFT.md confirms: "fork من Hermes Agent … أُعيد تسميته: Hermes → Mythos → Safa", users live on safaict.com, "stability first always". The dir name `mythos` is a leftover of the middle brand; all code/config/env now say `safa`.

The product is a **local agent + cloud brain**: the agent runs on the user's machine (CLI/TUI/dashboard/messaging gateways) and talks only to operator-run **Safa Cloud** (`mythos-cloud/`) for authenticated OpenAI-compatible inference, metering, quota/credits and billing; upstream provider keys never live on device (mythos-docs/01-architecture.md). The design-doc package in `mythos-docs/` (00–14) is written as build instructions for an autonomous coding agent and defines non-negotiables: keep the learning loop untouched, zero telemetry egress to the upstream org (packet-capture verified, doc 06), OS-level filesystem sandbox (doc 05), cloud quota/kill-switch before real users.

Core differentiators (README.md): closed learning loop (auto-created skills, self-improvement, FTS5 session recall, Honcho user modeling), messaging gateway to ~25 platforms from one process, natural-language cron automations, delegation/subagents, seven terminal backends (local/Docker/SSH/Singularity/Modal/Daytona/Vercel), RL/trajectory research tooling. Codebase is huge and doc-heavy (~964 .md incl. bundled skills' SKILL.md files and the Docusaurus tree).

Scale hotspots [measured]: run_agent.py 14.7k LOC (AIAgent loop), gateway/run.py 15.4k LOC, cli.py 12.6k LOC, safa_cli/web_server.py 4.2k LOC; ~977 test files / ~20k test functions under tests/.

## ARCHITECTURE
- **Agent core** — `run_agent.py` (`AIAgent.run_conversation()`: synchronous OpenAI-format tool loop, max_iterations=90 default, iteration budget, interrupts) + `model_tools.py` (tool discovery/dispatch, plugin hooks) + `toolsets.py` (`TOOLSETS` dict, `_SAFA_CORE_TOOLS`). Dependency chain enforced: `tools/registry.py ← tools/*.py ← model_tools.py ← run_agent/cli/batch_runner/environments` (AGENTS.md).
- **Surfaces (entrypoints)** — console scripts in pyproject.toml: `safa` = `safa_cli.main:main` (CLI + all subcommands + dashboard), `safa-agent` = `run_agent:main`, `safa-acp` = `acp_adapter.entry:main`. Plus `mcp_serve.py` (MCP server), `gateway/run.py` (messaging gateway process), `python -m safa_cli.main` for background services.
- **Messaging gateway** — `gateway/run.py` orchestrator + `session.py` + `platforms/` adapters: telegram, discord, slack, whatsapp, signal, matrix, mattermost, email, sms, dingtalk, wecom, weixin, feishu, qqbot, bluebubbles, yuanbao, webhook, homeassistant, api_server… (adding guide: platforms/ADDING_A_PLATFORM.md). Two message guards (base adapter queue + runner command interception) — see AGENTS.md pitfalls.
- **TUI** — `ui-tui/` (Ink/React TS owns the screen) ⇄ `tui_gateway/server.py` (Python JSON-RPC over stdio newline-delimited; prompt/tool/approval/session methods).
- **Dashboard** — `web/` React SPA built into the wheel (`safa_cli/web_dist`), served by FastAPI `safa_cli/web_server.py` (`/api/*`, token auth, `/api/pty` websocket embedding the real `safa --tui` via ptyprocess/xterm.js). Local-server contract modules: `safa_localserver/` (account/workspace APIs, localtoken).
- **Tools** — `tools/*.py` auto-discovered via registry.register(); terminal backends in `tools/environments/`; browser stack (browser_tool, cdp, camofox, supervisor w/ crash auto-recovery); MCP client (`mcp_tool.py`, oauth); delegation (`delegate_tool.py`: leaf/orchestrator roles, depth≤2).
- **Skills & learning loop** — `skills/` (bundled), `optional-skills/` (install-on-demand via `tools/skills_hub.py`), user skills in `$SAFA_HOME/skills/`; `agent/curator.py` background lifecycle (usage sidecar `.usage.json`, archive-only, pinned exempt); memory via `agent/memory_manager.py` + provider ABC `agent/memory_provider.py` (honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb under plugins/memory/).
- **Cron** — `cron/jobs.py` (store) + `cron/scheduler.py` (tick loop, `.tick.lock` file lock, 3-min hard interrupt, catchup windows).
- **Kanban multi-agent board** — `safa_cli/kanban_db.py` (SQLite), `tools/kanban_tools.py` (worker toolset), dispatcher runs inside gateway (`kanban.dispatch_in_gateway`).
- **Plugins/providers** — general plugin surface `safa_cli/plugins.py` + `plugins/<name>/register(ctx)`; model-provider plugins register `ProviderProfile` via lazy separate discovery (`providers/__init__.py._discover_providers()`); policy: plugins MUST NOT modify core files (PR #5295 precedent).
- **Safa Cloud** — `mythos-cloud/app/main.py` FastAPI: `/v1/chat/completions` streaming proxy (pre-flight gate sequence in `proxy.py`: session→quota→route→meter), pure decision logic isolated in `quota.py` (unit-tested, no deps), `upstream.py` routes with server-side keys, Stripe webhook, device-link auth (`/auth/device/start|poll|approve`). DB: Supabase migrations 0001–0003, prod Neon Postgres migration 0100 (git f8870a7 "resilient Neon pool", 299c143 "deployed Mythos Cloud (Vercel)").
- **Security layer** — `safa_sandbox/pathguard.py`+runtime.py (workspace-only filesystem boundary, doc 05), `tools/path_security.py`, `agent/file_safety.py`, `tools/approval.py` (command allowlist/pairing), `safa_privacy/` (telemetry-removal mandate; audit script `scripts/strip_nous_egress.py`).
- **XML standards usage** — the only XSDs are OOXML/ECMA-376 & ISO-IEC-29500 Office schemas (wml, sml, pml, dml, vml, opc-*) vendored at `skills/productivity/powerpoint/scripts/office/schemas/` — they define Word/Excel/PowerPoint part formats so the PowerPoint skill can generate/validate .pptx XML. Not an external integration standard.
- **RL/research** — `environments/` (Atropos envs: agentic_opd, hermes_swe, web_research…), `batch_runner.py`, `trajectory_compressor.py`, `rl_cli.py`, `[rl]` extra pins atroposlib+tinker git SHAs.
- **Docs/sites** — `website/` (Docusaurus, published to GitHub Pages via deploy-site.yml), `mythos-web/` ("safaeb": marketing/install landing + `latest.json` build stamp consumed by update banner), `docs/` (connector docs + kanban v1 spec PDF), `mythos-docs/` (the build-spec package).

## MODULES

### core-agent-loop — Agent Core (AIAgent + tool orchestration)
purpose: synchronous LLM tool-calling loop, context compression, prompt caching, credential routing.
path_prefixes: run_agent.py, model_tools.py, toolsets.py, agent/transports/, agent/prompt_builder.py, agent/context_compressor.py, agent/prompt_caching.py, agent/credential_pool.py
key_files: run_agent.py (14.7k LOC), model_tools.py, toolsets.py, agent/auxiliary_client.py (side-LLM task routing)
entrypoints: run_agent:main (`safa-agent`), imported by every other surface
responsibilities: chat-completions/responses/codex/gemini transports; tool schema collection & dispatch; iteration/budget limits; interrupt handling; trajectory saving (research)
invariants: prompt caching must not break (no mid-conversation context/toolset changes except during compression); handlers return JSON strings; agent-level tools (todo/memory) intercepted pre-dispatch; `_last_resolved_tool_names` is a process-global saved/restored around subagents
pitfalls: cross-tool references hardcoded in schema descriptions cause hallucinated calls (must be dynamic in get_tool_definitions); cache-breaking edits cost real money
confidence: high

### cli — Terminal CLI + subcommand framework
purpose: interactive prompt_toolkit/Rich chat UI, slash commands, setup wizard, config, all `safa <verb>` subcommands.
path_prefixes: cli.py, safa_cli/
key_files: cli.py (12.6k LOC, SafaCLI.process_command), safa_cli/commands.py (central COMMAND_REGISTRY — single source feeding CLI dispatch, gateway hooks, Telegram menu, Slack map, autocomplete), safa_cli/config.py (DEFAULT_CONFIG + _config_version migrations + OPTIONAL_ENV_VARS), safa_cli/skin_engine.py, safa_cli/curses_ui.py, safa_cli/kanban.py, safa_cli/curator.py, safa_cli/claw.py (OpenClaw migration)
entrypoints: `safa` console script
responsibilities: config load/merge (three distinct loaders — cli.py vs safa_cli/config.py vs raw YAML in gateway), wizard, backups/checkpoints
invariants: new slash command = CommandDef entry + handler(s); profile safety via get_safa_home()/display_safa_home(), never hardcode ~/.safa; no new simple_term_menu (curses instead)
pitfalls: adding a key to the wrong loader makes it invisible to CLI or gateway; config-version bumps only for destructive renames
confidence: high

### gateway — Messaging Gateway
purpose: one long-lived process bridging Telegram/Discord/Slack/WhatsApp/etc. to agent sessions.
path_prefixes: gateway/
key_files: gateway/run.py (15.4k LOC), gateway/session.py, gateway/platforms/base.py, gateway/status.py (scoped token locks), gateway/delivery.py, gateway/pairing.py (DM pairing), gateway/hooks.py + builtin_hooks/
entrypoints: `safa gateway setup|start`
responsibilities: per-chat sessions, message queuing while busy, /stop /new /queue /approve interception, background-process completion notifications, cross-platform conversation continuity, sticker/media handling
invariants: two sequential guards (adapter `_pending_messages` + runner) both must bypass approval/control commands; adapters holding unique credentials take acquire_scoped_lock(); cron deliveries land in separate cron sessions, not mirrored
pitfalls: new inline commands must bypass BOTH guards or race session lifecycle; MESSAGING_CWD removed (use terminal.cwd)
confidence: high

### tui — Ink TUI + JSON-RPC gateway
purpose: full terminal replacement UI; TypeScript renders, Python computes.
path_prefixes: ui-tui/, tui_gateway/
key_files: ui-tui/src/app.tsx, entry.tsx, gatewayClient.ts; tui_gateway/server.py (method/event catalog)
entrypoints: `safa --tui`; also embedded in dashboard via PTY
responsibilities: streaming transcript, approvals/clarify/sudo prompts, session picker, slash-command worker subprocess (_SlashWorker)
invariants: transport = newline-delimited JSON-RPC over stdio; do NOT re-implement chat surfaces in React for the dashboard — extend Ink
confidence: high

### dashboard-web — Local web dashboard + API
purpose: localhost SPA managing config/sessions/skills/cron/plugins/profiles/analytics + chat via embedded TUI.
path_prefixes: web/, safa_cli/web_server.py, safa_localserver/
key_files: web/src/App.tsx, web/src/pages/* (20 pages: Chat, Sessions, Skills, Cron, Workspace, Analytics…), safa_cli/web_server.py (FastAPI, ~4.2k LOC), safa_localserver/account_api.py, workspace_api.py, localtoken.py
entrypoints: `safa dashboard` (binds 127.0.0.1; docker-compose keeps it localhost-only)
responsibilities: REST `/api/*` (config, env vars, sessions+search, cron CRUD, profiles, plugins hub, OAuth connections, logs), `/api/pty` WebSocket (token via query param), static serving of web_dist
invariants: ephemeral _SESSION_TOKEN auth; browsers can't set Authorization on WS upgrade → query-param token; PTY frames raw bytes, resize via `\x1b[RESIZE:c;r]` escape
pitfalls: exposing on LAN without auth is unsafe (stores API keys) — docker-compose comments forbid --host 0.0.0.0
confidence: high

### tools-terminal — Tools & execution environments
purpose: 40+ built-in tools and seven terminal backends where shell/file/browser work executes.
path_prefixes: tools/, tools/environments/
key_files: tools/registry.py (zero-dep import root), tools/environments/ (local, docker, ssh, singularity, modal, daytona, vercel sandbox), tools/browser_tool.py + browser_supervisor.py + browser_cdp_tool.py, tools/delegate_tool.py, tools/file_operations.py, tools/approval.py, tools/mcp_tool.py, tools/code_execution_tool.py
entrypoints: invoked via handle_function_call from any surface
responsibilities: schema registration at import time; availability checks (check_fn/requires_env); background processes with notify_on_complete; browser self-healing (silent daemon-respawn detection + re-navigate, git 62cfac3/481cc72)
invariants: a registered tool is only exposed if its name appears in a toolset; state paths must use get_safa_home(); schemas generated after profile override
pitfalls: dead code wired into live paths without E2E validation (documented incident class)
confidence: high

### skills-learning — Skills, curator, memory (the "learning loop")
purpose: procedural memory — agent-created skills that self-improve; persistent curated memory; protected upstream asset.
path_prefixes: skills/, optional-skills/, agent/curator.py, agent/curator_backup.py, agent/memory_manager.py, agent/memory_provider.py, agent/skill_commands.py, tools/skill_*.py
key_files: agent/curator.py, tools/skill_usage.py (.usage.json sidecar), tools/skills_hub.py (agentskills.io standard + optional-skills installer)
entrypoints: slash `/<skill>` injected as user message (prompt-cache friendly); `safa curator <verb>`; `safa skills install`
responsibilities: skill creation/improvement, provenance tracking, tar.gz backups before runs, archive/restore/pin; memory provider orchestration (sync_turn/prefetch/shutdown/post_setup)
invariants: curator only touches created_by:"agent" skills; never deletes (max = archive to ~/.safa/skills/.archive/); pinned skills exempt everywhere; skill_manage delete refuses pinned
pitfalls: cron sessions pass skip_memory=True by design
confidence: high

### cron-scheduler — Scheduled jobs
purpose: natural-language scheduled automations delivered to any platform.
path_prefixes: cron/, tools/cronjob_tools.py, safa_cli/cron.py
key_files: cron/jobs.py, cron/scheduler.py
entrypoints: cronjob tool; `safa cron list/add/edit/…`; `/cron` slash
responsibilities: duration/every/5-field-cron/ISO parsing; per-job model/provider/script/context_from/workdir/multi-platform delivery
invariants: 3-minute hard interrupt per cron session; tick lock file prevents duplicate ticks across processes; catchup window = half period clamped 120s–2h; skip_memory=True
confidence: high

### kanban-fleet — Multi-agent work board
purpose: durable SQLite board coordinating multiple profiles/worker agents.
path_prefixes: safa_cli/kanban_db.py, safa_cli/kanban.py, tools/kanban_tools.py, plugins/kanban/
key_files: safa_cli/kanban_db.py (tables tasks, task_links, task_comments, task_events, task_runs, kanban_notify_subs), plugins/kanban/dashboard/, systemd unit mythos-kanban-dispatcher.service
entrypoints: `safa kanban <verb>`; dispatcher inside gateway (kanban.dispatch_in_gateway:true) or standalone service
responsibilities: atomically claim ready tasks, spawn assigned profiles, heartbeat/watch/gc, auto-block after ~5 consecutive spawn failures
invariants: Board = hard boundary (workers get SAFA_KANBAN_BOARD pinned); tenant = soft namespace within board; kanban_* toolset hidden unless SAFA_KANBAN_TASK set
confidence: high

### plugin-ecosystem — Plugins & model providers
purpose: extensibility without core edits; every inference backend is a swappable plugin.
path_prefixes: plugins/, providers/, safa_cli/plugins.py
key_files: safa_cli/plugins.py (PluginManager: ~/.safa/plugins, ./.safa/plugins, pip entry points; hooks pre/post_tool_call, pre/post_llm_call, session start/end; ctx.register_tool/register_cli_command), providers/__init__.py (lazy provider discovery, last-writer-wins), plugins/memory/<provider>/, plugins/model-providers/<name>/
entrypoints: discovered on model_tools import (general) or first get_provider_profile call (model-providers)
responsibilities: lifecycle hooks, extra tools/CLI commands, image-gen & context-engine provider dirs follow same ABC+orchestrator pattern
invariants: plugins MUST NOT modify core files — extend the generic surface instead (rule attributed Teknium May 2026; PR #5295 removed hardcoded honcho argparse); PluginManager records but does not import kind:model-provider manifests (double-instantiation)
pitfalls: discover_plugins() only runs as a side effect of importing model_tools.py
confidence: high

### safa-cloud — Operator-run SaaS backend
purpose: the ONLY internet endpoint devices talk to — inference proxy, metering, quota/credits, billing, auth.
path_prefixes: mythos-cloud/
key_files: app/quota.py (pure decision logic, fully unit-tested), app/proxy.py (pre-flight gate sequence), app/upstream.py (server-side keys), app/db.py (SupabaseDB prod / FakeDB tests), app/auth.py, app/credits.py, app/throttle.py, app/main.py, migrations/000{1,2,3}*.sql + 01xx_postgres_schema.sql
entrypoints: FastAPI app.main:app; ASGI via root index.py on Vercel (maxDuration=60); run-local.sh (127.0.0.1:8099)
responsibilities: /v1/chat/completions streaming proxy, model authorization per plan, usage events/counters, credit ledger, Stripe checkout+webhook, device-link pairing flow
invariants: privacy posture — aggregate usage only, never message content/memory/files; proxy doesn't persist prompts/completions by default (mythos-cloud/README.md, doc 06 §4); kill-switch/quota before real users
pitfalls: recent_request_count rate-limit was a stub in SupabaseDB (README admits; edge limiter needed); uuid/numeric/date casts needed for Postgres (git eb2fc69); pool resilience fixed intermittent device-link 500s (f8870a7)
confidence: high

### connectors — Google/Microsoft account integrations
purpose: first-class calendar/email/tasks/drive/contacts tools with OAuth.
path_prefixes: agent/connectors/, agent/google_connector_oauth.py, agent/microsoft_connector_oauth.py, tools/connector_tool.py
key_files: agent/connectors/google_{calendar,contacts,drive,gmail,tasks}.py, ms_{calendar,todo,outlook,onedrive}.py, shared _google_http/_ms_http
entrypoints: connector tool surfaced to agent; dashboard /api/connections OAuth flows
responsibilities: token refresh, explicit provider choice (ce87003 fixed always-Google bug), id-based update/delete + status vocabulary tolerance (0539422, 0b23d97)
invariants: listed in SHIFT.md as features to preserve completely
confidence: high

### security-sandbox — Filesystem boundary & approval
purpose: guarantee the agent cannot touch anything outside its workspace; human-in-the-loop for dangerous ops.
path_prefixes: safa_sandbox/, safa_privacy/, tools/path_security.py, tools/approval.py, agent/file_safety.py, tools/checkpoint_manager.py
key_files: safa_sandbox/pathguard.py, safa_sandbox/runtime.py, safa_sandbox/config.py
entrypoints: active in every tool call path (validator before execution)
responsibilities: write_root enforcement (~/.safa/workspace), read allowlist, trash soft-delete, command approval patterns, DM pairing for messaging
invariants: launch-blocking per docs — ship OS-level isolation AND app-layer guard together (doc 05); zero-egress mandate verified by packet capture (doc 12)
confidence: medium-high (app-layer code confirmed; OS-level enforcement details not read)

### research-rl — Batch generation & RL environments
purpose: trajectory generation/compression and Atropos RL training envs (research heritage from Hermes).
path_prefixes: environments/, batch_runner.py, trajectory_compressor.py, toolset_distributions.py, rl_cli.py, mini_swe_runner.py
key_files: environments/hermes_base_env.py, agentic_opd_env.py, web_research_env.py
entrypoints: rl_cli.py; [rl] extra (atroposlib/tinker pinned git SHAs)
responsibilities: parallel batch runs, tool-call parsers, benchmark harnesses (yc-bench extra)
pitfalls: doc 06 originally mandated REMOVING these as Nous data-collection pipelines; they survive as opt-in research tooling [inferred — kept but decoupled from product defaults]
confidence: medium

### docs-sites — Documentation & web presence
purpose: user/developer docs (Docusaurus), marketing/install site, and the internal AI-authored build-spec package.
path_prefixes: website/, mythos-web/, mythos-docs/, docs/
key_files: mythos-docs/00-MASTER-build-spec.md + 01–14 (architecture, cloud API, DB schema, sandbox, privacy, i18n/RTL, rebrand checklist, testing), mythos-web/package.json ("safaeb"), website/docs/** (published docs source)
entrypoints: deploy-site.yml (Vercel hook) / GH Pages; npm build per site
responsibilities: extract-skills/generate-skill-docs scripts sync skill docs into site; Arabic localization + RTL (i18n toggle, git a246e5c/f1243ca)
confidence: medium-high

## FLOWS

### Chat turn with tool call (any surface)
trigger: user message via CLI, TUI, dashboard WS, or gateway adapter.
steps: surface → AIAgent.run_conversation → chat.completions.create(tools=schemas) → if tool_calls: handle_function_call (plugin pre/post hooks, sandbox validator, tool exec in terminal backend) → tool result appended → repeat until content-only response or budget/interrupt.
files: run_agent.py, model_tools.py, tools/registry.py, tools/environments/*
confidence: high

### Messaging gateway turn
trigger: platform webhook/polling delivers message to bot.
steps: adapter receives → guard 1 (base.py queues if session active) → guard 2 (run.py intercepts control commands) → session lookup → agent turn → delivery.py replies to platform; background-process completions trigger new turns via watcher.
files: gateway/run.py, gateway/platforms/base.py, gateway/session.py, gateway/delivery.py
confidence: high

### Cloud proxied inference
trigger: agent issues chat-completions with bearer = Safa session token (device holds no provider keys).
steps: POST /v1/chat/completions → validate session → check quota/rate/concurrency → route upstream with server-side key → meter tokens (usage_event + counter RPC) → stream back; breach → 402/429 {code:"quota_exceeded"}; kill-switch hard-disables.
files: mythos-cloud/app/proxy.py, quota.py, upstream.py, db.py
confidence: high

### Device-link auth
trigger: fresh install login.
steps: device POST /auth/device/start (shows code) → user approves in web/app → device polls /auth/device/poll → approved → session token stored in ~/.safa/auth.json (0600).
files: mythos-cloud/app/auth.py, safa_cli/auth.py, mythos-docs/02-mythos-cloud-api.md
confidence: medium-high

### Cron job fire
trigger: scheduler tick (file-locked).
steps: due jobs selected → catchup/grace window math → spawn headless agent session (skip_memory, 3-min hard interrupt) → optional pre-run script stdout injected → output delivered to configured platforms → stored in dedicated cron session.
files: cron/scheduler.py, cron/jobs.py
confidence: high

### Dashboard chat (PTY embed)
trigger: user opens /chat in dashboard.
steps: xterm.js connects /api/pty?token=… → server spawns `safa --tui` child via ptyprocess → raw byte frames both ways → resize escape applied via TIOCSWINSZ.
files: safa_cli/web_server.py (@app.websocket("/api/pty")), safa_cli/pty_bridge.py, web/src/pages/ChatPage.tsx
confidence: high

## APIS
Cloud (mythos-cloud/app/main.py):

| Method | Path | Purpose |
|---|---|---|
| GET | /health | liveness (+?db=1 backend ping) |
| POST | /auth/signup, /auth/login, /auth/logout, /auth/refresh | email auth |
| POST | /auth/device/start, /auth/device/poll, /auth/device/approve | device-link pairing |
| GET | /v1/models | plan-allowed models |
| POST | /v1/chat/completions | OpenAI-compatible streaming inference proxy |
| GET | /v1/usage | aggregate usage for account |
| GET/POST | /v1/billing/checkout, /v1/credits | Stripe checkout; credit balance |
| POST | /webhooks/stripe | subscription/billing events |

Dashboard (safa_cli/web_server.py, ~60 routes, token-authed, localhost): /api/config(+raw,schema,defaults), /api/env (GET/POST/DELETE + reveal), /api/sessions (+search, messages, descendants), /api/skills, /api/tools/toolsets, /api/cron/jobs CRUD + pause/resume/trigger, /api/profiles CRUD + soul + open-terminal, /api/model/{info,options,set,auxiliary}, /api/providers/oauth*, /api/connections* (OAuth connect/disconnect/status), /api/dashboard/plugins* + /api/dashboard/agent-plugins* (enable/disable/update/install), /api/logs, /api/execution-logs, /api/analytics/{usage,models}, /api/status, /api/capabilities, /api/actions/{name}/status, /api/gateway/restart, /api/mythos/update, /api/update, WS /api/pty.
Other surfaces: gateway api_server platform (OpenAI-ish HTTP on device), acp_adapter (ACP protocol for VS Code/Zed/JetBrains), mcp_serve.py (MCP server), tui_gateway JSON-RPC method catalog (server.py). Convention: dashboard routes all under /api; cloud under /auth,/v1,/webhooks; errors as machine-readable envelopes {code:...}.

## DATABASE
Engines: SQLite (device, multiple stores) + Postgres (cloud: Supabase schema for dev, Neon for prod [inferred from migrations + git]).
Device SQLite:
- SessionDB (safa_state.py): `sessions` (id, platform ids, timestamps, metadata — resume support), `messages` (role/content per session), `state_meta` kv, `schema_version`, FTS5 virtual tables `messages_fts` + `messages_fts_trigram` (session_search tool w/ LLM summarization), telegram_dm_topic_mode/bindings (DM topic routing). Beets/sqlite-utils-style additive migration pattern (schema_version-guarded).
- Kanban (safa_cli/kanban_db.py:751+): `tasks` (board items: status/assignee/heartbeat), `task_links` (deps), `task_comments`, `task_events` (audit), `task_runs` (spawn records), `kanban_notify_subs`.
Other device files-as-DB: config.yaml, auth.json (0600), server.json, skills_state.json, skills/.usage.json, checkpoints, cron store, workspace/.
Cloud Postgres (migrations): `plans`, `models`, `plan_models` (plan↔model authz), `profiles` (Supabase) / `users`+`sessions` (0100 Neon variant), `device_sessions` (pairing), `subscriptions` (Stripe), `usage_events` (per-request tokens/cost), `usage_counters` (period aggregates, atomic increment RPC), `credit_ledger` (0003/0100 credits). RLS policies + quota_status() per doc 03.
Vector stores: NONE in-repo [verified by absence]; semantic recall = FTS5 + LLM summarize; optional external memory via provider plugins (honcho/mem0 etc.) which may bring their own stores.

## TESTS
Frameworks: pytest (pytest-xdist, pytest-asyncio, pytest-cov; addopts `-m 'not integration' -n auto`; marker `integration` = needs external services). Vitest for ui-tui. Plain pytest for mythos-cloud/tests (13 pure-logic tests, no network).
Commands: ALWAYS `scripts/run_tests.sh [path|-k flags]` — enforces CI parity (unsets credential env vars, TZ=UTC, LANG=C.UTF-8, -n 4 matching GHA); direct pytest diverges (documented incidents). Frontend: `cd ui-tui && npm run type-check|lint|test`.
Layout: tests/ mirrors packages — tests/{agent,cli,gateway,cron,acp,acp_adapter,plugins,providers,skills,e2e,integration,stress,fakes,run_agent,mythos_cli,mythos_state,safa_cloud,safa_onboarding,safa_privacy,safa_sandbox,honcho_plugin,openviking_plugin} plus many top-level regression files. conftest.py has autouse `_isolate_mythos_home` (SAFA_HOME→tmp) — tests must never write ~/.safa.
Mapping examples: gateway behavior → tests/gateway/; profiles → tests/mythos_cli/test_profiles-style fixtures (mock Path.home + SAFA_HOME); curator/skills → tests/skills/; cloud logic → mythos-cloud/tests/.
Policy (AGENTS.md): NO change-detector tests (snapshot catalogs/config versions/counts forbidden) — assert relationships/invariants instead. ~977 test_*.py files, ~20,299 test functions [grep-counted].

## GIT LESSONS
- **Global renames are dangerous**: b744782 "deep rename mythos→safa (package, modules, env, home, dist)" immediately followed by dcf5166 "fix: recover repo from corrupted global mythos→safa replace" and d2db7d2 cleanup; later 187082a had to restore skill-frontmatter 'mythos' schema key, 7655be2 fixed wrong outDir (SAFA_cli vs safa). Lesson: scripted whole-repo renames leave long tails; verify shipped artifacts.
- **Squash-merging stale branches silently reverts main's fixes** — documented pitfall (AGENTS.md): refresh branch onto origin/main before squash; red flag = unexpected deletions in `git diff HEAD~1..HEAD`.
- **Deploy pattern**: scripts/deploy.sh stamps BUILD_ID (safa_cli/_build_id.py) + latest.json {build, version, rollout%, install URL}, rebuilds dashboard+wheel, pushes to VPS; each deploy lands a `chore(deploy): ship build YYYYMMDDHHMMSS (<change>, rollout N%)` commit (15e9faf, ee1aded, …). Silent-update rollout percentage gates the update banner. (Deploy target credentials/IPs intentionally omitted.)
- **Native-dep pins**: 283dbe0 pin svglib<1.6 because 1.6 pulled pycairo→system cairo breaking fresh installs; voice extra kept out of termux extra for same reason; requests/PyJWT pinned with CVE comments (supply-chain posture; osv-scanner CI).
- **Reliability fixes worth remembering**: f8870a7 resilient Neon pool (intermittent device-link 500s), eb2fc69 cast uuid/numeric/date in Postgres SQL, 62cfac3/481cc72 browser crash self-heal, ce87003 explicit provider choice honored.
- **Dead code discipline**: AGENTS.md warns unused modules were dead for a reason — E2E-validate resolution chain with real imports against temp SAFA_HOME before wiring in.
- History starts at 027c668 (single initial import) — upstream Hermes history not retained.

## DECISIONS
- **Fork-and-rebrand Hermes as SaaS** — context: wanted productized self-improving agent w/o BYO-keys — decision: fork v0.13.0, rebrand, proxy all inference through own cloud, web-first UI, preserve learning loop verbatim — evidence: mythos-docs/00-INDEX.md, 09-rebrand-checklist.md, 10-self-improvement-preservation.md, git 027c668/b744782.
- **Zero telemetry egress** — context: upstream partly a training-data pipeline — decision: strip every egress path (trajectories, checkpoint upload, analytics, phone-home), verify by packet capture, launch-blocking — evidence: mythos-docs/06-privacy-and-telemetry-removal.md, scripts/strip_nous_egress.py, safa_privacy/.
- **Local agent + cloud brain trust split** — device holds only session token; provider keys server-side only; single-tenant on device, multi-tenant hardening in cloud — evidence: mythos-docs/01-architecture.md §2, mythos-cloud/README.md.
- **Filesystem sandbox is dual-layer** — OS-level isolation + app-layer pathguard shipped together, neither alone — evidence: mythos-docs/05-security-and-sandboxing.md, safa_sandbox/pathguard.py.
- **Plugin surface instead of core edits** — context: hardcoded honcho argparse in main.py — decision: expand generic hooks/ctx; PR #5295 removed 95 hardcoded lines; rule: plugins must not modify core — evidence: AGENTS.md Plugins section.
- **Prompt-cache preservation over freshness** — slash commands mutating system-prompt state default to deferred invalidation with opt-in --now — evidence: AGENTS.md Important Policies, /skills install --now pattern.
- **Dashboard embeds the real TUI** — no second chat implementation in React; PTY bridge carries `safa --tui` to xterm.js — evidence: AGENTS.md TUI-in-dashboard section, safa_cli/pty_bridge.py.
- **Hermetic test wrapper** — context: repeated works-locally-fails-CI incidents — decision: scripts/run_tests.sh normalizes env/keys/TZ/locale/workers; change-detector tests banned — evidence: AGENTS.md Testing section.
- **Lazy provider-plugin discovery separate from PluginManager** — avoids double ProviderProfile instantiation; user plugins override bundled (last-writer-wins) — evidence: AGENTS.md model-provider plugins, providers/__init__.py.

## RISKS & TECH DEBT
- God-files: run_agent.py 14,681 / gateway/run.py 15,436 / cli.py 12,577 LOC — merge-conflict and regression hotspot; three config loaders (cli.py vs safa_cli/config.py vs gateway raw YAML) already caused drift bugs (documented).
- Linting effectively off: `[tool.ruff] select = []` ("until we've wrangled typechecks"); ty targets py3.13 while floor is 3.11.
- pytest addopts `-n auto` conflicts with CI-parity guidance (-n 4) unless wrapper used.
- Rate limiting stub in cloud SupabaseDB (`recent_request_count`) — README says Redis/edge limiter still needed before scale.
- Two parallel Postgres schema families (Supabase 0001-0003 vs Neon 0100+) — divergence risk between dev and prod schemas.
- Rename debt: mixed branding residue (dir name mythos, container_name mythos, mythos-* dirs, /api/mythos/update route, mythos-achievements plugin) vs safa code namespace — greps for either name needed when auditing.
- Doc volume (964 md) includes duplicated/stale layers: mythos-docs build-spec describes an earlier target architecture (e.g., demote terminal UI; Supabase) that drifted from reality (TUI prominent, Neon/Vercel prod) — treat AGENTS.md > mythos-docs > website for current truth.
- deploy.sh defaults embed privileged remote-target assumptions in-repo (credentials omitted here); docker-compose uses network_mode: host.
- Test suite size (~20k functions) implies slow full runs; stress/integration tiers exist but rely on marker hygiene.
- Process-global mutable state (`_last_resolved_tool_names`, skin singleton) — concurrency hazards around subagents.

## UNCERTAIN
- Prod cloud topology today (Vercel vs VPS for mythos-cloud; Supabase vs Neon live) — inferred Neon/Vercel from migrations + commits f8870a7/299c143/cf17903; docs say AWS/Fly/Render possible.
- Exact split between `web/` (wheel-embedded dashboard) and `mythos-web/` (marketing/install site, "safaeb") at runtime [inferred from deploy.sh writing latest.json into mythos-web/public].
- Whether OS-level sandbox enforcement (containers/user separation) is fully implemented vs only app-layer pathguard — doc 05 mandates both; only app-layer code located.
- AGENTS.md cites "~17k tests (May 2026)" vs measured 20,299 defs — growth or counting-method difference.
- Whether RL/trajectory egress was fully neutralized in product defaults (doc 06 demanded removal; modules still present as research extras).
- safa_privacy/ contains only __init__.py — whether it is vestigial or placeholder for enforcement code.
