# CORTEX REPORT — iscc-Testing

## META
project_id: iscc-testing
root: /home/aboud/Dev/iscc-Testing
kind: Odoo 19 custom-addon suite (HRMS) + embedded AI-assistant widget addon
languages: Python, XML, JavaScript (OWL assets), ar PO translations
frameworks: Odoo 19 (Community dev / Enterprise target for payroll), OWL frontend assets
package_managers: none (Odoo addons-path convention; local docker-compose + odoo.conf gitignored)
test_frameworks: Odoo test harness (`odoo.tests.common`) — only in botify_agent
deployment: local Docker Compose for dev; production target is Odoo.sh (git remote github.com/ISCC557/iscc-Testing, branch Production); government CSV exports are manual uploads

## OVERVIEW

Despite the name and the "ISCC media-content hashing" guess in the brief, this repository has nothing to do with ISCC content identifiers. It is the custom HRMS suite for an organization abbreviated ISCC on Odoo 19: violations/penalties ("لائحة" escalation ladder), continuous-absence detection, external attendance sync, shift-based attendance violations, leave extensions, payroll deduction caps, an employee self-service portal, employee document files with record rules, multi-level approvals, shifts, analysis reports, and Qiwa/GOSI CSV exports (README.md; `iscc_*/__manifest__.py`).

The suite follows two explicit architecture rules stated in README.md: extend standard Odoo models (`hr.attendance`, `hr.leave`, `resource.calendar`, …) rather than fork them, and route every violation through one engine — detectors call `iscc.violation.action_issue()` instead of writing violations directly. Twelve `iscc_*` addon directories exist today plus a thirteenth addon, `botify_agent`, which embeds a floating AI chat widget that acts with each employee's own Odoo permissions via signed identity assertions [inferred from controller docstrings].

History shows active Odoo.sh deployment pain being absorbed into code: version bumps specifically to trigger ORM column migrations, fixes for Odoo 19 API removals (`res.users.groups_id`, removed services), and AccessError fixes so Odoo.sh's own CI tests pass. The working tree also carries an accidental 185 KB UTF-16 docker build log at repo root.

## ARCHITECTURE

Single Odoo database, addon-per-domain layout. No standalone entry points — everything loads inside the Odoo server; scheduled work runs through `ir.cron` records defined as XML data.

- Violation engine core: `iscc_violations/models/iscc_violation.py` (state machine draft→issued→objection→review→confirm/cancel/reverse), `iscc_penalty_rule.py` (per-occurrence escalation ladder), objection model + cancel wizard.
- Detector layer: attendance-driven detectors live in `iscc_shift/models/hr_attendance.py` (codes LATE / EARLY_LEAVE / MISSING_OUT / MIN_HOURS) and continuous absence in `iscc_continuous_absence/models/iscc_continuous_absence.py`; both inherit/emit through `iscc.violation`.
- Scheduled jobs (evidence):
  - `iscc_continuous_absence/data/ir_cron_data.xml` — daily `_cron_detect_continuous_absence`
  - `iscc_attendance_sync/data/ir_cron_data.xml` — hourly `_cron_sync_attendance`, shipped **inactive** with a demo/mock source record
  - `iscc_shift/data/ir_cron_data.xml`, `iscc_employee_files/data/ir_cron_data.xml` — shift/file housekeeping
  - README describes a monthly payroll deduction cron in `iscc_payroll_ext`
- Portal surface: `iscc_ess/controllers/portal.py` extends `CustomerPortal`.
- Botify widget endpoints: `botify_agent/controllers/main.py` (`/botify_agent/identity`, `/botify_agent/rpc`).

## MODULES

### violations-engine — iscc_violations
purpose: Single engine for disciplinary violations: types, penalty ladder, objections, cancellation, notifications, warning PDF.
path_prefixes: iscc_violations/
key_files: models/iscc_violation.py, models/iscc_penalty_rule.py, models/iscc_violation_objection.py, wizard/iscc_violation_cancel.py, data/sample_regulation_data.xml, data/mail_template_data.xml
entrypoints: installed via Apps; consumed by all detector modules
responsibilities: state lifecycle (`action_issue/_reset_to_draft/_register_objection/_start_review/_confirm/_cancel/_reverse_from_leave`), prior-occurrence counting to pick the N-th rung of the penalty ladder, deduction computation, employee notification.
invariants: all detectors must issue via `action_issue()` (README architecture rule).
pitfalls: leave reversal interacts with `iscc_leave_ext`; cancellation has two modes (`mode="cancel"` vs reverse) in `_apply_cancellation`.
confidence: high

