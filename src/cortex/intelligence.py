"""Repository-level architecture and change preflight intelligence."""
from __future__ import annotations

import pathlib
import re
import subprocess

from cortex import search
from cortex.db import code_root
from cortex.indexer import refresh_project


def _rows(con, sql: str, args: tuple) -> list[dict]:
    return [dict(row) for row in con.execute(sql, args)]


def _area(path: str) -> str:
    parts = pathlib.PurePosixPath(path).parts
    if len(parts) <= 1:
        return "(root)"
    if parts[0] in {"src", "app", "lib", "packages", "services", "apps"} and len(parts) > 2:
        return "/".join(parts[:2])
    return parts[0]


def architecture(con, project_id: str, refresh: str = "auto") -> dict:
    """Return a compact, evidence-backed structural map of one repository."""
    project = con.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if not project:
        return {"error": f"unknown project {project_id!r}"}
    sync = refresh_project(con, project_id, mode=refresh)

    files = _rows(con, """SELECT path,lang,loc,importance,is_test,is_entry
                            FROM files WHERE project_id=?""", (project_id,))
    symbols = con.execute(
        "SELECT COUNT(*) n FROM symbols WHERE project_id=?", (project_id,)).fetchone()["n"]
    if not files:
        return {"project": project_id, "path": code_root(project), "index_sync": sync,
                "summary": {"files": 0, "symbols": symbols, "loc": 0}, "languages": [],
                "areas": [], "entrypoints": [], "modules": [], "boundaries": [],
                "hotspots": [], "api_surface": [], "data_surface": [],
                "test_surface": {"files": 0, "ratio": 0.0, "kinds": []},
                "warnings": ["No indexable code is present in the current snapshot."]}

    langs: dict[str, dict] = {}
    areas: dict[str, dict] = {}
    for f in files:
        lang = f["lang"] or "other"
        item = langs.setdefault(lang, {"language": lang, "files": 0, "loc": 0})
        item["files"] += 1
        item["loc"] += f["loc"] or 0
        name = _area(f["path"])
        a = areas.setdefault(name, {"area": name, "files": 0, "loc": 0, "tests": 0})
        a["files"] += 1
        a["loc"] += f["loc"] or 0
        a["tests"] += int(bool(f["is_test"]))

    boundary_counts: dict[tuple[str, str], int] = {}
    for row in con.execute("""SELECT src_path,dst_path FROM refs
                              WHERE project_id=? AND dst_path IS NOT NULL""", (project_id,)):
        src, dst = _area(row["src_path"]), _area(row["dst_path"])
        if src != dst:
            boundary_counts[(src, dst)] = boundary_counts.get((src, dst), 0) + 1

    hotspots = _rows(con, """SELECT f.path, f.importance,
                               COUNT(DISTINCT r.src_path) AS inbound
                               FROM files f LEFT JOIN refs r
                                 ON r.project_id=f.project_id AND r.dst_path=f.path
                               WHERE f.project_id=? AND f.is_test=0
                               GROUP BY f.path ORDER BY inbound DESC, f.importance DESC LIMIT 10""",
                     (project_id,))
    modules = _rows(con, """SELECT name,path_prefixes,purpose,confidence
                              FROM modules WHERE project_id=? ORDER BY name LIMIT 20""",
                    (project_id,))
    apis = _rows(con, """SELECT method,route,handler_path,handler_symbol,auth
                           FROM apis WHERE project_id=? ORDER BY route,method LIMIT 30""",
                 (project_id,))
    api_count = con.execute(
        "SELECT COUNT(*) n FROM apis WHERE project_id=?", (project_id,)).fetchone()["n"]
    data = _rows(con, """SELECT name,kind,file_path FROM db_entities
                           WHERE project_id=? ORDER BY kind,name LIMIT 30""", (project_id,))
    data_count = con.execute(
        "SELECT COUNT(*) n FROM db_entities WHERE project_id=?", (project_id,)).fetchone()["n"]
    kinds = _rows(con, """SELECT COALESCE(kind,'unknown') kind, COUNT(*) count
                            FROM tests WHERE project_id=? GROUP BY kind ORDER BY count DESC""",
                  (project_id,))
    test_files = sum(1 for f in files if f["is_test"])
    code_files = max(len(files) - test_files, 1)
    warnings = []
    if not modules:
        warnings.append("No curated module map exists; areas are inferred from paths.")
    if test_files == 0:
        warnings.append("No test files were detected.")
    if sync.get("status") in {"failed", "unstable"}:
        warnings.append("The index could not be proven current; verify critical paths in source.")

    return {
        "project": project_id,
        "path": code_root(project),
        "index_sync": sync,
        "summary": {"files": len(files), "symbols": symbols,
                    "loc": sum(f["loc"] or 0 for f in files),
                    "apis": api_count, "db_entities": data_count, "tests": test_files},
        "languages": sorted(langs.values(), key=lambda x: (-x["loc"], x["language"])),
        "areas": sorted(areas.values(), key=lambda x: (-x["loc"], x["area"]))[:20],
        "entrypoints": [f["path"] for f in sorted(files, key=lambda x: -x["importance"])
                         if f["is_entry"]][:20],
        "modules": modules,
        "boundaries": [{"from": src, "to": dst, "references": count}
                       for (src, dst), count in sorted(boundary_counts.items(),
                       key=lambda item: -item[1])[:20]],
        "hotspots": hotspots,
        "api_surface": apis,
        "data_surface": data,
        "test_surface": {"files": test_files,
                         "ratio": round(test_files / code_files, 2), "kinds": kinds},
        "warnings": warnings,
    }


