---
cortex-generated: true
title: mythos api
tags: [api/project]
---

# mythos — API Surface

140 routes. Grouped by owning file; every route names its handler.

## `Safa_cli/web_dist/assets/index-C6Vqytab.js`
*module: [[mythos/modules/Terminal-Cli-Subcommand-Framework|terminal-cli-subcommand-framework]]*

- **DELETE** `index`

## `mythos-cloud/app/main.py`
*module: [[mythos/modules/Operator-Run-Saas-Backend|operator-run-saas-backend]]*

- **POST** `/auth/device/approve` → device_approve
- **POST** `/auth/device/poll` → device_poll
- **POST** `/auth/device/start` → device_start
- **POST** `/auth/login` → login
- **POST** `/auth/logout` → logout
- **POST** `/auth/refresh` → refresh
- **POST** `/auth/signup` → signup
- **GET** `/health` → health
- **POST** `/v1/billing/checkout` → checkout
- **POST** `/v1/chat/completions` → chat_completions
- **GET** `/v1/credits` → credits
- **GET** `/v1/models` → list_models
- **GET** `/v1/usage` → usage
- **POST** `/webhooks/stripe` → stripe_webhook

## `mythos-web/src/pages/Login.tsx`
*module: [[mythos/modules/Documentation-Web-Presence|documentation-web-presence]]*

- **GET** `next`

## `mythos-web/src/pages/Pair.tsx`
*module: [[mythos/modules/Documentation-Web-Presence|documentation-web-presence]]*

- **GET** `code`

## `mythos-web/src/pages/Signup.tsx`
*module: [[mythos/modules/Documentation-Web-Presence|documentation-web-presence]]*

- **GET** `next`

## `plugins/example-dashboard/dashboard/plugin_api.py`
*module: [[mythos/modules/Plugins-Model-Providers|plugins-model-providers]]*

- **GET** `/hello` → hello

## `plugins/kanban/dashboard/plugin_api.py`
*module: [[mythos/modules/Multi-Agent-Work-Board|multi-agent-work-board]]*

- **GET** `/assignees` → get_assignees
- **GET** `/board` → get_board
- **GET** `/boards` → list_boards
- **POST** `/boards` → create_board_endpoint
- **PATCH** `/boards/{slug}` → rename_board
- **DELETE** `/boards/{slug}` → delete_board
- **POST** `/boards/{slug}/switch` → switch_board
- **GET** `/config` → get_config
- **GET** `/diagnostics` → list_diagnostics
- **POST** `/dispatch` → dispatch
- **GET** `/home-channels` → get_home_channels
- **POST** `/links` → add_link
- **DELETE** `/links` → delete_link
- **GET** `/stats` → get_stats
- **POST** `/tasks` → create_task
- **POST** `/tasks/bulk` → bulk_update
- **GET** `/tasks/{task_id}` → get_task
- **PATCH** `/tasks/{task_id}` → update_task
- **POST** `/tasks/{task_id}/comments` → add_comment
- **POST** `/tasks/{task_id}/home-subscribe/{platform}` → subscribe_home
- **DELETE** `/tasks/{task_id}/home-subscribe/{platform}` → unsubscribe_home
- **GET** `/tasks/{task_id}/log` → get_task_log
- **POST** `/tasks/{task_id}/reassign` → reassign_task_endpoint
- **POST** `/tasks/{task_id}/reclaim` → reclaim_task_endpoint

## `plugins/mythos-achievements/dashboard/plugin_api.py`
*module: [[mythos/modules/Plugins-Model-Providers|plugins-model-providers]]*

- **GET** `/achievements` → achievements
- **GET** `/recent-unlocks` → recent_unlocks
- **POST** `/rescan` → rescan
- **POST** `/reset-state` → reset_state
- **GET** `/scan-status` → scan_status
- **GET** `/sessions/{session_id}/badges` → session_badges

## `safa_cli/web_dist/assets/index-CKjYOpnK.js`
*module: [[mythos/modules/Terminal-Cli-Subcommand-Framework|terminal-cli-subcommand-framework]]*

