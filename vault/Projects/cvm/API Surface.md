---
cortex-generated: true
title: cvm api
tags: [api/project]
---

# CVM — API Surface

524 routes. Grouped by owning file; every route names its handler.

## `apps/api/src/app.ts`
*module: [[cvm/modules/Fastify-Http-Api|fastify-http-api]]*

- **GET** `/api/v1/openapi.json` → `async`

## `apps/api/src/health.ts`
*module: [[cvm/modules/Fastify-Http-Api|fastify-http-api]]*

- **GET** `/health` → `async`
- **GET** `/ready` → `async`

## `apps/web/src/app/(app)/administration/policy/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `channel`
- **GET** `channel`
- **GET** `channel`
- **GET** `customer_id`
- **GET** `enabled`
- **GET** `expires_at`
- **GET** `expires_at`
- **GET** `id`
- **GET** `identifier_type`
- **GET** `identifier_value`
- **GET** `note`
- **GET** `reason`
- **GET** `reason`
- **GET** `threshold`

## `apps/web/src/app/(app)/administration/security/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `absolute_hours`
- **GET** `code`
- **GET** `default_role`
- **GET** `enabled`
- **GET** `factor`
- **GET** `factor`
- **GET** `idle_minutes`
- **GET** `max_concurrent_sessions`
- **GET** `name`
- **GET** `note`
- **GET** `package`
- **GET** `require_mfa_for_all`
- **GET** `secret`

## `apps/web/src/app/(app)/audiences/[key]/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `ast`
- **GET** `ast`
- **GET** `ast`
- **GET** `ast`
- **GET** `ast`
- **GET** `confirmation`
- **GET** `index`
- **GET** `join`
- **GET** `json`
- **GET** `note`
- **GET** `path`
- **GET** `path`
- **GET** `path`
- **GET** `segment_key`
- **GET** `segment_key`
- **GET** `segment_key`
- **GET** `segment_key`
- **GET** `segment_key`
- **GET** `segment_key`
- **GET** `segment_key`
- **GET** `segment_key`
- **GET** `version`

## `apps/web/src/app/(app)/audiences/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `key`
- **GET** `name`
- **GET** `type`

## `apps/web/src/app/(app)/campaigns/[code]/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `acknowledge`
- **GET** `action`
- **GET** `attribution_window_hours`
- **GET** `campaign_type`
- **GET** `confirmation`
- **GET** `confirmation`
- **GET** `control_percent`
- **GET** `conversion_event_type`
- **GET** `conversion_value_field`
- **GET** `currency`
- **GET** `decision`
- **GET** `decision`
- **GET** `ends_at`
- **GET** `ends_at`
- **GET** `note`
- **GET** `note`
- **GET** `objective`
- **GET** `owner`
- **GET** `purpose`
- **GET** `reason`
- **GET** `reason`
- **GET** `reason`
- **GET** `requires_approval`
- **GET** `run_id`
- **GET** `run_id`
- **GET** `segment_key`
- **GET** `separate_approver`
- **GET** `starts_at`
- **GET** `starts_at`

## `apps/web/src/app/(app)/campaigns/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `body`
- **GET** `channel`
- **GET** `code`
- **GET** `code`
- **GET** `name`
- **GET** `name`
- **GET** `owner`
- **GET** `subject`

## `apps/web/src/app/(app)/customers/[id]/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `confirmation`
- **GET** `customer_id`
- **GET** `customer_id`
- **GET** `reason`

## `apps/web/src/app/(app)/data-quality/[sourceId]/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `batch_id`

## `apps/web/src/app/(app)/decisions/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `channel`
- **GET** `channel`
- **GET** `customer_id`
- **GET** `customer_id`
- **GET** `offer_code`
- **GET** `purpose`
- **GET** `purpose`
- **GET** `trigger_event_type`

## `apps/web/src/app/(app)/games/[code]/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `reason`
- **GET** `state`

## `apps/web/src/app/(app)/identity/conflicts/[id]/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `confirmation`
- **GET** `note`
- **GET** `resolution`
- **GET** `target_customer_id`

## `apps/web/src/app/(app)/identity/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `confirmation`
- **GET** `merge_id`
- **GET** `reason`

