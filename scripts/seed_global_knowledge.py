"""Seed global (cross-project) engineering knowledge into memories."""
from __future__ import annotations
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from cortex.db import connect

GLOBAL_KNOWLEDGE = [
    ("principle", "Verified-but-never-wired trap",
     "CVM Phase 10 shipped eight capabilities with passing unit tests and facade exports but NO "
     "caller — screens showed empty tables for months while the suite stayed green. "
     "A unit test proves a function WORKS; nothing proved it RUNS. "
     "Evidence: Dev/CVM/tools/wiring/check.ts; gate checks register(name), not imports.",
     ["Dev/CVM/tools/wiring/check.ts"]),
    ("principle", "Composite foreign keys for tenant isolation",
     "Cross-tenant access hole found via single-column FK: a row could reference a parent in ANOTHER "
     "tenant. Fix pattern: composite FKs (tenant_id, parent_id) referencing unique(tenant_id, id) on "
     "every parent relation. Found independently in Campify (ADR-0010) and applied in Mushagil/Telvora.",
     ["Dev/Campify ADR-0010"]),
    ("pitfall", "Fail-open configuration on missing NODE_ENV",
     "Campify commit 578b127: missing/unset NODE_ENV defaulted to permissive mode. Configuration must "
     "fail closed — refuse to boot when environment is undefined."),
    ("principle", "RLS as defense-in-depth, not the only wall",
     "Mushagil/CVM/Telvora enforce Postgres FORCE ROW LEVEL SECURITY per tenant AND validate tenancy "
     "in the app layer. Mawid-AI deliberately relies on app-layer only (documented trade-off). "
     "When touching any tenants table: check both layers exist or the omission is documented.", None),
    ("principle", "Mutation + audit + outbox in one transaction",
     "Mushagil M02+ pattern: every state mutation writes the row, the audit event, and the outbox "
     "record in a single DB transaction; relay publishes async. Prevents silent audit loss.", None),
    ("pitfall", "Claim-vs-retry double processing",
     "CVM game-day finding: claiming a job then retrying after timeout can process twice unless the "
     "claim is atomic (advisory lock / lease token / ON CONFLICT). Luma uses (workerId, lease_generation) "
     "fencing tokens; Mushagil uses idempotency_key table. Never catch 25P02 (serialization failure) as "
     "'already exists' — distinguish conflict outcomes.", None),
    ("principle", "Immutable published snapshots as source of truth",
     "Mushagil ADR-0004: published entities are stored as immutable JSONB snapshots; readers never join "
     "live drafts. Same idea in Telvora decision engine inputs. Avoids read-your-drafts bugs.", None),
    ("principle", "Route ownership conflicts resolved immediately",
     "Telvora AGENT_BUILD_PROTOCOL: when a new phase's route spec conflicts with an existing phase's "
     "route ownership, resolve immediately (move/rename) instead of shipping compatibility shims.", None),
    ("pitfall", "Docs drift faster than code",
     "Recurring: Mawid-AI OpenAPI documented 3 deleted endpoints; TEAM-GUIDE named wrong session cookie; "
     "Luma worker API implemented despite docs claiming otherwise; Mushagil CURRENT_STATE.md lagged reality. "
     "Trust code+git over prose; when updating docs, grep for stale references.", None),
    ("principle", "Bilingual (ar/en, RTL-first) is a core constraint",
     "Most products here are Arabic-first with RTL UI: Campify, Mushagil, Telvora console, sham-v2, "
     "shamsieh. Any new UI work must plan locale catalogs, RTL-safe layout and Arabic formatting "
     "(numbers/dates/money) from day one.", None),
]


def main():
    con = connect()
    n = 0
    for entry in GLOBAL_KNOWLEDGE:
        scope, title, body = entry[0], entry[1], entry[2]
        sources = entry[3] if len(entry) > 3 else None
        con.execute("""INSERT INTO memories(project_id,scope,title,body_md,confidence,origin,
                       source_files_json) VALUES (NULL,?,?,?,?,?,?)""",
                    (scope, title, body, "verified" if sources else "strongly_inferred",
                     "curated", __import__("json").dumps(sources or [])))
        n += 1
    con.commit()
    from cortex.indexer import _refresh_memory_fts
    _refresh_memory_fts(con)
    print(f"seeded {n} global memories")


if __name__ == "__main__":
    main()
