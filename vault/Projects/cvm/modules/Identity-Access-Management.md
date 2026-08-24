---
cortex-generated: true
title: identity-access-management
tags: [module]
---

# Identity & Access Management

**Project:** [[cvm]] | **Confidence:** strongly_inferred | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/iam/`

purpose: users, roles/personas, permissions (30 domain perms, 10 persona roles), sessions (opaque, server-side), Argon2id auth, MFA (TOTP+recovery), API keys (embed tenant — ADR-016), service accounts, SSO (OIDC), SCIM 2.0 at /scim/v2, org units, session policy, IP allow-listing.
path_prefixes: packages/modules/src/iam/
key_files: iam/index.ts (exports IamAuthenticator consumed via platform port — ADR-014), application/, http/routes.ts
entrypoints: authRoutes, iamAdminRoutes, scimRoutes, ssoRoutes registered in app.ts
responsibilities: authenticate() port impl; permissionsFor(tenantId) — permission sets are tenant-paired; login failure/permission-denial audited via sink.
invariants: separation of duties — admin@example.com deliberately cannot read customers/campaigns/analytics.
pitfalls: SSO/SCIM wiring exposed three bugs on landing (d81b9a5); SCIM must live outside /api/v1 or Okta-style base URLs break.
confidence: strongly_inferred

## Files (16+)

- `packages/modules/src/iam/application/apikeys.ts`
- `packages/modules/src/iam/application/mfa.ts`
- `packages/modules/src/iam/application/permissions.ts`
- `packages/modules/src/iam/application/policy.ts`
- `packages/modules/src/iam/application/scim.ts`
- `packages/modules/src/iam/application/sessions.ts`
- `packages/modules/src/iam/application/sso.ts`
- `packages/modules/src/iam/application/users.ts`
- `packages/modules/src/iam/domain/credentials.ts`
- `packages/modules/src/iam/domain/mfa.ts`
- `packages/modules/src/iam/http/admin-routes.ts`
- `packages/modules/src/iam/http/auth-routes.ts`
- `packages/modules/src/iam/http/scim-routes.ts`
- `packages/modules/src/iam/http/sso-routes.ts`
- `packages/modules/src/iam/index.ts`
- `packages/modules/src/iam/infrastructure/authenticator.ts`

## API surface

- `DELETE /scim-tokens/:id`
- `POST /scim-tokens`
- `GET /scim-tokens`
- `PUT /identity-providers`
- `GET /identity-providers`
- `PUT /session-policy`
- `GET /session-policy`
- `DELETE /me/mfa/:id`
- `POST /me/mfa/:id/confirm`
- `POST /me/mfa`
- `GET /me/mfa`
- `DELETE /api-keys/:id`
- `POST /api-keys`
- `GET /api-keys`
- `POST /service-accounts`