## `apps/web/src/app/(app)/integrations/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `activate`
- **GET** `code`
- **GET** `contract_id`
- **GET** `freshness`
- **GET** `freshness`
- **GET** `kind`
- **GET** `name`
- **GET** `owner_contact`
- **GET** `owner_team`
- **GET** `pull_url`
- **GET** `pull_url`
- **GET** `record_type`
- **GET** `source_id`
- **GET** `spec`

## `apps/web/src/app/(app)/journeys/[code]/edit/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `ast`
- **GET** `entry_event_type`
- **GET** `entry_kind`
- **GET** `entry_segment_key`
- **GET** `goal_event_type`
- **GET** `graph`
- **GET** `graph`
- **GET** `graph`
- **GET** `graph`
- **GET** `graph`
- **GET** `graph`
- **GET** `index`
- **GET** `join`
- **GET** `max_concurrent_per_customer`
- **GET** `max_duration_hours`
- **GET** `node`
- **GET** `node_id`
- **GET** `node_id`
- **GET** `node_id`
- **GET** `node_id`
- **GET** `note`
- **GET** `reentry_cooldown_hours`
- **GET** `reentry_cooldown_hours`
- **GET** `retry_limit`

## `apps/web/src/app/(app)/journeys/[code]/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `confirmation`
- **GET** `decision`
- **GET** `reason`
- **GET** `reason`
- **GET** `reason`
- **GET** `simulated`
- **GET** `state`

## `apps/web/src/app/(app)/loyalty/[code]/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `confirmation`
- **GET** `membership_id`
- **GET** `points`
- **GET** `reason`
- **GET** `reason`
- **GET** `state`

## `apps/web/src/app/(app)/models/[code]/operations/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `challenger_version`
- **GET** `decision`
- **GET** `drift_psi`
- **GET** `enabled`
- **GET** `hypothesis`
- **GET** `id`
- **GET** `interval_days`
- **GET** `min_rows`
- **GET** `reason`
- **GET** `traffic_percent`
- **GET** `trigger`

## `apps/web/src/app/(app)/models/[code]/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `confirmation`
- **GET** `confirmation`
- **GET** `decision`
- **GET** `decision`
- **GET** `note`
- **GET** `reason`
- **GET** `reason`
- **GET** `reason`
- **GET** `version`
- **GET** `version`
- **GET** `version`

## `apps/web/src/app/(app)/offers/[code]/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `ast`
- **GET** `ast`
- **GET** `ast`
- **GET** `budget`
- **GET** `capacity`
- **GET** `confirmation`
- **GET** `cost`
- **GET** `currency`
- **GET** `decision`
- **GET** `eligibility`
- **GET** `ends_at`
- **GET** `ends_at`
- **GET** `exclusion`
- **GET** `expected_margin`
- **GET** `index`
- **GET** `join`
- **GET** `legal_text`
- **GET** `note`
- **GET** `other`
- **GET** `priority`
- **GET** `reason`
- **GET** `starts_at`
- **GET** `starts_at`
- **GET** `title`
- **GET** `value_amount`
- **GET** `value_amount`
- **GET** `value_type`
- **GET** `version`
- **GET** `version`
- **GET** `version`
- **GET** `which`

## `apps/web/src/app/(app)/offers/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `category`
- **GET** `code`
- **GET** `code`
- **GET** `name`
- **GET** `name`
- **GET** `owner`
- **GET** `product_code`

## `apps/web/src/app/(app)/privacy/governance/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `code`
- **GET** `days`
- **GET** `kind`
- **GET** `reason`

## `apps/web/src/app/(app)/privacy/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `confirmation`
- **GET** `decision`
- **GET** `id`
- **GET** `reason`

## `apps/web/src/app/login/page.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `email`
- **GET** `password`

## `apps/web/src/components/band-rail.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `next`

## `apps/web/src/components/journey-builder.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `channel`
- **GET** `method`
- **GET** `name`
- **GET** `new_id`
- **GET** `next`
- **GET** `node_id`
- **GET** `node_type`
- **GET** `offer_codes`
- **GET** `on_false`
- **GET** `on_true`
- **GET** `purpose`
- **GET** `reason`
- **GET** `score_type`
- **GET** `template_code`
- **GET** `threshold`
- **GET** `url`
- **GET** `wait`
- **GET** `wait_until_hour`

## `apps/web/src/components/locale-switcher.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `locale`

