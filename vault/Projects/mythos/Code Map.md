---
cortex-generated: true
title: mythos code map
tags: [codemap/project]
---

# mythos — Code Map

## Directory layout (indexed files)

- `tests/` — 1016 files
- `ui-tui/` — 303 files
- `web/` — 99 files
- `tools/` — 91 files
- `plugins/` — 80 files
- `agent/` — 77 files
- `safa_cli/` — 72 files
- `gateway/` — 58 files
- `skills/` — 49 files
- `environments/` — 30 files
- `mythos-web/` — 29 files
- `mythos-cloud/` — 23 files
- `optional-skills/` — 23 files
- `scripts/` — 13 files
- `acp_adapter/` — 9 files
- `tui_gateway/` — 8 files
- `website/` — 8 files
- `safa_localserver/` — 4 files
- `safa_sandbox/` — 4 files
- `cron/` — 3 files
- `installer/` — 3 files
- `providers/` — 2 files
- `Safa_cli/` — 1 files
- `batch_runner.py/` — 1 files
- `cli.py/` — 1 files
- `locales/` — 1 files
- `mcp_serve.py/` — 1 files
- `mini_swe_runner.py/` — 1 files
- `model_tools.py/` — 1 files
- `rl_cli.py/` — 1 files

## Entry points

- `mythos-cloud/app/main.py`
- `safa_cli/main.py`
- `run_agent.py`
- `web/src/i18n/index.ts`
- `web/src/plugins/index.ts`
- `installer/windows/main.go`
- `ui-tui/packages/mythos-ink/index.js`
- `acp_adapter/__main__.py`
- `ui-tui/packages/mythos-ink/src/native-ts/yoga-layout/index.ts`

## Most-connected symbols (fan-in leaders)

| Symbol | Kind | Location |
|---|---|---|
| `AL` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:49` |
| `wL` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:49` |
| `_a` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:47` |
| `Be` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:47` |
| `ve` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:47` |
| `x` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:47` |
| `p` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:47` |
| `f` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:47` |
| `a` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:47` |
| `S5` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:43` |
| `qp` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:28` |
| `yv` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:28` |
| `jR` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:16` |
| `bn` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:16` |
| `Rp` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:15` |
| `In` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:15` |
| `po` | class | `Safa_cli/web_dist/assets/index-C6Vqytab.js:15` |
| `$z` | function | `Safa_cli/web_dist/assets/index-C6Vqytab.js:50` |
| `Pz` | function | `Safa_cli/web_dist/assets/index-C6Vqytab.js:50` |
| `N0` | function | `Safa_cli/web_dist/assets/index-C6Vqytab.js:50` |
| `Bz` | function | `Safa_cli/web_dist/assets/index-C6Vqytab.js:50` |
| `Uz` | function | `Safa_cli/web_dist/assets/index-C6Vqytab.js:50` |
| `Iz` | function | `Safa_cli/web_dist/assets/index-C6Vqytab.js:50` |
| `Dz` | function | `Safa_cli/web_dist/assets/index-C6Vqytab.js:50` |
| `Oz` | function | `Safa_cli/web_dist/assets/index-C6Vqytab.js:50` |
| `jz` | function | `Safa_cli/web_dist/assets/index-C6Vqytab.js:50` |
| `Mz` | function | `Safa_cli/web_dist/assets/index-C6Vqytab.js:50` |
| `Az` | function | `Safa_cli/web_dist/assets/index-C6Vqytab.js:50` |
| `Cz` | function | `Safa_cli/web_dist/assets/index-C6Vqytab.js:50` |
| `kz` | function | `Safa_cli/web_dist/assets/index-C6Vqytab.js:50` |

## Highest-importance files

- `safa_cli/web_server.py` (4175 loc)
- `gateway/run.py` (15437 loc)
- `plugins/kanban/dashboard/plugin_api.py` (1537 loc)
- `safa_cli/kanban_db.py` (4387 loc)
- `tools/browser_tool.py` (4234 loc)
- `cli.py` (12578 loc)
- `mythos-cloud/app/main.py` (632 loc)
- `utils.py` (298 loc)
- `safa_cli/config.py` (5162 loc)
- `safa_cli/plugins.py` (1367 loc)
- `safa_cli/auth.py` (5342 loc)
- `tools/kanban_tools.py` (872 loc)
- `safa_cli/main.py` (11005 loc)
- `tools/web_tools.py` (2224 loc)
- `tools/skill_usage.py` (610 loc)
- `plugins/google_meet/node/protocol.py` (125 loc)
- `run_agent.py` (14682 loc)
- `safa_cli/gateway.py` (4891 loc)
- `safa_localserver/workspace_api.py` (136 loc)
- `tools/mcp_tool.py` (3404 loc)
- `safa_cli/tools_config.py` (2557 loc)
- `plugins/google_meet/process_manager.py` (327 loc)
- `safa_cli/curator.py` (590 loc)
- `scripts/whatsapp-bridge/bridge.js` (707 loc)
- `tools/approval.py` (1259 loc)