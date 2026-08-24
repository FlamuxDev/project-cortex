---
cortex-generated: true
title: terminal-cli-subcommand-framework
tags: [module]
---

# Terminal CLI + subcommand framework

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `cli.py,safa_cli/`

purpose: interactive prompt_toolkit/Rich chat UI, slash commands, setup wizard, config, all `safa <verb>` subcommands.
path_prefixes: cli.py, safa_cli/
key_files: cli.py (12.6k LOC, SafaCLI.process_command), safa_cli/commands.py (central COMMAND_REGISTRY — single source feeding CLI dispatch, gateway hooks, Telegram menu, Slack map, autocomplete), safa_cli/config.py (DEFAULT_CONFIG + _config_version migrations + OPTIONAL_ENV_VARS), safa_cli/skin_engine.py, safa_cli/curses_ui.py, safa_cli/kanban.py, safa_cli/curator.py, safa_cli/claw.py (OpenClaw migration)
entrypoints: `safa` console script
responsibilities: config load/merge (three distinct loaders — cli.py vs safa_cli/config.py vs raw YAML in gateway), wizard, backups/checkpoints
invariants: new slash command = CommandDef entry + handler(s); profile safety via get_safa_home()/display_safa_home(), never hardcode ~/.safa; no new simple_term_menu (curses instead)
pitfalls: adding a key to the wrong loader makes it invisible to CLI or gateway; config-version bumps only for destructive renames
confidence: high

## Files (40+)

- `Safa_cli/web_dist/assets/index-C6Vqytab.js`
- `cli.py`
- `plugins/google_meet/cli.py`
- `plugins/google_meet/node/cli.py`
- `plugins/memory/honcho/cli.py`
- `safa_cli/__init__.py`
- `safa_cli/_build_id.py`
- `safa_cli/_parser.py`
- `safa_cli/auth.py`
- `safa_cli/auth_commands.py`
- `safa_cli/azure_detect.py`
- `safa_cli/backup.py`
- `safa_cli/banner.py`
- `safa_cli/browser_connect.py`
- `safa_cli/callbacks.py`
- `safa_cli/checkpoints.py`
- `safa_cli/claw.py`
- `safa_cli/cli_output.py`
- `safa_cli/clipboard.py`
- `safa_cli/codex_models.py`
- `safa_cli/colors.py`
- `safa_cli/commands.py`
- `safa_cli/completion.py`
- `safa_cli/config.py`
- `safa_cli/copilot_auth.py`

## API surface

- `DELETE index`
- `GET /api/status`
- `POST /api/gateway/restart`
- `POST /api/mythos/update`
- `GET /api/actions/{name}/status`
- `GET /api/sessions`
- `GET /api/sessions/search`
- `GET /api/config`
- `GET /api/config/defaults`
- `GET /api/config/schema`
- `GET /api/model/info`
- `GET /api/model/options`
- `GET /api/model/auxiliary`
- `POST /api/model/set`
- `PUT /api/config`
