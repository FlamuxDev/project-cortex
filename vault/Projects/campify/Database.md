---
cortex-generated: true
title: campify db
tags: [database/project]
---

# Campify — Database

109 entities.

## table (63)

- **ai_suggestions** — `packages/db/migrations/0018_ai_suggestions.sql`
- **api_keys** — `packages/db/migrations/0024_analytics.sql`
- **audit_log** — `packages/db/migrations/0006_audit.sql`
- **auth_audit_log** — `packages/db/migrations/0008_auth_audit_and_invites.sql`
- **campaign_approvals** — `packages/db/migrations/0015_campaigns.sql`
- **campaign_audience_members** — `packages/db/migrations/0015_campaigns.sql`
- **campaign_audience_snapshots** — `packages/db/migrations/0015_campaigns.sql`
- **campaign_audiences** — `packages/db/migrations/0015_campaigns.sql`
- **campaign_channels** — `packages/db/migrations/0015_campaigns.sql`
- **campaign_comments** — `packages/db/migrations/0015_campaigns.sql`
- **campaign_exclusions** — `packages/db/migrations/0015_campaigns.sql`
- **campaign_test_recipients** — `packages/db/migrations/0021_delivery.sql`
- **campaign_tracking_rules** — `packages/db/migrations/0015_campaigns.sql`
- **campaign_versions** — `packages/db/migrations/0015_campaigns.sql`
- **campaigns** — `packages/db/migrations/0015_campaigns.sql`
- **companies** — `packages/db/migrations/0034_crm.sql`
- **consent_records** — `packages/db/migrations/0003_consent.sql`
- **contact_fields** — `packages/db/migrations/0002_contacts.sql`
- **contact_tags** — `packages/db/migrations/0002_contacts.sql`
- **contacts** — `packages/db/migrations/0002_contacts.sql`
- **content_comments** — `packages/db/migrations/0016_content.sql`
- **content_items** — `packages/db/migrations/0016_content.sql`
- **content_templates** — `packages/db/migrations/0016_content.sql`
- **content_variants** — `packages/db/migrations/0016_content.sql`
- **content_versions** — `packages/db/migrations/0016_content.sql`
- **crm_activities** — `packages/db/migrations/0034_crm.sql`
- **deals** — `packages/db/migrations/0034_crm.sql`
- **delivery_attempts** — `packages/db/migrations/0021_delivery.sql`
- **emergency_stops** — `packages/db/migrations/0021_delivery.sql`
- **events** — `packages/db/migrations/0024_analytics.sql`
- **import_jobs** — `packages/db/migrations/0004_imports.sql`
- **import_rows** — `packages/db/migrations/0004_imports.sql`
- **in_review** — `packages/core/src/campaigns/state.unit.test.ts`
- **invitations** — `packages/db/migrations/0001_identity.sql`
- **journey_edges** — `packages/db/migrations/0022_journeys.sql`
- **journey_enrollments** — `packages/db/migrations/0022_journeys.sql`
- **journey_nodes** — `packages/db/migrations/0022_journeys.sql`
- **journey_step_executions** — `packages/db/migrations/0022_journeys.sql`
- **journey_versions** — `packages/db/migrations/0022_journeys.sql`
- **journeys** — `packages/db/migrations/0022_journeys.sql`
- **list_members** — `packages/db/migrations/0002_contacts.sql`
- **lists** — `packages/db/migrations/0002_contacts.sql`
- **memberships** — `packages/db/migrations/0001_identity.sql`
- **messages** — `packages/db/migrations/0021_delivery.sql`
- **pipeline_stages** — `packages/db/migrations/0034_crm.sql`
- **plans** — `packages/db/migrations/0033_plans_and_quotas.sql`
- **provider_delivery_events** — `packages/db/migrations/0032_provider_delivery_events.sql`
- **rate_limit_windows** — `packages/db/migrations/0021_delivery.sql`
- **sales_tasks** — `packages/db/migrations/0027_sales_tasks.sql`
- **segment_members** — `packages/db/migrations/0005_segments.sql`
- **segment_versions** — `packages/db/migrations/0005_segments.sql`
- **segments** — `packages/db/migrations/0005_segments.sql`
- **send_frequency** — `packages/db/migrations/0021_delivery.sql`
- **sessions** — `packages/db/migrations/0001_identity.sql`
- **suppressions** — `packages/db/migrations/0003_consent.sql`
- **tags** — `packages/db/migrations/0002_contacts.sql`
- **usage_counters** — `packages/db/migrations/0033_plans_and_quotas.sql`
- **users** — `packages/db/migrations/0001_identity.sql`
- **verification_tokens** — `packages/db/migrations/0001_identity.sql`
- **webhook_deliveries** — `packages/db/migrations/0029_webhooks.sql`
- **webhook_subscriptions** — `packages/db/migrations/0029_webhooks.sql`
- **workspace_plans** — `packages/db/migrations/0033_plans_and_quotas.sql`
- **workspaces** — `packages/db/migrations/0001_identity.sql`

## type (21)

