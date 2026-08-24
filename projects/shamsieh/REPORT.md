# CORTEX REPORT — shamsieh

## META
project_id: shamsieh
root: /home/aboud/Dev/shamsieh
kind: Odoo 19 customization monorepo (HR/attendance/payroll/CRM/project) + two standalone FastAPI device bridges + AI-assistant addon
languages: Python, XML, JavaScript (OWL), ar PO translations
frameworks: Odoo 19 (Odoo.sh hosted), FastAPI + uvicorn (bridges), pyzk, xmlrpc.client, python-dotenv
package_managers: pip (bridge requirements.txt files); Odoo addons-path convention for modules
test_frameworks: Odoo test harness (hr_overtime_management, botify_agent); most test dirs are empty or disabled
deployment: Odoo.sh production tenant (github.com/shamsieh-odoX/shamsieh, branch production); Hikvision webhook service runs on a host reachable by devices; ZKTeco poller runs on a LAN PC; SQLite used inside the bridge

## OVERVIEW

This is the customization layer for "Shamsieh", a Jordanian organization running Odoo 19 on Odoo.sh. The repo mixes three kinds of code: (1) twelve-ish Odoo custom modules covering attendance (fingerprint + face), holidays (including Jordanian "Article 11" hourly departures), overtime with multi-level approval, loans & advances, CRM teams/targets, project extensions, MS-To-Do-style shared lists, an Arabic translation pack, and a public website-lead API; (2) `botify_agent`, an AI-assistant integration addon at protocol v2 that lets an external agent act with each employee's own permissions under grant-based delegation; and (3) two standalone device bridges — a Hikvision access-control webhook receiver and a ZKTeco poller — that push fingerprint punches into Odoo via XML-RPC.

Three modules (`hr_overtime_payroll`, `hr_payroll_custom_ext`, `hr_payroll_jo_custom_ext`) survive only as "REMOVED — uninstall me" stubs so Odoo.sh can upgrade databases where they were once installed — a deliberate migration-hygiene pattern [evidenced in their manifests].

The `botify_agent` manifest comment is unusually rich provenance: it documents protocol v2 (per-operation single-use grants replacing shared-secret HMAC), an Odoo-19 quirk (`_sql_constraints` silently ignored → raw ALTER TABLE for the nonce UNIQUE index), per-tenant custom-model write policy defaulting off, and an ElevenLabs voice-call path reusing the Botify backend's signed-url endpoint — which is almost certainly the sibling TEST-AI project (its systemd units are named `shamsieh-refresh`) [inferred].

## ARCHITECTURE

Three runtimes in one repo:

1. **Odoo.sh tenant** — all `*_custom_ext` / `hr_*` / `shams_*` / `website_lead_api` / `botify_agent` addon dirs. Scheduled jobs as `ir.cron` data:
   - `hr_attendance_custom_ext/data/ir_cron_data.xml`: sync all devices, generate daily attendance status, recompute late/early status, flag missing checkouts, backfill current-month unworked time, purge old raw payloads (+ `_cron_process_pending` on device logs)
   - `hr_holidays_custom_ext/data/ir_cron_data.xml`: renew annual sick leave allocations each Jan 1
2. **Hikvision bridge** (`hikvision_attendance_service/app/main.py`): FastAPI app; devices POST multipart events to `/hikvision/attendance`; events parsed (`hikvision_parser.py`), persisted to SQLite (`db.py` EventStore) with an async retry worker, then forwarded to Odoo via `xmlrpc.client` (`odoo_client.py`). Health endpoints `/health`, `/odoo/ping`; door-heartbeat noise filtered from logs.
3. **ZKTeco bridge** (`zkteco_attendance_service/app/main.py`): long-running poller on a LAN PC using `pyzk`; pushes normalized events into Odoo through `fingerprint.device.ingest_external_attendance_events`.

Cross-cutting: `botify_agent/controllers/{main,grant,_shared}.py` implement identity → delegation credential → single-use grant → RPC execution under `with_user(uid)`; `website_lead_api` exposes one public POST route.

## MODULES