## `apps/web/src/components/rule-builder.tsx`
*module: [[cvm/modules/Next-Js-Operator-Console|next-js-operator-console]]*

- **GET** `field`
- **GET** `op`
- **GET** `path`
- **GET** `value`
- **GET** `window`

## `packages/modules/src/analytics/http/routes.ts`
*module: [[cvm/modules/Analytics-Kpis|analytics-kpis]]*

- **GET** `/analytics/affinity` → `async`
- **GET** `/analytics/attribution-comparison` → `async`
- **GET** `/analytics/behaviour-funnel` → `async`
- **GET** `/analytics/cohorts` → `async`
- **GET** `/analytics/executive` → `async`
- **GET** `/analytics/segment-overlap` → `async`
- **GET** `/analytics/trend` → `async`

## `packages/modules/src/audit/http/routes.ts`
*module: [[cvm/modules/Append-Only-Audit-Trail|append-only-audit-trail]]*

- **GET** `/audit` → `async`
- **GET** `/audit/correlation/:correlationId` → `async`

## `packages/modules/src/campaigns/http/routes.ts`
*module: [[cvm/modules/Campaign-Orchestration|campaign-orchestration]]*

- **GET** `/campaign-states` → `async`
- **POST** `/campaigns` → `async`
- **GET** `/campaigns` → `async`
- **GET** `/campaigns/:code` → `async`
- **POST** `/campaigns/:code/approval` → `async`
- **POST** `/campaigns/:code/launch` → `async`
- **POST** `/campaigns/:code/request-approval` → `async`
- **GET** `/campaigns/:code/runs` → `async`
- **POST** `/campaigns/:code/validate` → `async`
- **POST** `/campaigns/:code/versions` → `async`
- **GET** `/customers/:id/marketing` → `async`
- **GET** `/runs/:id/analysis` → `async`
- **GET** `/runs/:id/funnel` → `async`
- **POST** `/runs/:id/kill` → `async`
- **POST** `/runs/:id/pause` → `async`
- **GET** `/runs/:id/progress` → `async`
- **GET** `/runs/:id/reconcile` → `async`
- **POST** `/runs/:id/resume` → `async`
- **GET** `/templates` → `async`
- **PUT** `/templates/:code` → `async`

## `packages/modules/src/catalog/http/routes.ts`
*module: [[cvm/modules/Offer-Catalog|offer-catalog]]*

- **POST** `/offers` → `async`
- **GET** `/offers` → `async`
- **GET** `/offers/:code` → `async`
- **POST** `/offers/:code/archive` → `async`
- **POST** `/offers/:code/eligibility-preview` → `async`
- **PUT** `/offers/:code/inventory` → `async`
- **POST** `/offers/:code/versions` → `async`
- **POST** `/offers/:code/versions/:version/approval` → `async`
- **POST** `/offers/:code/versions/:version/publish` → `async`
- **POST** `/offers/:code/versions/:version/request-approval` → `async`
- **POST** `/products` → `async`
- **GET** `/products` → `async`

## `packages/modules/src/consent/http/routes.ts`
*module: [[cvm/modules/Consent-Contact-Policy|consent-contact-policy]]*

- **GET** `/contact-policies` → `async`
- **PUT** `/contact-policies/:channel` → `async`
- **POST** `/customers/:id/consent` → `async`
- **GET** `/customers/:id/consent` → `async`
- **GET** `/customers/:id/contacts` → `async`
- **POST** `/suppressions` → `async`
- **GET** `/suppressions` → `async`
- **DELETE** `/suppressions/:id` → `async`

## `packages/modules/src/decision/http/routes.ts`
*module: [[cvm/modules/Decision-Engine-Gate-Ranker|decision-engine-gate-ranker]]*

- **GET** `/decision-codes` → `async`
- **POST** `/decision-weights` → `async`
- **GET** `/decision-weights` → `async`
- **GET** `/decisions` → `async`
- **POST** `/decisions` → `async`
- **GET** `/decisions/:id` → `async`
- **POST** `/decisions/:id/outcome` → `async`
- **POST** `/decisions/batch` → `async`
- **GET** `/decisions/summary` → `async`
- **POST** `/policy/evaluate` → `async`