### attendance-sync — iscc_attendance_sync
purpose: Pull punches from external systems (Sprinklr or generic HTTP JSON, plus a mock provider) into `hr.attendance`.
path_prefixes: iscc_attendance_sync/
key_files: models/iscc_attendance_source.py, models/iscc_attendance_punch.py, data/ir_cron_data.xml
entrypoints: cron `model._cron_sync_attendance()` (inactive by default), manual `action_sync`
responsibilities: provider abstraction (`mock|sprinklr|http_json` → `_fetch_punches_http` using `requests.get` timeout 30), employee matching by `iscc_external_attendance_id`, overnight-punch handling.
invariants: cron ships disabled with a "Sprinklr (Demo/Mock)" source row — enabling is a deliberate operator act.
pitfalls: matching by external id fails silently if the field is unpopulated [inferred from `_match_employee`].
confidence: high

### shift-detector — iscc_shift
purpose: Shift A/B/C definitions, admin assignment history, overnight shift-date attribution, and the attendance-violation detector.
path_prefixes: iscc_shift/
key_files: models/hr_attendance.py (ATTENDANCE_VIOLATION_CODES = LATE, EARLY_LEAVE, MISSING_OUT, MIN_HOURS), models/iscc_violation.py (adds source-attendance link), data/violation_type_data.xml
entrypoints: inherits `iscc.violation`; evaluated around attendance writes/crons
responsibilities: breach evaluation against assigned shift windows; keeps violations linked to the generating `hr.attendance` row so corrections can re-sync them.
invariants: every attendance-driven violation records `iscc_source_attendance_id` (field help text states this purpose).
pitfalls: README still names a separate module `iscc_attendance_violations` (R17); that directory was deleted and its logic now lives here — documentation drift.
confidence: high

### continuous-absence — iscc_continuous_absence
purpose: Daily detection of employees with no punches for N days; auto-issue absence violation + report.
path_prefixes: iscc_continuous_absence/
key_files: models/iscc_continuous_absence.py, wizard/iscc_absence_scan.py, data/ir_cron_data.xml
entrypoints: daily cron `model._cron_detect_continuous_absence()`; manual scan wizard
responsibilities: scan, sequence-numbered case creation, report views.
confidence: medium-high

### payroll-deductions — iscc_payroll_ext
purpose: Monthly deduction statements with a cap and carry-over between months, posted onto Enterprise payslips.
path_prefixes: iscc_payroll_ext/
key_files: models/iscc_deduction_statement.py (`generate_for_period`, `_prev_carry`, `action_confirm/action_post`, `_iscc_propagate_carryover`, `_iscc_refresh_period_payslip`), wizard/iscc_deduction_generate.py, data/hr_payslip_input_type_data.xml
entrypoints: statement workflow + generation wizard
responsibilities: aggregate confirmed violations per employee/period, cap enforcement, carry remaining balance forward, feed DEDUCTION payslip input (the data record enables `available_in_attachments=True` without which Odoo never creates the input — comment cites R11 posting).
invariants: depends on Enterprise `hr_payroll` (README says skip on Community).
pitfalls: carry-over propagation order across periods; reset-to-draft path re-refreshes payslips.
confidence: medium-high

### ess-portal — iscc_ess
purpose: Employee self-service portal pages for violations, details, objection filing.
path_prefixes: iscc_ess/
key_files: controllers/portal.py (extends `CustomerPortal`)
entrypoints: portal routes `/my/...` (`portal_my_violations`, `portal_my_violation_detail`, `portal_file_objection`, `portal_my_objections`)
responsibilities: portal counters, own-record scoping via `_iscc_employee`, objection upload.
invariants: employees see only their own records (commit 99c45d3 restricted the deduction statement likewise).
confidence: high

### leave-integration — iscc_leave_ext
purpose: Reverse pending violations when a leave is approved; convert permissions into leave balance.
path_prefixes: iscc_leave_ext/
key_files: models/hr_leave.py, models/hr_leave_type.py, models/iscc_violation_type.py, data/hr_leave_type_data.xml
entrypoints: hooks into `hr.leave` approval flow
responsibilities: on approval call `action_reverse_from_leave`; provide leave-type data.
pitfalls: history shows the hook caused AccessError inside Odoo.sh's hr_holidays tests (commit ee07f48) and needed an Odoo-19-specific fix (c76fcc3).
confidence: medium-high