### hr-attendance-custom-ext — HR Attendance Custom Extensions
purpose: Attendance core: fingerprint sync (Hikvision + ZKTeco), face attendance enrollment/matching, daily status views, live status, unworked-time tracking.
path_prefixes: hr_attendance_custom_ext/
key_files: models/fingerprint_device.py (`_cron_sync_all`, ingest endpoint target), models/fingerprint_device_log.py (`_cron_process_pending`, `_cron_purge_raw_payload`), models/hr_attendance_daily_status.py (`_cron_generate_daily_status`, `_cron_backfill_current_month_unworked_time`), models/hr_attendance.py (`_cron_recompute_status`, `_cron_flag_missing_checkouts`), services/zkteco.py, static/src JS dialogs
entrypoints: crons above; controllers for public presence-status reads; post_init_hook
responsibilities: normalize device events into `hr.attendance`; daily status rows; late/early computation; missing-checkout flagging; billable unworked minutes; PIN/face check-in alignment with live status.
invariants: raw device payloads purged after processing; public exposure of attendance fields limited to what officers need (commit 330c17da).
pitfalls: recursion bug in the custom attendance action override was real (86f04052); Owl prop binding broke dialogs (9b558a15); `tests_disabled/` directory exists — coverage intentionally off.
confidence: high

### botify-agent — Botify Agent (protocol v2)
purpose: Embed the external Botify AI assistant and let it act strictly as the requesting employee, via grant-based delegation.
path_prefixes: botify_agent/
key_files: controllers/main.py (/identity, /rpc), controllers/grant.py (/grant), models/botify_policy.py + botify_security.py, tests/test_pure_policy.py, tests/test_grant_and_rpc.py, tests/test_delegation_and_nonce.py
entrypoints: `/botify_agent/identity` (mints per-user delegation credential), `/botify_agent/grant` (single-use per-op grant, X-Botify-Grant header), `/botify_agent/rpc`
responsibilities: verify delegation proof + transport; enforce deny-by-default policy manifest incl. explicit operator decision to open `hr.payslip`/`hr.payslip.line` reads (commit 786781a1); company-scope escalation guard; nonce replay guard with UNIQUE(jti) created via raw ALTER TABLE because Odoo 19 ignores pre-19 `_sql_constraints`; per-tenant classification of this DB's custom models with writes default-off; voice-call button reusing the backend's `/api/widget/:agentId/elevenlabs/signed-url` with the session's identity token.
invariants: shared secret alone can never name a uid (protocol v2 breaking change, `botify_protocol_version: 2`); every RPC consumes its jti once; grant cannot exceed both the user's and delegation's companies.
pitfalls: version-coupled to the Botify backend ("older rebuilds cannot drive this addon"); grant route must stay write-capable (Odoo 17+ read-only cursor default caused ReadOnlySqlTransaction).
confidence: high

### hikvision-bridge — hikvision_attendance_service
purpose: Receive Hikvision attendance/access webhooks, persist durably, forward into Odoo.
path_prefixes: hikvision_attendance_service/
key_files: app/main.py, app/hikvision_parser.py, app/db.py (SQLite EventStore + retry queue), app/odoo_client.py (XML-RPC over `/xmlrpc/2/common|object`), app/config.py (env-driven, SQLITE_PATH default hikvision_bridge.db)
entrypoints: uvicorn app; POST/GET `/hikvision/attendance`, `/health`, `/odoo/ping`
responsibilities: multipart event parsing (employee_no, sub_event_type, verify_mode), punch-type normalization, idempotent forwarding with retry worker, log-noise suppression.
invariants: nothing is dropped silently — failed forwards sit in SQLite until retried.
pitfalls: runs outside Odoo.sh, so its config/secrets live in env files not in git.
confidence: high

### zkteco-bridge — zkteco_attendance_service
purpose: Poll ZKTeco terminals from a LAN PC and push events into Odoo.
path_prefixes: zkteco_attendance_service/
key_files: app/main.py (imports `zkteco` client from hr_attendance_custom_ext/services via sys.path insertion)
entrypoints: `python -m app.main`
responsibilities: pull new punches (pyzk), normalize, XML-RPC push to `fingerprint.device.ingest_external_attendance_events`.
pitfalls: reaches into the Odoo module tree of a *sibling checkout* (`extra_addons/hr_attendance_custom_ext/services`) — deployment layout coupling.
confidence: medium-high

