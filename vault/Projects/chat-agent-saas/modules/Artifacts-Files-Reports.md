---
cortex-generated: true
title: artifacts-files-reports
tags: [module]
---

# artifacts / files / reports

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Chat-generated files: unified `create_file` tool producing CSV/XLSX/PDF/DOCX (`services/ai/fileTools.ts`, 1252 lines) delivered as message attachments with a no-text fallback (`chat.service.ts:1728-1731`). Generation is hard-gated on explicit user intent (commit a25053a) so the model doesn't spontaneously produce downloads; a silent model with files ready still delivers via `fileReadyFallback`.
- Standalone upload/download surface for dashboards at `/api/files` (`files.routes.ts`) against S3/MinIO (`utils/s3.ts`); private media served through HMAC-signed short-lived URLs keyed off ENCRYPTION_KEY (README:63).
- ReportArtifacts: revisionable Excel/Word reports generated from conversations during Odoo/Dynatrace/Splunk investigations; object key + spec/provenance stored **encrypted**, client gets short-lived capability token hashed at rest; revisions linked via self-relation (`schema.prisma:610-657`, `modules/artifacts/artifact.routes.ts` + test). Evidence extraction feeding these comes from the integrations `evidence.ts` framework — every observed tool result during `runToolLoop` is recorded via the `onToolResult` callback (`chat.service.ts:1669-1671`).

