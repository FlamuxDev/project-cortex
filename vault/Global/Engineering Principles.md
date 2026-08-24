---
cortex-generated: true
title: principles
tags: [global]
---
# Engineering Principles

## Fail-open configuration on missing NODE_ENV

Campify commit 578b127: missing/unset NODE_ENV defaulted to permissive mode. Configuration must fail closed — refuse to boot when environment is undefined.

## Claim-vs-retry double processing

CVM game-day finding: claiming a job then retrying after timeout can process twice unless the claim is atomic (advisory lock / lease token / ON CONFLICT). Luma uses (workerId, lease_generation) fencing tokens; Mushagil uses idempotency_key table. Never catch 25P02 (serialization failure) as 'already exists' — distinguish conflict outcomes.

## Docs drift faster than code

Recurring: Mawid-AI OpenAPI documented 3 deleted endpoints; TEAM-GUIDE named wrong session cookie; Luma worker API implemented despite docs claiming otherwise; Mushagil CURRENT_STATE.md lagged reality. Trust code+git over prose; when updating docs, grep for stale references.

## Verified-but-never-wired trap

CVM Phase 10 shipped eight capabilities with passing unit tests and facade exports but NO caller — screens showed empty tables for months while the suite stayed green. A unit test proves a function WORKS; nothing proved it RUNS. Evidence: Dev/CVM/tools/wiring/check.ts; gate checks register(name), not imports.

## Composite foreign keys for tenant isolation

Cross-tenant access hole found via single-column FK: a row could reference a parent in ANOTHER tenant. Fix pattern: composite FKs (tenant_id, parent_id) referencing unique(tenant_id, id) on every parent relation. Found independently in Campify (ADR-0010) and applied in Mushagil/Telvora.

## RLS as defense-in-depth, not the only wall

Mushagil/CVM/Telvora enforce Postgres FORCE ROW LEVEL SECURITY per tenant AND validate tenancy in the app layer. Mawid-AI deliberately relies on app-layer only (documented trade-off). When touching any tenants table: check both layers exist or the omission is documented.

## Mutation + audit + outbox in one transaction

Mushagil M02+ pattern: every state mutation writes the row, the audit event, and the outbox record in a single DB transaction; relay publishes async. Prevents silent audit loss.

## Immutable published snapshots as source of truth

Mushagil ADR-0004: published entities are stored as immutable JSONB snapshots; readers never join live drafts. Same idea in Telvora decision engine inputs. Avoids read-your-drafts bugs.

## Route ownership conflicts resolved immediately

Telvora AGENT_BUILD_PROTOCOL: when a new phase's route spec conflicts with an existing phase's route ownership, resolve immediately (move/rename) instead of shipping compatibility shims.

## Bilingual (ar/en, RTL-first) is a core constraint

Most products here are Arabic-first with RTL UI: Campify, Mushagil, Telvora console, sham-v2, shamsieh. Any new UI work must plan locale catalogs, RTL-safe layout and Arabic formatting (numbers/dates/money) from day one.

