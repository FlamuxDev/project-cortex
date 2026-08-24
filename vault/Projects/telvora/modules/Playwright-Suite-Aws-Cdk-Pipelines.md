---
cortex-generated: true
title: playwright-suite-aws-cdk-pipelines
tags: [module]
---

# Playwright suite + AWS CDK + pipelines

**Project:** [[telvora]] | **Confidence:** verified | **verified@** `7423f040ed46`
**Owns:** `e2e/tests/*.spec.ts (38 files),infra/cdk/{lib,scripts},.github/workflows`

purpose: black-box flows against running stack (EN+AR browser locales); IaC + CI/CD
path_prefixes: e2e/tests/*.spec.ts (38 files), infra/cdk/{lib,scripts}, .github/workflows
key_files: playwright.config.ts (two locale projects, webServer autostart), infra/cdk/lib/platform-stack.ts (Fargate web/core/ml, EFS access points, MigrationTask `/migrate bootstrap-up` barrier at line ~479-486), ci.yml (three jobs, live Postgres services, restricted-role test runs), deploy.yml (OIDC, SHA-tagged immutable images)
confidence: verified

