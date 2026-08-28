# Security Policy

## Supported versions

Security fixes are applied to the latest release on the `main` branch.

## Reporting a vulnerability

Please use GitHub's **Security → Report a vulnerability** flow for this repository. Do
not open a public issue for secret-redaction bypasses, path traversal, unsafe repository
discovery, or cases where Cortex persists credentials from indexed code or git history.

Include the affected version, a minimal reproduction, expected behavior, and whether the
issue exposed real credentials. Replace all real secrets with test values before sharing.

## Scope and data model

Cortex is local-first: it does not upload indexed code or telemetry. It does persist
derived signatures, documentation, commit subjects, memories, and task episodes in a
local SQLite database. Secret redaction is defense in depth, not permission to index
repositories you do not trust or have authorization to read.
