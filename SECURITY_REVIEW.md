# Known Limitations

Honest list of what Cortex does NOT do well yet, ranked by pain.

1. **Symbol-level references are approximate across barrels/re-exports.** `refs` are built from
   imports + call-name matching. Code that reaches a symbol through index-barrels or dynamic
   registration can be missed by callers (impact falls back to stem-name matching, which trades
   false positives for recall). LSP-grade precision would need language servers — deliberately
   deferred.
2. **Cross-project ranking is lexical-first.** "How did we implement X elsewhere?" works when X's
   vocabulary is consistent; synonyms across projects can bury the best evidence below the packet
   budget. Embeddings remain the documented upgrade path if this matters in practice.
3. **Dirty worktrees are flagged, not indexed.** Uncommitted files are hashed as-is at update time,
   but memories verified against HEAD may lag a fast-moving tree (e.g., Mushagil M03 wave).
   Packets always state dirty counts and brain-behind distances — read them.
4. **mythos cold index is slow** (~13 min of the 14-min full build; 48k symbols incl. vendored
   content). Incremental is seconds. A per-language worker pool would parallelize if it ever annoys.
5. **Route extraction covers common frameworks only** (Express/Fastify/Hono-style calls, NestJS
   decorators, FastAPI/Flask decorators, Go net/http+gin-style, Next.js file conventions).
   Unusual routers (e.g., custom registries) appear only via delegate reports.
6. **Test→target mapping is import-based + filename heuristics.** Tests exercising code via HTTP
   without importing it map only by naming conventions.
7. **Arabic support is a glossary bridge, not NLP.** ~40 curated AR→EN term mappings make Arabic
   tasks hit English code/memories; unlisted vocabulary won't resolve. Extend `AR_EN` in
   `search.py` as needed.
8. **Episode quality depends on the lessons agents provide.** Cortex gathers evidence
   deterministically but never invents root causes; junk lessons fail retrieval relevance
   and stay dormant rather than polluting packets. Auto-promotion caps at module/pitfall
   scope; global scope requires an explicit human `cortex episode promote --scope global`.
9. **Precision metrics need real usage.** Hit-rate dashboards stay n/a below 3 measured
   implementation tasks (discovery-only and abandoned tasks don't count). The simulated
   ~94% token benchmark remains labeled simulated until unaided-baseline sessions are logged.
9. **Windows/macOS untested.** Built and validated on Linux; paths are POSIX-assumed in places.
10. **Git-worktree detection maps via git-common-dir**; exotic setups (submodules inside indexed paths) may resolve to the parent project.
11. **The friendly eval was authored in-process** (optimism bias). Counterweights: independent
    adversarial + hallucination audits ran with repo-level ground truth; their findings drove
    real fixes. Keep both audits in the loop after major changes.
