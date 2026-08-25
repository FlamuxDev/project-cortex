<!-- Title: <type>(<scope>): <short imperative summary> -->

## What & why

<!-- One paragraph: what changed and the problem it solves. Link issues with Fixes #N. -->

## Type

- [ ] `feat` — new capability
- [ ] `fix` — bug fix
- [ ] `docs` — documentation only
- [ ] `refactor` — no behavior change
- [ ] `test` — tests only
- [ ] `chore` — tooling/build/deps

## Verification

- [ ] `python -m unittest discover tests` passes locally
- [ ] New logic covered by tests (fixture repos in `tests/`, no real index touched)
- [ ] Any newly persisted text passes secret redaction (`cortex.langs.redact`)
- [ ] Retrieval/packet changes: reran `scripts/retrieval_eval.py` and report numbers below
      (measured vs simulated clearly labeled)

```
<eval output / score>
```

## Checklist

- [ ] Conventional commit title (`feat(extractors): ...`)
- [ ] Docs updated if behavior changed (`README.md`, `docs/MCP.md`, `ARCHITECTURE.md`)
- [ ] No new runtime dependencies without justification
- [ ] Deterministic: same input → same index → same packet
