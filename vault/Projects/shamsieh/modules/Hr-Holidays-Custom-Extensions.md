---
cortex-generated: true
title: hr-holidays-custom-extensions
tags: [module]
---

# HR Holidays Custom Extensions

**Project:** [[shamsieh]] | **Confidence:** inferred | **verified@** `ad14342a33e9`
**Owns:** `hr_holidays_custom_ext/`

purpose: Exceptional holidays, leave-balance logic, sick/annual automation, Article 11 hourly departures, remote-work (WFH) requests migrated into Time Off.
path_prefixes: hr_holidays_custom_ext/
key_files: models/*, wizard/*, data/ir_cron_data.xml (Jan 1 sick renewal)
entrypoints: leave flows + cron
responsibilities: hourly-departure allocation type (Article 11 policy), two-step approval fields preserved across merges (1aaf2259), period-based WFH requests with manager+HR approval.
pitfalls: Article 11 merge previously dropped approval fields — merge regressions here are historical fact.
confidence: medium-high

## Files (40+)

- `hr_holidays_custom_ext/__init__.py`
- `hr_holidays_custom_ext/__manifest__.py`
- `hr_holidays_custom_ext/hooks.py`
- `hr_holidays_custom_ext/migrations/19.0.1.3.11/post-migrate.py`
- `hr_holidays_custom_ext/migrations/19.0.1.3.4/post-migrate.py`
- `hr_holidays_custom_ext/migrations/19.0.1.3.7/post-migrate.py`
- `hr_holidays_custom_ext/migrations/19.0.1.3.8/post-migrate.py`
- `hr_holidays_custom_ext/migrations/19.0.1.4.0/post-migrate.py`
- `hr_holidays_custom_ext/migrations/19.0.1.4.3/post-migrate.py`
- `hr_holidays_custom_ext/models/__init__.py`
- `hr_holidays_custom_ext/models/hr_annual_leave_carryover_log.py`
- `hr_holidays_custom_ext/models/hr_employee.py`
- `hr_holidays_custom_ext/models/hr_exceptional_holiday.py`
- `hr_holidays_custom_ext/models/hr_exceptional_holiday_approval_line.py`
- `hr_holidays_custom_ext/models/hr_hourly_departure_allocation_log.py`
- `hr_holidays_custom_ext/models/hr_hourly_departure_balance.py`
- `hr_holidays_custom_ext/models/hr_hourly_departure_conversion.py`
- `hr_holidays_custom_ext/models/hr_leave.py`
- `hr_holidays_custom_ext/models/hr_leave_allocation.py`
- `hr_holidays_custom_ext/models/hr_leave_approval_trail.py`
- `hr_holidays_custom_ext/models/hr_leave_balance_summary.py`
- `hr_holidays_custom_ext/models/hr_leave_type.py`
- `hr_holidays_custom_ext/models/hr_overtime_leave_helper.py`
- `hr_holidays_custom_ext/models/hr_overtime_request.py`
- `hr_holidays_custom_ext/models/hr_sick_leave_renewal_log.py`
