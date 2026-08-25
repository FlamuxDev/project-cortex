---
cortex-generated: true
title: billing-plans-quotas
tags: [module]
---

# billing / plans / quotas

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Dynamic catalog editable from platform-admin: Plan / FeatureCatalog / PlanFeature cached in-process and hot-reloaded (`services/plans/planCatalog.ts`, schema comments 1712-1717). Subscription denormalizes limits (-1 = unlimited) with `currentPeriodEnd`; rolling-period quota workers: `jobs/subscriptionPeriod.ts`. PricingConfig/OrgBillingSettings track per-unit price + markup + outstanding balance for manual invoicing (`schema.prisma:1173-1204`).
- No payment gateway in code — billing is operator-managed (platform-billing.controller adjusts balances).