### hr-base-and-misc — iscc_hr_base / iscc_approvals / iscc_employee_files / iscc_reports / iscc_gov_integration
purpose: Shared foundation (groups/menus/company policy fields), multi-level approval routes wired into the violation model, employee documents with CSV import + record rules + purge cron, analysis-only report menus, and CSV generators for Qiwa/GOSI.
path_prefixes: iscc_hr_base/, iscc_approvals/, iscc_employee_files/, iscc_reports/, iscc_gov_integration/
key_files: iscc_hr_base/models/res_company.py (+res_config_settings, hr_employee); iscc_approvals/models/iscc_approval_route.py; iscc_gov_integration/models/iscc_gov_export.py
entrypoints: gov export `action_generate()` button
responsibilities: base config; approval routing; document governance; reporting menus; government file rows.
invariants: install order matters (README prescribes hr_base → violations → rest).
pitfalls: `_build_rows` is explicitly marked "PLACEHOLDER column mapping — align with the real Qiwa/GOSI template", and the class docstring flags that Qiwa/GOSI have no public write-API, hence CSV + manual upload.
confidence: high (structure), low (gov export content)

### botify-widget — botify_agent
purpose: Floating AI chat widget whose tool calls execute as the logged-in employee, not a shared integration account.
path_prefixes: botify_agent/
key_files: controllers/main.py, models/botify_security.py, static/src/js/botify_widget.js, tests/test_identity.py, tests/test_rpc_permissions.py
entrypoints: `/botify_agent/identity` (auth="user"), `/botify_agent/rpc` (HMAC-signed, allowlisted methods)
responsibilities: mint 120s single-use HS256 identity assertion server-side; execute Botify calls under `with_user(uid)` (su=False) so ACLs/record rules/company scope apply; method allowlist (READ/WRITE/ACTION sets) with hard FORBIDDEN set (`unlink`, `sudo`, `with_user`, `browse`, `_`-prefixed) and MAX_LIMIT=200.
invariants: browser never names the user; endpoint must be safe on its own terms (auth="none"); deletion is "a decision, not an oversight".
pitfalls: mirrors SAFE_ACTION_METHODS in a TypeScript backend ("keep the two in step") — a manual cross-repo contract.
confidence: high

## FLOWS

### violation-to-paypayslip
trigger: any detector (shift breaches, continuous absence) or manual issue
steps: detector evaluates → `iscc.violation.action_issue()` → notification mail → optional objection/review → confirm → monthly `generate_for_period` aggregates with cap + prior carry-over → confirm/post → DEDUCTION salary attachment becomes payslip input → carry-over propagated to next period.
files: iscc_violations/models/iscc_violation.py, iscc_payroll_ext/models/iscc_deduction_statement.py, iscc_payroll_ext/data/hr_payslip_input_type_data.xml
confidence: medium-high