def _git(root: str, *args: str, text: bool = True):
    return subprocess.run(["git", "-C", root, *args], capture_output=True,
                          text=text, timeout=60, check=False)


def _validate_base(root: str, base: str) -> str:
    if not base or base.startswith("-") or not re.fullmatch(r"[A-Za-z0-9_./@{}~^:+-]+", base):
        raise ValueError("base must be a safe git revision, e.g. HEAD or origin/main")
    run = _git(root, "rev-parse", "--verify", "--end-of-options", f"{base}^{{commit}}")
    if run.returncode:
        raise ValueError(f"git base {base!r} does not resolve to a commit")
    return run.stdout.strip()


def _changed_files(root: str, base: str) -> list[dict]:
    run = _git(root, "diff", "--name-status", "-z", "--find-renames", base, "--", text=False)
    if run.returncode:
        raise ValueError(run.stderr.decode("utf-8", "replace")[:300])
    parts = run.stdout.split(b"\0")
    changed: list[dict] = []
    i = 0
    while i < len(parts) and parts[i]:
        status = parts[i].decode("ascii", "replace")
        i += 1
        if status.startswith(("R", "C")):
            if i + 1 >= len(parts):
                break
            old = parts[i].decode("utf-8", "surrogateescape")
            path = parts[i + 1].decode("utf-8", "surrogateescape")
            i += 2
            changed.append({"status": status[0], "path": path, "old_path": old})
        else:
            if i >= len(parts):
                break
            path = parts[i].decode("utf-8", "surrogateescape")
            i += 1
            changed.append({"status": status[:1], "path": path})
    untracked = _git(root, "ls-files", "--others", "--exclude-standard", "-z", text=False)
    if untracked.returncode == 0:
        known = {c["path"] for c in changed}
        for raw in untracked.stdout.split(b"\0"):
            if not raw:
                continue
            path = raw.decode("utf-8", "surrogateescape")
            if path not in known:
                changed.append({"status": "?", "path": path})
    return sorted(changed, key=lambda item: item["path"])


def _path_evidence(con, project_id: str, paths: list[str]) -> dict:
    result = {"symbols": set(), "dependents": set(), "tests": set(),
              "apis": set(), "db_entities": set(), "entrypoints": set(),
              "code_paths": set()}
    for path in paths:
        f = con.execute("SELECT lang,is_test,is_entry FROM files WHERE project_id=? AND path=?",
                        (project_id, path)).fetchone()
        if f and f["lang"] and not f["is_test"]:
            result["code_paths"].add(path)
        if f and f["is_entry"]:
            result["entrypoints"].add(path)
        for row in con.execute("""SELECT name FROM symbols WHERE project_id=? AND path=?
                                  ORDER BY importance DESC LIMIT 20""", (project_id, path)):
            result["symbols"].add(row["name"])
        result["dependents"].update(search.callers_of(con, project_id, path, limit=50))
        result["dependents"].update(search.importers_of(con, project_id, path, limit=50))
        for row in search.tests_for_paths(con, project_id, [path], limit=30):
            result["tests"].add(row["path"])
        for row in search.apis_for_path(con, project_id, path, limit=20):
            result["apis"].add(f"{row['method']} {row['route']}")
        for row in search.db_entities_for_file(con, project_id, path):
            result["db_entities"].add(f"{row['kind']} {row['name']}")
    return result


def _merge_evidence(left: dict, right: dict) -> dict:
    return {key: set(left.get(key, set())) | set(right.get(key, set()))
            for key in set(left) | set(right)}


