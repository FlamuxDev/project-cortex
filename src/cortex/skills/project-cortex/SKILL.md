---
name: project-cortex
description: Use Project Cortex for codebase discovery, impact analysis, test selection, freshness checks, and durable engineering memory. Apply to non-trivial engineering work in repositories indexed by Cortex; skip trivial questions or environments where Cortex is unavailable.
license: MIT
metadata:
  author: Project Cortex contributors
  repository: https://github.com/FlamuxDev/project-cortex
---

# Project Cortex

Use Cortex as the evidence layer for repository work. Keep the user's request and
the repository's own instructions authoritative.

## Start a task

For non-trivial engineering work, call `cortex_task_start` before broad
exploration. Pass the user's task verbatim and include `cwd` or `project` when
the server cannot reliably infer the active workspace.

Use the packet as a prioritized map:

1. Check `index_sync`, freshness, and evidence warnings. The default `auto`
   mode fingerprints and refreshes changed indexable code before returning.
2. Read the named `PRIMARY FILES` before expanding the search.
3. Verify critical claims against the current source, especially when the
   worktree is dirty, the index is behind, or task terms were not found.
4. If sync is `failed` or `unstable`, verify critical claims in source. Use a
   forced refresh only after the worktree settles; use `never` only when an
   intentionally stale diagnostic is required.

If MCP tools are unavailable, use the CLI equivalent:

```bash
cortex task start "<task>"
```

Capture the returned session id for task completion.

For an unfamiliar repository, onboarding request, or architecture question,
call `cortex_architecture` once before deeper navigation. It provides areas,
boundaries, entrypoints, dependency hotspots, and API/data/test surfaces. Skip
it when the task packet already provides enough local evidence.

## Navigate with narrow evidence

- Use `cortex_symbol` for exact definitions.
- Use `cortex_references` and `cortex_callers` for usage and dependency paths.
- Use `cortex_search` when the packet does not identify enough evidence.
- Use `cortex_module` for maintained invariants and pitfalls.
- Expand to repository-wide search only when Cortex evidence is insufficient.

Treat Cortex as retrieval-grade guidance, not a replacement for reading source,
running tests, or using an LSP for exact refactors.

## Before changing code

Call `cortex_impact` before cross-module, public API, schema, or shared-symbol
changes. Review direct and indirect dependents, mapped tests, routes, database
entities, and past fixes. With CLI-only access, run:

```bash
cortex impact "<file-or-symbol>"
```

Do not infer permission for unrelated changes from the impact report.

After a non-trivial implementation, call `cortex_preflight` before final
verification. Its default base `HEAD` covers staged, unstaged, and untracked
worktree changes; use the repository's target branch (for example
`origin/main`) when the review must also cover commits on the current branch.
Review its risk reasons, dependents, public/data surfaces, and selected tests.

## Verify and close the loop

Run the related tests named in the packet plus any checks required by the
repository. After the implementation is settled:

1. Run the tests selected by the packet/preflight plus repository-required
   checks, then call `cortex_update` so completion evidence matches final source.
2. Call `cortex_task_complete` with the session id, actual outcome, tests run,
   and only durable root-cause or invariant lessons worth resurfacing later.

CLI equivalent:

```bash
cortex update <project>
cortex task complete --session <id> --outcome tested \
  --tests-run "<commands run>" --lessons "<durable lesson>"
```

Do not invent lessons, test results, or verification evidence. If Cortex is not
installed or the project is not indexed, state that briefly and continue with
normal repository tools unless the user asked for Cortex setup.
