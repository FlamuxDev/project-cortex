---
cortex-generated: true
title: shamsieh api
tags: [api/project]
---

# shamsieh — API Surface

4 routes. Grouped by owning file; every route names its handler.

## `hikvision_attendance_service/app/main.py`
*module: [[shamsieh/modules/Hikvision-Attendance-Service|hikvision-attendance-service]]*

- **GET** `/health` → health
- **GET** `/hikvision/attendance` → hikvision_attendance_get
- **POST** `/hikvision/attendance` → hikvision_attendance
- **GET** `/odoo/ping` → odoo_ping