## `packages/modules/src/delivery/http/routes.ts`
*module: [[cvm/modules/Execution-Engine-Channels|execution-engine-channels]]*

- **GET** `/channels` → `async`
- **GET** `/deliveries/:id` → `async`
- **PUT** `/provider-credentials` → `async`
- **GET** `/provider-credentials` → `async`
- **DELETE** `/provider-credentials/:id` → `async`
- **POST** `/provider-credentials/:id/test` → `async`
- **GET** `/t/:token` → `async`
- **GET** `/trace/:deliveryId` → `async`
- **POST** `/webhooks/delivery/:provider` → `async`

## `packages/modules/src/experiments/http/routes.ts`
*module: [[cvm/modules/A-B-Experiments-Outcomes|a-b-experiments-outcomes]]*

- **POST** `/experiments` → `async`
- **GET** `/experiments` → `async`
- **GET** `/experiments/:code` → `async`
- **POST** `/experiments/reallocate` → `async`

## `packages/modules/src/features/http/routes.ts`
*module: [[cvm/modules/Feature-Platform|feature-platform]]*

- **POST** `/feature-definitions` → `async`
- **GET** `/feature-definitions` → `async`
- **PATCH** `/feature-definitions/:key` → `async`
- **GET** `/feature-definitions/:key` → `async`
- **POST** `/feature-definitions/:key/recompute` → `async`
- **GET** `/feature-definitions/freshness` → `async`

## `packages/modules/src/iam/http/admin-routes.ts`
*module: [[cvm/modules/Identity-Access-Management|identity-access-management]]*

- **POST** `/api-keys` → `async`
- **GET** `/api-keys` → `async`
- **DELETE** `/api-keys/:id` → `async`
- **PUT** `/identity-providers` → `async`
- **GET** `/identity-providers` → `async`
- **POST** `/me/mfa` → `async`
- **GET** `/me/mfa` → `async`
- **DELETE** `/me/mfa/:id` → `async`
- **POST** `/me/mfa/:id/confirm` → `async`
- **GET** `/roles` → `async`
- **POST** `/scim-tokens` → `async`
- **GET** `/scim-tokens` → `async`
- **DELETE** `/scim-tokens/:id` → `async`
- **POST** `/service-accounts` → `async`
- **GET** `/service-accounts` → `async`
- **PUT** `/session-policy` → `async`
- **GET** `/session-policy` → `async`
- **POST** `/users` → `async`
- **GET** `/users` → `async`
- **POST** `/users/:userId/deactivate` → `async`
- **POST** `/users/:userId/password` → `async`
- **POST** `/users/:userId/roles` → `async`
- **DELETE** `/users/:userId/roles/:roleCode` → `async`

## `packages/modules/src/iam/http/auth-routes.ts`
*module: [[cvm/modules/Identity-Access-Management|identity-access-management]]*

- **POST** `/auth/login` → `async`
- **POST** `/auth/logout` → `async`
- **GET** `/auth/me` → `async`
- **GET** `/auth/permissions` → `async`
- **POST** `/auth/switch-tenant` → `async`

## `packages/modules/src/iam/http/scim-routes.ts`
*module: [[cvm/modules/Identity-Access-Management|identity-access-management]]*

- **GET** `/scim/v2/ServiceProviderConfig` → `async`
- **POST** `/scim/v2/Users` → `async`
- **GET** `/scim/v2/Users` → `async`
- **DELETE** `/scim/v2/Users/:id` → `async`
- **PATCH** `/scim/v2/Users/:id` → `async`
- **PUT** `/scim/v2/Users/:id` → `async`
- **GET** `/scim/v2/Users/:id` → `async`

## `packages/modules/src/iam/http/sso-routes.ts`
*module: [[cvm/modules/Identity-Access-Management|identity-access-management]]*

- **GET** `/auth/sso/oidc/callback` → `async`
- **POST** `/auth/sso/saml/callback` → `async`
- **POST** `/auth/sso/start` → `async`

## `packages/modules/src/identity/http/routes.ts`
*module: [[cvm/modules/Identity-Resolution-Merge|identity-resolution-merge]]*