def preflight(con, project_id: str, base: str = "HEAD",
              refresh: str = "auto") -> dict:
    """Map the current git diff to dependents, surfaces, risk, and tests."""
    project = con.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if not project:
        return {"error": f"unknown project {project_id!r}"}
    root = code_root(project)
    base_sha = _validate_base(root, base)
    changed = _changed_files(root, base)
    paths = [item["path"] for item in changed]
    old_paths = [item.get("old_path", item["path"]) for item in changed]
    before = _path_evidence(con, project_id, old_paths)
    sync = refresh_project(con, project_id, mode=refresh)
    after = _path_evidence(con, project_id, paths)
    evidence = _merge_evidence(before, after)

    code_paths = evidence["code_paths"]
    deleted_code = [item["path"] for item in changed
                    if item["status"] == "D" and item.get("old_path", item["path"]) in code_paths]
    changed_areas = sorted({_area(path) for path in paths})
    reasons: list[str] = []
    risk = "low"
    if deleted_code:
        risk = "high"
        reasons.append(f"deletes {len(deleted_code)} indexed code file(s)")
    if evidence["db_entities"]:
        risk = "high"
        reasons.append("touches persisted data definitions")
    if len(evidence["dependents"]) > 15 or len(code_paths) >= 20:
        risk = "high"
        reasons.append("large dependency or file blast radius")
    elif evidence["apis"] or evidence["entrypoints"] or len(evidence["dependents"]) > 5:
        if risk == "low":
            risk = "medium"
        reasons.append("touches a public/entry surface or several dependents")
    if code_paths and not evidence["tests"]:
        if risk == "low":
            risk = "medium"
        reasons.append("no mapped tests cover changed code")
    if not changed:
        reasons.append("no changes found against the selected base")
    if sync.get("status") in {"failed", "unstable"}:
        if risk == "low":
            risk = "medium"
        reasons.append("index freshness could not be proven")

    return {
        "project": project_id,
        "base": base,
        "base_sha": base_sha[:12],
        "index_sync": sync,
        "risk": risk,
        "reasons": reasons,
        "changed_files": changed,
        "changed_areas": changed_areas,
        "affected_symbols": sorted(evidence["symbols"])[:40],
        "direct_dependents": sorted(evidence["dependents"])[:60],
        "api_surface": sorted(evidence["apis"]),
        "data_surface": sorted(evidence["db_entities"]),
        "entrypoints": sorted(evidence["entrypoints"]),
        "recommended_tests": sorted(evidence["tests"]),
        "test_mapping": ("mapped" if evidence["tests"] else
                         "missing" if code_paths else "not-applicable"),
        "confidence": "reduced" if sync.get("status") in {"failed", "unstable"} else "indexed-evidence",
    }


def format_architecture(result: dict) -> str:
    if "error" in result:
        return f"ERROR: {result['error']}"
    summary = result["summary"]
    lines = [f"ARCHITECTURE: {result['project']}",
             f"PATH: {result['path']}",
             f"INDEX: {result['index_sync'].get('status', 'unknown')}",
             (f"SCALE: {summary['files']} files | {summary['symbols']} symbols | "
              f"{summary['loc']} LOC | {summary.get('tests', 0)} tests"),
             "LANGUAGES: " + ", ".join(
                 f"{x['language']} {x['loc']} LOC" for x in result["languages"][:8])]
    if result["areas"]:
        lines += ["", "AREAS:"] + [f"  {a['area']}: {a['files']} files, {a['loc']} LOC, {a['tests']} tests"
                                    for a in result["areas"][:12]]
    if result["entrypoints"]:
        lines += ["", "ENTRYPOINTS:"] + [f"  {p}" for p in result["entrypoints"]]
    if result["boundaries"]:
        lines += ["", "STRONGEST BOUNDARIES:"] + [
            f"  {b['from']} -> {b['to']} ({b['references']} refs)" for b in result["boundaries"][:10]]
    if result["hotspots"]:
        lines += ["", "DEPENDENCY HOTSPOTS:"] + [
            f"  {h['path']} ({h['inbound']} inbound)" for h in result["hotspots"][:10]]
    if result["api_surface"]:
        lines += ["", "API SURFACE:"] + [
            f"  {a['method']} {a['route']} -> {a['handler_path']}" for a in result["api_surface"][:15]]
    if result["data_surface"]:
        lines += ["", "DATA SURFACE:"] + [
            f"  {d['kind']} {d['name']} -> {d['file_path']}" for d in result["data_surface"][:15]]
    if result["warnings"]:
        lines += ["", "WARNINGS:"] + [f"  {w}" for w in result["warnings"]]
    return "\n".join(lines)


def format_preflight(result: dict) -> str:
    if "error" in result:
        return f"ERROR: {result['error']}"
    lines = [f"PREFLIGHT: {result['project']} vs {result['base']} ({result['base_sha']})",
             f"RISK: {result['risk'].upper()} | INDEX: {result['index_sync'].get('status', 'unknown')} | CONFIDENCE: {result['confidence']}"]
    lines += [f"  - {reason}" for reason in result["reasons"]]
    if result["changed_files"]:
        lines += ["", "CHANGED FILES:"] + [
            f"  {item['status']} {item['path']}" +
            (f" (from {item['old_path']})" if item.get("old_path") else "")
            for item in result["changed_files"]]
    for title, key in (("DIRECT DEPENDENTS", "direct_dependents"),
                       ("API SURFACE", "api_surface"), ("DATA SURFACE", "data_surface"),
                       ("RUN TESTS", "recommended_tests")):
        if result[key]:
            lines += ["", f"{title}:"] + [f"  {item}" for item in result[key]]
    if result["test_mapping"] == "missing":
        lines += ["", "TEST GAP: changed code has no mapped test coverage."]
    return "\n".join(lines)
