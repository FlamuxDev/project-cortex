# Known Limitations

An honest list of what Cortex does **not** do well yet, ranked by pain. If one of these
matters to you, it matters more than anything in the benchmarks.

1. **Symbol-level references are approximate across barrels and re-exports.** `refs` are
   built from imports plus call-name matching. Code that reaches a symbol through
   index-barrels or dynamic registration can be missed; `cortex_impact` falls back to
   stem-name matching, trading false positives for recall. LSP-grade precision would need
   language servers — deliberately deferred. This is the concrete meaning of
   "retrieval-grade, not IDE-grade".

2. **Cross-project ranking is lexical-first.** "How did we implement X elsewhere?" works
   when X's vocabulary is consistent across repos; synonyms can bury the best evidence
   below the packet budget. Embeddings remain the documented upgrade path if this turns
   out to matter in practice.

3. **Dirty worktrees are flagged, not indexed.** Uncommitted files are hashed as-is at
   update time, but memories verified against HEAD may lag a fast-moving tree. Packets
   always state dirty counts and brain-behind distances — read them.

4. **Full-text symbol indexing is capped per project.** `CORTEX_FTS_SYMBOL_CAP`
   (default 100,000) and `CORTEX_FTS_FILE_CAP` (default 20,000) bound how much of a
   project enters the FTS tables, ordered by importance. Repos beyond the cap keep their
   tail reachable by path and content matching but not by symbol name. Raise the cap for
   very large monorepos; the cost is index size.

5. **Cold indexing is slow on very large repos.** A ~48k-symbol repo (including vendored
   content) takes roughly 13 minutes for a full build. Incremental updates are seconds.
   A per-language worker pool would parallelize this if it ever becomes annoying.

6. **Route extraction covers common frameworks only** — Express/Fastify/Hono-style calls,
   NestJS decorators, FastAPI/Flask decorators, Go net/http and gin-style, and Next.js
   file conventions. Unusual or custom routers won't be picked up.

7. **Test→target mapping is import-based plus filename heuristics.** Tests that exercise
   code over HTTP without importing it map only by naming convention, so `TESTS TO RUN`
   can be incomplete for integration-heavy suites.

8. **Non-English support is a glossary bridge, not NLP.** ~40 curated Arabic→English term
   mappings let Arabic tasks hit English code and memories; unlisted vocabulary won't
   resolve. Extend it per install via `$CORTEX_HOME/glossary.json` — see
   [`QUICKSTART.md`](QUICKSTART.md#non-english-tasks). No other language ships a table.

9. **Windows and macOS are untested.** Built and validated on Linux; paths are
   POSIX-assumed in places.

10. **The retrieval eval was authored in-process, by the author, over the author's own
   repos.** Optimism bias is real. The counterweights are independent adversarial and
   hallucination audits run with repo-level ground truth, whose findings drove real fixes
   (cross-project round-robin retrieval, the `EVIDENCE WARNING` guardrail, live git
   freshness). It is still not third-party validation. See
   [`BENCHMARKS.md`](BENCHMARKS.md).

11. **A vanished repository is detected, but never pruned automatically.** If an indexed
    repo is deleted, or its code moves outside the indexed root, the rows stay in the
    brain. That is now surfaced rather than hidden: `cortex projects` prints
    `!! PHANTOM (indexed files gone)`, `cortex doctor` reports `PHANTOM`/`MISSING`, and a
    context packet replaces `FRESHNESS: fresh` with an explicit `⚠ STALE` line naming the
    missing root. Removing the rows is still a manual decision — episodes and memories
    anchored to that project would go with them.

12. **Framework detection is manifest-based and shallow.** It reads dependency names from
    `package.json` (root and `apps/*`, `packages/*`) against a fixed tag list. Frameworks
    outside that list, or used without a direct dependency entry, won't be reported in the
    packet header.
