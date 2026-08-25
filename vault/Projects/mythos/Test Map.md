---
cortex-generated: true
title: mythos tests
tags: [tests/project]
---

# mythos — Test Map

1090 test files.

| Kind | Count |
|---|---|
| e2e | 5 |
| integration | 17 |
| unit | 1068 |

## e2e (5)

- `tests/e2e/__init__.py`
- `tests/e2e/conftest.py` — covers 1 targets
- `tests/e2e/matrix_xsign_bootstrap/test_bootstrap.py`
- `tests/e2e/test_discord_adapter.py`
- `tests/e2e/test_platform_commands.py`

## integration (17)

- `skills/creative/comfyui/tests/test_cloud_integration.py`
- `tests/agent/test_bedrock_integration.py`
- `tests/cli/test_cli_skin_integration.py`
- `tests/gateway/test_webhook_integration.py`
- `tests/integration/__init__.py`
- `tests/integration/test_batch_runner.py`
- `tests/integration/test_checkpoint_resumption.py`
- `tests/integration/test_daytona_terminal.py`
- `tests/integration/test_ha_integration.py`
- `tests/integration/test_modal_terminal.py`
- `tests/integration/test_voice_channel_flow.py`
- `tests/integration/test_web_tools.py`
- `tests/safa_sandbox/test_file_safety_integration.py` — covers 1 targets
- `tests/test_cli_skin_integration.py`
- `tests/test_yuanbao_integration.py`
- `tests/tools/test_mcp_oauth_integration.py`
- `tests/tools/test_voice_cli_integration.py` — covers 1 targets

## unit (1068)

- `mythos-cloud/tests/__init__.py`
- `mythos-cloud/tests/test_credits.py`
- `mythos-cloud/tests/test_endpoints.py`
- `mythos-cloud/tests/test_proxy_endpoints.py`
- `mythos-cloud/tests/test_proxy_logic.py`
- `mythos-cloud/tests/test_reservation.py`
- `mythos-cloud/tests/test_throttle.py`
- `plugins/mythos-achievements/tests/test_achievement_engine.py`
- `skills/creative/comfyui/tests/conftest.py`
- `skills/creative/comfyui/tests/test_check_deps.py`
- `skills/creative/comfyui/tests/test_common.py`
- `skills/creative/comfyui/tests/test_extract_schema.py`
- `skills/creative/comfyui/tests/test_run_workflow.py`
- `tests/__init__.py`
- `tests/acp/__init__.py`
- `tests/acp/conftest.py`
- `tests/acp/test_approval_isolation.py`
- `tests/acp/test_auth.py`
- `tests/acp/test_entry.py` — covers 1 targets
- `tests/acp/test_events.py`
- `tests/acp/test_mcp_e2e.py`
- `tests/acp/test_permissions.py`
- `tests/acp/test_ping_suppression.py`
- `tests/acp/test_server.py` — covers 1 targets
- `tests/acp/test_session.py` — covers 1 targets
- `tests/acp/test_tools.py`
- `tests/acp_adapter/conftest.py`
- `tests/acp_adapter/test_acp_commands.py`
- `tests/acp_adapter/test_acp_images.py`
- `tests/agent/__init__.py`
- `tests/agent/test_anthropic_adapter.py`
- `tests/agent/test_anthropic_keychain.py`
- `tests/agent/test_arcee_trinity_overrides.py`
- `tests/agent/test_auxiliary_client.py` — covers 1 targets
- `tests/agent/test_auxiliary_client_anthropic_custom.py`
- `tests/agent/test_auxiliary_config_bridge.py` — covers 1 targets
- `tests/agent/test_auxiliary_main_first.py` — covers 1 targets
- `tests/agent/test_auxiliary_named_custom_providers.py`
- `tests/agent/test_auxiliary_transport_autodetect.py`
- `tests/agent/test_bedrock_1m_context.py` — covers 1 targets
- `tests/agent/test_bedrock_adapter.py`
- `tests/agent/test_capability_and_guard.py` — covers 4 targets
- `tests/agent/test_codex_cloudflare_headers.py` — covers 1 targets
- `tests/agent/test_compress_focus.py`
- `tests/agent/test_compressor_image_tokens.py`
- `tests/agent/test_connector_security.py` — covers 1 targets
- `tests/agent/test_context_compressor.py`
- `tests/agent/test_context_compressor_summary_continuity.py`
- `tests/agent/test_context_engine.py` — covers 1 targets
- `tests/agent/test_context_references.py`
- …and 1018 more

## High-importance code with no obvious mapped test

_Heuristic (name/import match). Verify before treating as gaps._

- `scripts/whatsapp-bridge/bridge.js`
- `mythos-web/src/anim/primitives.tsx`
- `mythos-web/src/components/Logo.tsx`
- `mythos-web/src/components/LegalLayout.tsx`
- `mythos-web/src/pages/Login.tsx`
- `mythos-web/src/pages/Pair.tsx`
- `mythos-web/src/pages/Signup.tsx`
- `Safa_cli/web_dist/assets/index-C6Vqytab.js`
- `safa_cli/web_dist/assets/index-CKjYOpnK.js`
- `web/src/i18n/types.ts`
- `scripts/whatsapp-bridge/allowlist.js`
- `ui-tui/packages/mythos-ink/src/ink/global.d.ts`
- `web/src/contexts/page-header-context.ts`
- `web/src/contexts/system-actions-context.ts`
- `mythos-web/src/components/AuthShell.tsx`
- `tools/discord_tool.py`
- `ui-tui/src/app/overlayStore.ts`
- `ui-tui/src/app/turnStore.ts`
- `ui-tui/src/app/uiStore.ts`
- `web/src/plugins/slots.ts`
- `web/src/plugins/types.ts`
- `mythos-web/src/App.tsx`
- `mythos-web/src/components/ConnectorsStrip.tsx`
- `mythos-web/src/components/CookieConsent.tsx`
- `mythos-web/src/components/Features.tsx`
