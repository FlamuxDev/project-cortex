---
cortex-generated: true
title: operator-run-saas-backend
tags: [module]
---

# Operator-run SaaS backend

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `mythos-cloud/`

purpose: the ONLY internet endpoint devices talk to — inference proxy, metering, quota/credits, billing, auth.
path_prefixes: mythos-cloud/
key_files: app/quota.py (pure decision logic, fully unit-tested), app/proxy.py (pre-flight gate sequence), app/upstream.py (server-side keys), app/db.py (SupabaseDB prod / FakeDB tests), app/auth.py, app/credits.py, app/throttle.py, app/main.py, migrations/000{1,2,3}*.sql + 01xx_postgres_schema.sql
entrypoints: FastAPI app.main:app; ASGI via root index.py on Vercel (maxDuration=60); run-local.sh (127.0.0.1:8099)
responsibilities: /v1/chat/completions streaming proxy, model authorization per plan, usage events/counters, credit ledger, Stripe checkout+webhook, device-link pairing flow
invariants: privacy posture — aggregate usage only, never message content/memory/files; proxy doesn't persist prompts/completions by default (mythos-cloud/README.md, doc 06 §4); kill-switch/quota before real users
pitfalls: recent_request_count rate-limit was a stub in SupabaseDB (README admits; edge limiter needed); uuid/numeric/date casts needed for Postgres (git eb2fc69); pool resilience fixed intermittent device-link 500s (f8870a7)
confidence: high

## Files (24+)

- `mythos-cloud/app/__init__.py`
- `mythos-cloud/app/auth.py`
- `mythos-cloud/app/credits.py`
- `mythos-cloud/app/db.py`
- `mythos-cloud/app/main.py`
- `mythos-cloud/app/proxy.py`
- `mythos-cloud/app/quota.py`
- `mythos-cloud/app/throttle.py`
- `mythos-cloud/app/upstream.py`
- `mythos-cloud/index.py`
- `mythos-cloud/migrations/0001_init.sql`
- `mythos-cloud/migrations/0002_seed.sql`
- `mythos-cloud/migrations/0003_credits.sql`
- `mythos-cloud/migrations/0100_postgres_schema.sql`
- `mythos-cloud/migrations/0101_seed_gemini.sql`
- `mythos-cloud/migrations/0102_plans_2026.sql`
- `mythos-cloud/tests/__init__.py`
- `mythos-cloud/tests/test_credits.py`
- `mythos-cloud/tests/test_endpoints.py`
- `mythos-cloud/tests/test_proxy_endpoints.py`
- `mythos-cloud/tests/test_proxy_logic.py`
- `mythos-cloud/tests/test_reservation.py`
- `mythos-cloud/tests/test_throttle.py`
- `plugins/model-providers/mythos-cloud/__init__.py`

## API surface

- `POST /v1/chat/completions`
- `GET /v1/models`
- `GET /v1/usage`
- `GET /v1/credits`
- `GET /health`
- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/device/start`
- `POST /auth/device/approve`
- `POST /auth/device/poll`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /v1/billing/checkout`
- `POST /webhooks/stripe`