- **approval_decision** — `packages/db/migrations/0015_campaigns.sql`
- **attribution_model** — `packages/db/migrations/0035_attribution_defaults.sql`
- **campaign_objective** — `packages/db/migrations/0015_campaigns.sql`
- **campaign_status** — `packages/db/migrations/0015_campaigns.sql`
- **channel** — `packages/db/migrations/0003_consent.sql`
- **consent_status** — `packages/db/migrations/0003_consent.sql`
- **contact_field_type** — `packages/db/migrations/0002_contacts.sql`
- **crm_activity_kind** — `packages/db/migrations/0034_crm.sql`
- **deal_status** — `packages/db/migrations/0034_crm.sql`
- **exclusion_kind** — `packages/db/migrations/0015_campaigns.sql`
- **import_status** — `packages/db/migrations/0004_imports.sql`
- **journey_enrollment_status** — `packages/db/migrations/0022_journeys.sql`
- **journey_node_type** — `packages/db/migrations/0022_journeys.sql`
- **journey_reentry_policy** — `packages/db/migrations/0022_journeys.sql`
- **journey_status** — `packages/db/migrations/0022_journeys.sql`
- **journey_step_status** — `packages/db/migrations/0022_journeys.sql`
- **message_status** — `packages/db/migrations/0021_delivery.sql`
- **sales_task_status** — `packages/db/migrations/0027_sales_tasks.sql`
- **segment_kind** — `packages/db/migrations/0005_segments.sql`
- **webhook_delivery_status** — `packages/db/migrations/0029_webhooks.sql`
- **workspace_role** — `packages/db/migrations/0001_identity.sql`

## function (25)

- **assign_default_plan** — `packages/db/migrations/0033_plans_and_quotas.sql`
- **audience_snapshot_write_once** — `packages/db/migrations/0019_snapshot_immutability.sql`
- **audit_log_immutable** — `packages/db/migrations/0006_audit.sql`
- **campaign_version_immutable** — `packages/db/migrations/0015_campaigns.sql`
- **consent_supersede** — `packages/db/migrations/0003_consent.sql`
- **consent_supersede** — `packages/db/migrations/0007_composite_tenant_fks.sql`
- **consent_supersede** — `packages/db/migrations/0010_consent_race_and_self_lookup.down.sql`
- **consent_supersede** — `packages/db/migrations/0010_consent_race_and_self_lookup.sql`
- **content_version_append_only** — `packages/db/migrations/0016_content.sql`
- **due_campaign_starts** — `packages/db/migrations/0021_delivery.sql`
- **due_journey_entries** — `packages/db/migrations/0022_journeys.sql`
- **due_journey_entries** — `packages/db/migrations/0023_journey_hardening.down.sql`
- **due_journey_entries** — `packages/db/migrations/0023_journey_hardening.sql`
- **due_journey_steps** — `packages/db/migrations/0022_journeys.sql`
- **due_messages** — `packages/db/migrations/0021_delivery.sql`
- **due_webhook_deliveries** — `packages/db/migrations/0029_webhooks.sql`
- **find_active_api_key** — `packages/db/migrations/0025_api_key_lookup.sql`
- **find_message_by_provider_reference** — `packages/db/migrations/0032_provider_delivery_events.sql`
- **journey_graph_immutable** — `packages/db/migrations/0022_journeys.sql`
- **journey_graph_immutable** — `packages/db/migrations/0023_journey_hardening.down.sql`
- **journey_graph_immutable** — `packages/db/migrations/0023_journey_hardening.sql`
- **journey_version_immutable** — `packages/db/migrations/0022_journeys.sql`
- **platform_set_workspace_plan** — `packages/db/migrations/0033_plans_and_quotas.sql`
- **seed_default_pipeline** — `packages/db/migrations/0034_crm.sql`
- **usage_counters_never_decrease** — `packages/db/migrations/0036_quota_grant_hardening.sql`

## RLS policies (row-level security)

Defense-in-depth check: app-layer tenancy + these policies must BOTH hold.

- `RLS:workspaces.tenant_isolation` — `packages/db/migrations/0001_identity.sql`
- `RLS:invitations.tenant_isolation` — `packages/db/migrations/0001_identity.sql`
- `RLS:memberships.tenant_isolation` — `packages/db/migrations/0001_identity.sql`
- `RLS:audit_log.tenant_isolation` — `packages/db/migrations/0006_audit.sql`
- `RLS:invitations.tenant_isolation` — `packages/db/migrations/0008_auth_audit_and_invites.down.sql`
- `RLS:invitations.tenant_isolation` — `packages/db/migrations/0008_auth_audit_and_invites.sql`
- `RLS:memberships.tenant_isolation` — `packages/db/migrations/0009_policy_hardening.down.sql`
- `RLS:invitations.tenant_isolation` — `packages/db/migrations/0009_policy_hardening.down.sql`
- `RLS:invitations.tenant_isolation` — `packages/db/migrations/0009_policy_hardening.sql`
- `RLS:invitations.invitation_token_lookup` — `packages/db/migrations/0009_policy_hardening.sql`
- `RLS:memberships.tenant_isolation` — `packages/db/migrations/0009_policy_hardening.sql`
- `RLS:memberships.membership_self_lookup` — `packages/db/migrations/0009_policy_hardening.sql`
- `RLS:ai_suggestions.tenant_isolation` — `packages/db/migrations/0018_ai_suggestions.sql`