- **DELETE** `index`

## `safa_cli/web_server.py`
*module: [[mythos/modules/Terminal-Cli-Subcommand-Framework|terminal-cli-subcommand-framework]]*

- **GET** `/api/actions/{name}/status` → get_action_status
- **GET** `/api/analytics/models` → get_models_analytics
- **GET** `/api/analytics/usage` → get_usage_analytics
- **GET** `/api/capabilities` → list_capabilities
- **GET** `/api/config` → get_config
- **PUT** `/api/config` → update_config
- **GET** `/api/config/defaults` → get_defaults
- **GET** `/api/config/raw` → get_config_raw
- **PUT** `/api/config/raw` → update_config_raw
- **GET** `/api/config/schema` → get_schema
- **GET** `/api/connections` → list_connections
- **POST** `/api/connections/{connection_id}/disconnect` → disconnect_connection
- **POST** `/api/connections/{connection_id}/oauth/start` → start_connection_oauth
- **GET** `/api/connections/{connection_id}/oauth/status` → connection_oauth_status
- **GET** `/api/cron/jobs` → list_cron_jobs
- **POST** `/api/cron/jobs` → create_cron_job
- **GET** `/api/cron/jobs/{job_id}` → get_cron_job
- **PUT** `/api/cron/jobs/{job_id}` → update_cron_job
- **DELETE** `/api/cron/jobs/{job_id}` → delete_cron_job
- **POST** `/api/cron/jobs/{job_id}/pause` → pause_cron_job
- **POST** `/api/cron/jobs/{job_id}/resume` → resume_cron_job
- **POST** `/api/cron/jobs/{job_id}/trigger` → trigger_cron_job
- **POST** `/api/dashboard/agent-plugins/install` → post_agent_plugin_install
- **DELETE** `/api/dashboard/agent-plugins/{name}` → delete_agent_plugin
- **POST** `/api/dashboard/agent-plugins/{name}/disable` → post_agent_plugin_disable
- **POST** `/api/dashboard/agent-plugins/{name}/enable` → post_agent_plugin_enable
- **POST** `/api/dashboard/agent-plugins/{name}/update` → post_agent_plugin_update
- **PUT** `/api/dashboard/plugin-providers` → put_plugin_providers
- **GET** `/api/dashboard/plugins` → get_dashboard_plugins
- **GET** `/api/dashboard/plugins/hub` → get_plugins_hub
- **GET** `/api/dashboard/plugins/rescan` → rescan_dashboard_plugins
- **POST** `/api/dashboard/plugins/{name}/visibility` → post_plugin_visibility
- **GET** `/api/env` → get_env_vars
- **PUT** `/api/env` → set_env_var
- **DELETE** `/api/env` → remove_env_var
- **POST** `/api/env/reveal` → reveal_env_var
- **GET** `/api/execution-logs` → list_execution_logs
- **POST** `/api/gateway/restart` → restart_gateway
- **GET** `/api/logs` → get_logs
- **GET** `/api/model/auxiliary` → get_auxiliary_models
- …and 33 more

## `safa_localserver/account_api.py`
*module: [[mythos/modules/Local-Web-Dashboard-Api|local-web-dashboard-api]]*

- **GET** `` → account
- **POST** `/logout` → logout

## `safa_localserver/workspace_api.py`
*module: [[mythos/modules/Local-Web-Dashboard-Api|local-web-dashboard-api]]*

- **GET** `/file` → read_file
- **PUT** `/file` → write_file
- **DELETE** `/file` → delete_file
- **POST** `/mkdir` → mkdir
- **POST** `/move` → move
- **POST** `/rename` → move
- **GET** `/tree` → tree
- **POST** `/upload` → upload

## `scripts/whatsapp-bridge/bridge.js`

- **GET** `/chat/:id` → `async`
- **POST** `/edit` → `async`
- **GET** `/health`
- **GET** `/messages`
- **POST** `/send` → `async`
- **POST** `/send-media` → `async`
- **POST** `/typing` → `async`
