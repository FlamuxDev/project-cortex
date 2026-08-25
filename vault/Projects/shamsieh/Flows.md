---
cortex-generated: true
title: shamsieh flows
tags: [flows/project]
---

# shamsieh — Product Flows

End-to-end behaviors as verified from source. Files are the evidence trail.

## fingerprint-punch-to-attendance
**Trigger:** device event (push) or poller cycle
*[[shamsieh]] · confidence: high*

trigger: device event (push) or poller cycle
steps: Hikvision POST → parse multipart → SQLite store → retry worker → Odoo XML-RPC ingest → `hr.attendance` creation → daily-status cron recomputes late/early/missing-checkout/unworked minutes. ZK variant polls terminal then calls the same ingest method directly.
files: hikvision_attendance_service/app/main.py, hr_attendance_custom_ext/models/fingerprint_device*.py, models/hr_attendance_daily_status.py
confidence: high

**Files:**
- `hikvision_attendance_service/app/main.py`
- `hr_attendance_custom_ext/models/fingerprint_device*.py`
- `models/hr_attendance_daily_status.py`

## assistant-delegation-v2
**Trigger:** employee opens Botify widget/client action
*[[shamsieh]] · confidence: high*

trigger: employee opens Botify widget/client action
steps: `/identity` (auth=user) mints per-user delegation credential → browser relays → backend requests `/grant` naming one uid + op class → single-use jti validated → `/rpc` executes under `with_user(uid)` with policy-manifest checks and company escalation guard.
files: botify_agent/controllers/grant.py, controllers/main.py, models/botify_policy.py
confidence: high

**Files:**
- `botify_agent/controllers/grant.py`
- `controllers/main.py`
- `models/botify_policy.py`

## website-lead-ingest
**Trigger:** external site POST `/api/website/lead`
*[[shamsieh]] · confidence: high*

trigger: external site POST `/api/website/lead`
steps: honeypot check → API key validation → rate limit by IP → field validation → `crm.lead` create (sudo) → submission log row.
files: website_lead_api/controllers/
confidence: high

**Files:**
- `website_lead_api/controllers/`

## wfh-and-overtime-approval
**Trigger:** employee request
*[[shamsieh]] · confidence: medium*

trigger: employee request
steps: WFH request over date range → manager then HR approval → becomes Time Off leave; approved overtime may convert to Time Off (no balance banking from fingerprints).
files: hr_holidays_custom_ext/models/, hr_overtime_management/models/
confidence: medium

**Files:**
- `hr_holidays_custom_ext/models/`
- `hr_overtime_management/models/`