- **GET** `/identity/conflicts` → `async`
- **GET** `/identity/conflicts/:id` → `async`
- **POST** `/identity/conflicts/:id/resolve` → `async`
- **GET** `/identity/customers/:id` → `async`
- **GET** `/identity/lookup` → `async`
- **POST** `/identity/merge` → `async`
- **GET** `/identity/merges` → `async`
- **GET** `/identity/merges/:id` → `async`
- **PUT** `/identity/rules` → `async`
- **GET** `/identity/rules` → `async`
- **POST** `/identity/unmerge` → `async`

## `packages/modules/src/ingestion/http/routes.ts`
*module: [[cvm/modules/Ingestion-Contracts-Quarantine-Quality|ingestion-contracts-quarantine-quality]]*

- **POST** `/data-contracts` → `async`
- **GET** `/data-contracts` → `async`
- **GET** `/data-contracts/:id` → `async`
- **POST** `/data-contracts/:id/activate` → `async`
- **GET** `/data-quality/contract-vocabulary` → `async`
- **GET** `/data-quality/metrics` → `async`
- **GET** `/data-quality/reasons` → `async`
- **GET** `/data-quality/sources` → `async`
- **POST** `/data-sources` → `async`
- **GET** `/data-sources` → `async`
- **PATCH** `/data-sources/:id` → `async`
- **GET** `/data-sources/:id` → `async`
- **POST** `/event-types` → `async`
- **GET** `/event-types` → `async`
- **POST** `/ingest/:source_code/batches` → `async`
- **GET** `/ingest/batches` → `async`
- **GET** `/ingest/batches/:id` → `async`
- **GET** `/ingest/errors` → `async`
- **POST** `/ingest/errors/replay` → `async`

## `packages/modules/src/journeys/application/journeys.ts`

- **GET** `active`
- **GET** `cancelled`
- **GET** `completed`
- **GET** `exited`
- **GET** `failed`
- **GET** `goal_reached`
- **GET** `waiting`

## `packages/modules/src/journeys/http/routes.ts`

- **GET** `/journey-instances/:id` → `async`
- **POST** `/journey-instances/:id/step` → `async`
- **POST** `/journeys` → `async`
- **GET** `/journeys` → `async`
- **GET** `/journeys/:code` → `async`
- **POST** `/journeys/:code/approval` → `async`
- **POST** `/journeys/:code/enter` → `async`
- **GET** `/journeys/:code/instances` → `async`
- **POST** `/journeys/:code/kill` → `async`
- **POST** `/journeys/:code/request-approval` → `async`
- **POST** `/journeys/:code/state` → `async`
- **POST** `/journeys/:code/versions` → `async`

## `packages/modules/src/loyalty/http/routes.ts`

- **GET** `/customers/:id/games` → `async`
- **POST** `/customers/:id/loyalty` → `async`
- **GET** `/customers/:id/loyalty` → `async`
- **GET** `/games` → `async`
- **GET** `/games/:code` → `async`
- **PUT** `/games/:code` → `async`
- **POST** `/games/:code/state` → `async`
- **POST** `/loyalty/ledger/:id/reverse` → `async`
- **POST** `/loyalty/memberships/:id/adjust` → `async`
- **POST** `/loyalty/memberships/:id/close` → `async`
- **GET** `/loyalty/memberships/:id/history` → `async`
- **POST** `/loyalty/memberships/:id/redeem` → `async`
- **GET** `/loyalty/memberships/:id/redemptions` → `async`
- **POST** `/loyalty/programs` → `async`
- **GET** `/loyalty/programs` → `async`
- **GET** `/loyalty/programs/:code` → `async`
- **PUT** `/loyalty/programs/:code/earn-rules/:rule` → `async`
- **PUT** `/loyalty/programs/:code/promotions/:promotion` → `async`
- **PUT** `/loyalty/programs/:code/rewards/:reward` → `async`
- **POST** `/loyalty/programs/:code/state` → `async`
- **PUT** `/loyalty/programs/:code/tiers/:tier` → `async`
- **POST** `/loyalty/redemptions/:id/cancel` → `async`
- **POST** `/loyalty/redemptions/:id/fulfil` → `async`

## `packages/modules/src/ml/http/routes.ts`
*module: [[cvm/modules/Model-Registry-Scoring-Platform-Side-Of-Track-B|model-registry-scoring-platform-side-of-track-b]]*