### attendance-ingest
trigger: hourly cron (when enabled) or manual sync
steps: `iscc.attendance.source._cron_sync_attendance` → fetch punches since cursor (`requests.get` or mock) → match employee by external id → create `hr.attendance` (overnight-aware) → shift detector may issue violations linked to source attendance.
files: iscc_attendance_sync/models/*.py, iscc_shift/models/hr_attendance.py
confidence: high

### botify-chat-as-user
trigger: employee clicks floating widget
steps: client action calls `/botify_agent/identity` (server reads `request.env.user`, signs assertion) → browser relays to Botify → Botify verifies signature/jti/expiry → later Botify POSTs `/botify_agent/rpc` with HMAC naming uid → Odoo executes allowlisted method under `with_user(uid)`.
files: botify_agent/controllers/main.py, botify_agent/static/src/js/botify_widget.js
confidence: high

## APIS

Served (HTTP):
- POST/GET `/botify_agent/identity`, `/botify_agent/rpc` (botify_agent/controllers/main.py)
- ESS portal routes under `/my` (iscc_ess/controllers/portal.py)

Called (outbound):
- Configurable attendance-provider HTTP JSON endpoints via `requests.get(url, headers, params, timeout=30)` (iscc_attendance_sync/models/iscc_attendance_source.py:122); mock provider makes no network call.
- Qiwa/GOSI: deliberately no API integration — CSV generated for manual upload.

CLI surface: none (Odoo shell/docker commands documented in README).

## DATABASE

Storage: PostgreSQL through the Odoo ORM exclusively; no raw SQL found.
Entities (custom models): `iscc.violation` (disciplinary case w/ source attendance link), `iscc.violation.type`, penalty rule ladder, `iscc.violation.objection`, `iscc.continuous.absence`, `iscc.attendance.source/punch` (external ingest + cursor), `iscc.shift` (+ assignment history), `iscc.approval.route`, `iscc.employee.document`, `iscc.deduction.statement`/`.line`, `website lead` n/a. Standard models extended: `hr.attendance`, `hr.leave`, `hr.leave.type`, `hr.employee`, `res.company`, `res.config.settings`, payslip input types. Sequences (ir_sequence) number cases; mail templates notify.

## TESTS

Frameworks: Odoo's built-in `odoo.tests` (TransactionCase style) — present ONLY under `botify_agent/tests/` (`test_identity.py`, `test_rpc_permissions.py`). The 12 HR modules contain no automated tests. Commands: standard Odoo test runner (`--test-enable --stop-after-init -u <module>`) [inferred]; no CI config found beyond Odoo.sh's own build checks referenced in commit messages.

## GIT LESSONS

- dd0c65c..ce403b9: history dominated by "Add files via upload" / bulk delete cycles — GitHub web-UI editing produced noisy, hard-to-audit history; treat history as weak evidence for intent.
- 49a6afa & 065a068: version bumps ("19.0.1.1.0", "19.0.1.2.0") made *specifically* to trigger ORM migration for new fields on Odoo.sh — on this deployment, schema changes need a manifest bump to land.
- ee07f48 & c76fcc3: leave hooks broke Odoo.sh's own hr_holidays tests with AccessError; lesson — overrides must not assume elevated access when running inside platform test flows.
- 2012eba: Odoo 19 removed `res.users.groups_id` — identity assertion crashed; lesson: pin assumptions about core schema per Odoo version.
- 4ef751a: Odoo 19 removed a frontend service; replaced with `rpc()`. 23f14af: Odoo command palette swallowed chat keystrokes — global hotkeys conflict with core UI.
- c77cb22 + 96dc887: double-mount race in the floating widget; final fix passes the identity token directly instead of racing mount/identify — race conditions in widget bootstrap were fixed at the data-flow level, not with locks.
- 99c45d3: portal security tightening after the fact (deduction statement limited to own record) — record-scoping was retrofitted; audit new portal routes for it up front.

## DECISIONS

- Extend, don't fork core Odoo models; new modules only at clear boundaries (README "Architecture rules").
- One violation engine; detectors delegate to `action_issue()`.
- Attendance sync cron ships inactive with a mock demo source — safe-by-default rollout.
- Payroll integration requires Enterprise `hr_payroll`; explicitly skipped on Community.
- Government reporting via CSV + manual upload because platforms lack open write APIs (flagged in code).
- Botify RPC: deny-by-default method allowlist, forbidden-method hard stop, limit cap 200, no deletion ever.

## RISKS & TECH DEBT

- Near-zero automated tests on business-critical logic (violations, payroll carry-over, absence detection) — only botify_agent is covered.
- `install_log.txt` (185 KB UTF-16 Windows docker log) committed at repo root; junk + possible environment leakage.
- README drift: lists `iscc_attendance_violations` (deleted; logic moved into `iscc_shift`) and names `iscc_shifts` while the dir is `iscc_shift`.
- Qiwa/GOSI export column mapping is an acknowledged PLACEHOLDER — wrong-file risk if used before alignment.
- Manual cross-repo contract: method allowlist must mirror a TypeScript service elsewhere ("keep the two in step") — silent drift risk.
- History hygiene: web-upload/delete churn obscures provenance; branch sprawl (`main` vs `Production` divergence, origin HEAD → main).
- Payroll carry-over and overnight-shift attribution are exactly the kind of date/money logic with no regression net.

## UNCERTAIN

- Actual production hosting split (Odoo.sh vs on-prem Docker) inferred from commit messages, not config files (compose/conf are gitignored).
- Sprinklr provider payload shape unknown (mock-first development).
- Whether `iscc_reports` contains any Python logic at all (only views/xml observed).
- Exact monthly payroll cron schedule (README mentions it; cron XML not seen in tree — possibly defined differently or pending).
- Identity of "ISCC" organization and relation to the shamsieh project (both carry a `botify_agent` addon; likely same consultancy/client family [inferred]).
