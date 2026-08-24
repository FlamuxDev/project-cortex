---
cortex-generated: true
title: identity-tenancy-rbac-trial-paypal-billing-m02
tags: [module]
---

# Identity, Tenancy, RBAC, Trial & PayPal Billing (M02)

**Project:** [[mushagil]] | **Confidence:** verified | **verified@** `638838aad84d`
**Owns:** `packages/modules/identity-tenant-billing,apps/api/src/identity,apps/web components LoginScreen/TeamScreen/BillingScreen/SecurityScreen/AcceptInvitationScreen/WorkspaceSwitcher`

purpose: OIDC login/sessions, tenants/memberships/invitations, central permission evaluation, 14-day trial, PayPal subscription verification/webhooks, entitlement projection.
path_prefixes: packages/modules/identity-tenant-billing, apps/api/src/identity, apps/web components ***REDACTED-B64***
key_files: src/domain/permission-evaluator.ts (manifest-driven, deny-by-default, 9-step order), src/domain/roles.ts (grant ceiling), src/domain/subscription-state.ts, src/application/{tenant,membership,session,user,team-query,paypal-verification,billing-webhook,trial-expiry,entitlement}-service.ts, src/infrastructure/auth0/{fake,live}-identity-provider.ts, src/infrastructure/paypal/{sandbox,live}-paypal-client.ts; controllers auth/billing/members/sessions/tenants.controller.ts
entrypoints: POST /v1/auth/login → GET /v1/auth/callback (PKCE S256 + state/nonce cookies) → session cookie; POST /v1/tenants, /v1/tenants/:id/switch, /v1/invitations/accept, /v1/billing/subscriptions/verify; raw POST /v1/billing/paypal/webhook (Fastify raw-body plugin scoped to this route only — apps/api/src/main.ts:100–140)
responsibilities: resolvePrincipal re-reads membership from DB every request (immediate revocation, no poisonable role cache); last-owner invariant enforced by DB trigger + SELECT…FOR UPDATE; webhook dedupe on provider_event_id with out-of-order regression protection.
invariants: browser approval alone grants nothing — verification requires planId AND productId AND currency AND amount AND provider status AND custom_id tenant binding (paypal-verification-service.ts, six rules); APPROVAL_PENDING/APPROVED map to null (no state change); terminal CANCELED/EXPIRED never transition; downgrade/suspend never deletes data; unknown events persisted without error; PAYPAL_WEBHOOK_ID absent ⇒ production rejects every webhook (fail-closed).
pitfalls: legacy plan P-83S97234B32877119NKFP42Y has identical price but wrong product — a named mandatory test refuses it; "price parity is not authorisation" (M02 evidence). Known documented gap: genuinely lost response on tenant-create/invitation-accept returns error instead of replaying original result. Trial previews GROWTH entitlement tier (config-driven).
confidence: verified

