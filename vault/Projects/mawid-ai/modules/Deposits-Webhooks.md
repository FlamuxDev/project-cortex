---
cortex-generated: true
title: deposits-webhooks
tags: [module]
---

# Deposits & webhooks

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `packages/backend/src/payments/,stripe/`

purpose: optional deposit checkout + webhook verification.
path_prefixes: packages/backend/src/payments/, stripe/
key_files: payments/stripe-appointment-deposit.ts, stripe/verify-webhook.ts; consumer route apps/web/app/api/stripe/webhook/route.ts (checkout.session.completed → appointment status pending_deposit→scheduled :27,:46)
invariants: inert until STRIPE_SECRET_KEY set AND platform_settings.payments_enabled=true; only verified events processed
confidence: high

## Files (3+)

- `apps/web/app/api/stripe/webhook/route.ts`
- `packages/backend/src/payments/stripe-appointment-deposit.ts`
- `packages/backend/src/stripe/verify-webhook.ts`

## API surface

- `POST /api/stripe/webhook`