### hr-holidays-custom-ext — HR Holidays Custom Extensions
purpose: Exceptional holidays, leave-balance logic, sick/annual automation, Article 11 hourly departures, remote-work (WFH) requests migrated into Time Off.
path_prefixes: hr_holidays_custom_ext/
key_files: models/*, wizard/*, data/ir_cron_data.xml (Jan 1 sick renewal)
entrypoints: leave flows + cron
responsibilities: hourly-departure allocation type (Article 11 policy), two-step approval fields preserved across merges (1aaf2259), period-based WFH requests with manager+HR approval.
pitfalls: Article 11 merge previously dropped approval fields — merge regressions here are historical fact.
confidence: medium-high

### overtime-suite — hr_overtime_management (+ retired hr_overtime_payroll)
purpose: Overtime requests with multi-level approval and timesheet integration; conversion of approved OT into Time Off (approval-only, no fingerprint banking).
path_prefixes: hr_overtime_management/, hr_overtime_payroll/
key_files: models/, wizard/ (Hourly Departure allocation), report/, tests/test_hr_overtime.py; hr_overtime_payroll/__manifest__.py (uninstall-me stub)
entrypoints: request/approval workflows
responsibilities: OT lifecycle; payroll computation moved out (stub remains for Odoo.sh upgrades).
confidence: medium-high

### loans-advances — hr_loans_advances
purpose: Salary advances and loans with manager/HR approval and repayment handling.
path_prefixes: hr_loans_advances/
key_files: models/, wizard/
responsibilities: loan request lifecycle; approver resolution without requiring res.company read access (c5ffc75c, e3d32f88 fixed AccessError).
confidence: medium

### crm-project-todo — crm_custom_ext / project_custom_ext / shams_todo_groups
purpose: CRM fields/security/teams/targets/dashboards; project security groups, progress, task templates; Microsoft-To-Do-style shared lists with dark mode and due dates.
path_prefixes: crm_custom_ext/, project_custom_ext/, shams_todo_groups/
key_files: crm_custom_ext/models/crm_team_target.py, project_custom_ext/models/project_task_template.py, shams_todo_groups/models/todo_group.py
confidence: low-medium (surveyed by structure)

### website-lead-api — website_lead_api
purpose: Public JSON endpoint for external website contact forms to create CRM leads.
path_prefixes: website_lead_api/
key_files: controllers/*.py — POST `/api/website/lead` (auth='public', csrf=False, cors='*')
responsibilities: API-key validation, honeypot field, IP rate limiting, submission logging (`website.lead.submission.log` with ip/email/lead), multi-site/product form mapping, message escaped into Internal Notes.
invariants: honeypot returns fake success; every lead leaves a submission-log row.
confidence: high

### i18n-and-stubs — shamsieh_i18n_ar + removed-module stubs
purpose: Professional Arabic translations across apps (generated/maintained via scripts/generate_ar_po.py); uninstall-me stubs keep Odoo.sh upgradeable.
path_prefixes: shamsieh_i18n_ar/, scripts/, hr_payroll_custom_ext/, hr_payroll_jo_custom_ext/
confidence: high

## FLOWS

### fingerprint-punch-to-attendance
trigger: device event (push) or poller cycle
steps: Hikvision POST → parse multipart → SQLite store → retry worker → Odoo XML-RPC ingest → `hr.attendance` creation → daily-status cron recomputes late/early/missing-checkout/unworked minutes. ZK variant polls terminal then calls the same ingest method directly.
files: hikvision_attendance_service/app/main.py, hr_attendance_custom_ext/models/fingerprint_device*.py, models/hr_attendance_daily_status.py
confidence: high

### assistant-delegation-v2
trigger: employee opens Botify widget/client action
steps: `/identity` (auth=user) mints per-user delegation credential → browser relays → backend requests `/grant` naming one uid + op class → single-use jti validated → `/rpc` executes under `with_user(uid)` with policy-manifest checks and company escalation guard.
files: botify_agent/controllers/grant.py, controllers/main.py, models/botify_policy.py
confidence: high

### website-lead-ingest
trigger: external site POST `/api/website/lead`
steps: honeypot check → API key validation → rate limit by IP → field validation → `crm.lead` create (sudo) → submission log row.
files: website_lead_api/controllers/
confidence: high

### wfh-and-overtime-approval
trigger: employee request
steps: WFH request over date range → manager then HR approval → becomes Time Off leave; approved overtime may convert to Time Off (no balance banking from fingerprints).
files: hr_holidays_custom_ext/models/, hr_overtime_management/models/
confidence: medium

## APIS

Served:
- Odoo HTTP: `/api/website/lead` (public POST), `/botify_agent/identity|grant|rpc`, public employee-profile reads for officers, portal/customer routes in attendance ext.
- Bridge HTTP: `/hikvision/attendance` (GET health-check style + POST events), `/health`, `/odoo/ping`.

Called (outbound):
- Odoo External API via xmlrpc.client `/xmlrpc/2/common`, `/xmlrpc/2/object` (both bridges)
- Meta Graph API (`graph.facebook.com`, WhatsApp Cloud) and ElevenLabs signed-url `/api/widget/:agentId/elevenlabs/signed-url` consumed indirectly through botify_agent frontend toward the Botify backend [inferred from manifest comments].

## DATABASE

Storage: PostgreSQL via Odoo ORM (tenant DB); SQLite in the Hikvision bridge (`hikvision_bridge.db` event/retry store); no other persistence.
Entities: fingerprint devices + device logs (raw payloads, purgeable), attendance daily status rows, unworked-time records, face templates/enrollment + face attendance logs, WFH/overtime/loan request headers with approval chains, CRM team targets, task templates, todo groups/tasks, lead submission logs, botify nonce/delegation tables (raw-SQL managed).

## TESTS

Frameworks: Odoo's unittest-based harness.
Commands: standard Odoo test runner [inferred].
Present: `hr_overtime_management/tests/test_hr_overtime.py`; `botify_agent/tests/` — six files including pure-function suites (`test_pure_policy.py`, `test_pure_grant_security.py`, `test_pure_canonical.py`) that run without Odoo [inferred from names].
Absent/disabled: `hr_attendance_custom_ext/tests/__init__.py` empty plus a `tests_disabled/` directory; most other modules have no tests at all.

## GIT LESSONS

- bb766e2c → b7fd9851/ace204fd: the auth model was redesigned (shared-secret HMAC → per-operation grants) after recognizing "the shared secret alone can name any uid" as a threat-model violation; security fixes were followed by policy-manifest additions and operator-documented openings (786781a1) rather than ad-hoc exceptions.
- bfe7e8be vs manifest comment on ace204fd: `_sql_constraints` deprecated → `models.Constraint`, but Odoo 19 *silently ignored* the old form in the nonce table — silent schema no-ops forced a raw ALTER TABLE; verify constraints actually exist after major-version migrations.
- e3d32f88/c5ffc75c: employees couldn't submit loans because approver resolution required res.company read; lesson — record-rule failures surface as unrelated AccessErrors deep in flows.
- 86f04052: an override recursed into itself (custom action calling super chain that re-entered); override recursion is a live hazard when wrapping actions.
- d9970685/82136fc4/330c17da: kiosk/PIN/face paths and public profiles needed deliberate read scoping — public auth surfaces were iteratively tightened.
- 9869845b/ac080faa: remote work moved from custom object into Time Off leave flow — consolidating onto platform primitives instead of parallel custom entities.
- eaf9f671: even version bumps were used to clear Odoo.sh build-warning states — release numbers double as deployment signaling on Odoo.sh.
- Early history ("fix", "fix-hikivision", "6587bebd hr_approval") shows terse messages before the team adopted descriptive ones; recent messages carry design rationale inline.

## DECISIONS

- Keep payroll modules removable via uninstall-me stubs rather than breaking Odoo.sh upgrades.
- Deny-by-default Botify policy manifest with explicit, commit-recorded operator decisions for each opened model.
- Device integrations live outside Odoo (FastAPI bridges) because Odoo.sh cannot reach LAN devices; durable SQLite queue bridges unreliable networks.
- Consolidate WFH/overtime/hourly departures onto the native Time Off engine.
- Arabic-first UX: dedicated professional translation module plus generated PO tooling.
- Raw payload retention is temporary by design (purge cron).

## RISKS & TECH DEBT

- Attendance — the most operationally critical module — has its tests disabled/empty; regressions in status/backfill logic would ship silently.
- The ZK bridge imports Odoo-module code via sys.path from an assumed sibling checkout path (`extra_addons/...`) — fragile deployment coupling.
- `/api/website/lead` uses `sudo()` for lead creation; mitigations exist (key, honeypot, rate limit, log) but the CORS `*` + public auth widens surface.
- Protocol lockstep between botify_agent versions and the external Botify backend is breaking-change coupled (documented but manual).
- Two attendance sources (Hikvision push, ZK poll) plus kiosk PIN/face paths multiply edge cases around duplicate punches and overnight shifts.
- Mixed-language/terse early history reduces archaeology value; several "fix"-only commits have no rationale.

## UNCERTAIN

- Whether the Botify backend driving this addon is exactly the TEST-AI repo (strong circumstantial: shamsieh-named systemd units, matching ElevenLabs endpoint, same org family) [inferred].
- Exact Odoo.sh project name and whether bridges run on-prem at Shamsieh sites or a cloud VM.
- Scope of `project_custom_ext` and `crm_custom_ext` business rules (surveyed structurally, not read line-by-line).
- Face-attendance matching algorithm details (enrollment wizard seen; matcher not audited).
- Loan repayment accounting integration depth into accounting entries.