- **POST** `/challengers/:id/decision` → `async`
- **GET** `/customers/:id/scores` → `async`
- **GET** `/datasets/:id` → `async`
- **POST** `/models` → `async`
- **GET** `/models` → `async`
- **GET** `/models/:code` → `async`
- **POST** `/models/:code/challengers` → `async`
- **GET** `/models/:code/challengers` → `async`
- **POST** `/models/:code/datasets` → `async`
- **POST** `/models/:code/drift` → `async`
- **GET** `/models/:code/drift` → `async`
- **GET** `/models/:code/monitoring` → `async`
- **GET** `/models/:code/retrain-policy` → `async`
- **PUT** `/models/:code/retrain-policy` → `async`
- **POST** `/models/:code/rollback` → `async`
- **POST** `/models/:code/score` → `async`
- **POST** `/models/:code/versions` → `async`
- **GET** `/models/:code/versions/:version` → `async`
- **POST** `/models/:code/versions/:version/approval` → `async`
- **POST** `/models/:code/versions/:version/deploy` → `async`
- **POST** `/models/:code/versions/:version/request-approval` → `async`

## `packages/modules/src/privacy/http/routes.ts`
*module: [[cvm/modules/Erasure-Governance|erasure-governance]]*

- **POST** `/customers/:id/erasure` → `async`
- **GET** `/erasure-requests` → `async`
- **POST** `/erasure-requests/:id/decision` → `async`
- **GET** `/erasure-scope` → `async`
- **GET** `/governance/consent-packs` → `async`
- **PUT** `/governance/consent-packs/:code` → `async`
- **POST** `/governance/consent-packs/:code/activate` → `async`
- **POST** `/governance/exports` → `async`
- **GET** `/governance/exports` → `async`
- **GET** `/governance/processing-register` → `async`

## `packages/modules/src/profile/http/routes.ts`
*module: [[cvm/modules/Customer-360-Projection|customer-360-projection]]*

- **GET** `/customers` → `async`
- **GET** `/customers/:id` → `async`
- **GET** `/customers/:id/features` → `async`
- **GET** `/customers/:id/identity` → `async`
- **POST** `/customers/:id/reproject` → `async`
- **GET** `/customers/:id/timeline` → `async`
- **POST** `/customers/export` → `async`

## `packages/modules/src/segments/http/routes.ts`
*module: [[cvm/modules/Audiences-Rule-Language|audiences-rule-language]]*

- **POST** `/exclusion-lists` → `async`
- **GET** `/exclusion-lists` → `async`
- **POST** `/exclusion-lists/:code/members` → `async`
- **GET** `/exclusion-lists/:code/members` → `async`
- **GET** `/segment-fields` → `async`
- **POST** `/segments` → `async`
- **GET** `/segments` → `async`
- **PATCH** `/segments/:key` → `async`
- **GET** `/segments/:key` → `async`
- **POST** `/segments/:key/archive` → `async`
- **GET** `/segments/:key/diff` → `async`
- **GET** `/segments/:key/explain` → `async`
- **POST** `/segments/:key/materialize` → `async`
- **GET** `/segments/:key/members` → `async`
- **POST** `/segments/:key/preview` → `async`
- **POST** `/segments/:key/publish` → `async`
- **GET** `/segments/:key/runs` → `async`
- **PUT** `/segments/:key/schedule` → `async`
- **POST** `/segments/:key/versions` → `async`
- **GET** `/segments/:key/versions` → `async`

## `packages/modules/src/tenancy/http/routes.ts`

- **GET** `/entitlements` → `async`
- **PUT** `/entitlements/:package` → `async`
- **POST** `/org-units` → `async`
- **GET** `/org-units` → `async`
- **DELETE** `/org-units/:id` → `async`
- **GET** `/quotas` → `async`
- **PUT** `/quotas/:resource` → `async`
- **GET** `/retention-policies` → `async`
- **PUT** `/retention-policies/:dataset` → `async`
- **GET** `/settings` → `async`
- **PUT** `/settings/:key` → `async`
- **PATCH** `/tenant` → `async`
- **GET** `/tenant` → `async`
- **POST** `/tenants` → `async`

## `packages/modules/src/triggers/http/routes.ts`

- **GET** `/customers/:id/triggers` → `async`
- **GET** `/triggers` → `async`
- **PUT** `/triggers/:code` → `async`
- **GET** `/triggers/:code/firings` → `async`
