---
cortex-generated: true
title: identity-tenancy-rbac-audit-pii
tags: [module]
---

# Identity, tenancy, RBAC, audit, PII

**Project:** [[telvora]] | **Confidence:** verified | **verified@** `7423f040ed46`
**Owns:** `services/core-api/internal/{auth,tenants,rbac,audit,pii}`

purpose: sessions (opaque bearer tokens, SHA-256-at-rest), Argon2id passwords, TOTP MFA, invite/verify/recover, tenant lifecycle, custom roles + granular permissions, hash-chained append-only audit log, PII masking-by-default
path_prefixes: services/core-api/internal/{auth,tenants,rbac,audit,pii}
key_files: internal/auth/token.go, password.go, totp.go, account_handler.go, security_handler.go; internal/rbac/store.go; internal/audit/store.go (chain verify at GET /api/v1/tenant/audit/verify); internal/pii/pii.go (MaskEmail/MaskPhone; authorization deliberately NOT this package's job)
entrypoints: routes main.go:267-311 (auth/*, platform-admin/tenants/*, tenant/users|roles|audit)
responsibilities: signup→tenant creation (ADR-005), invitations as the only seat-grant path, MFA enrollment/login, session listing/revocation, suspend/reactivate tenants, audit chain integrity
invariants: session token only ever hashed server-side; PII reveal requires customers.read_pii permission AND is audited (POST /customers/{id}/reveal-pii); employees cannot self-register into existing tenants
pitfalls: superuser bypasses RLS regardless of FORCE — never point DATABASE_URL at the migration role (.env.example warnings)
confidence: verified

## Files (24+)

- `apps/web/src/app/(protected)/[locale]/app/audit/page.tsx`
- `apps/web/src/app/(protected)/[locale]/platform-admin/tenants/[id]/page.tsx`
- `apps/web/src/app/(protected)/[locale]/platform-admin/tenants/page.tsx`
- `apps/web/src/app/api/platform-admin/tenants/[id]/reactivate/route.ts`
- `apps/web/src/app/api/platform-admin/tenants/[id]/suspend/route.ts`
- `apps/web/src/app/api/platform-admin/tenants/route.ts`
- `apps/web/src/app/api/tenant/audit/verify/route.ts`
- `apps/web/src/lib/audit.ts`
- `apps/web/src/lib/rbac.ts`
- `apps/web/src/lib/tenants.ts`
- `e2e/tests/audit.spec.ts`
- `packages/ui/src/AuditLogRow.tsx`
- `services/core-api/internal/audit/audit_test.go`
- `services/core-api/internal/audit/handler.go`
- `services/core-api/internal/audit/model.go`
- `services/core-api/internal/audit/store.go`
- `services/core-api/internal/rbac/handler.go`
- `services/core-api/internal/rbac/model.go`
- `services/core-api/internal/rbac/rbac_test.go`
- `services/core-api/internal/rbac/store.go`
- `services/core-api/internal/tenants/handler.go`
- `services/core-api/internal/tenants/model.go`
- `services/core-api/internal/tenants/store.go`
- `services/core-api/internal/tenants/tenants_test.go`

## API surface

- `GET locale`
- `GET adminEmail`
- `GET environmentLabel`
- `GET displayName`
- `GET slug`
- `POST /api/platform-admin/tenants/[id]/suspend`
- `POST /api/platform-admin/tenants`
- `POST /api/platform-admin/tenants/[id]/reactivate`
- `GET /api/tenant/audit/verify`
