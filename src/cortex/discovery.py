"""Project discovery under configured root directories."""
from __future__ import annotations
import json, os, pathlib, subprocess, sys, tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cortex.langs import is_code, ignored_dir
from cortex.db import cortex_home  # noqa: F401  re-exported; canonical home lives in db


def load_config() -> dict:
    cfg_path = cortex_home() / "config.json"
    cfg: dict = {}
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text())
        except Exception:
            cfg = {}
    roots = os.environ.get("CORTEX_ROOTS")
    if roots:
        cfg["roots"] = [r for r in (r.strip() for r in roots.split(":")) if r]
    cfg.setdefault("roots", [])
    return cfg


def save_config(cfg: dict):
    home = cortex_home()
    home.mkdir(parents=True, exist_ok=True)
    target = home / "config.json"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=home,
                                     prefix=".config.", suffix=".tmp", delete=False) as f:
        pending = pathlib.Path(f.name)
        f.write(json.dumps(cfg, indent=1) + "\n")
        f.flush()
        os.fsync(f.fileno())
    try:
        os.replace(pending, target)
    finally:
        pending.unlink(missing_ok=True)


EXCLUDED: set[str] = set()  # per-install exclusions come from config.json

KNOWN_META = {  # slug -> delegate report metadata override (kind hints)
}


def git(root: pathlib.Path, *args) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=30)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def scan_file_tree(root: pathlib.Path) -> list[str]:
    out = []
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            for e in d.iterdir():
                if e.is_dir():
                    if not ignored_dir(e.name):
                        stack.append(e)
                elif is_code(str(e)):
                    out.append(str(e.relative_to(root)))
        except PermissionError:
            continue
    return sorted(out)


def detect_manifests(root: pathlib.Path) -> dict:
    info = {"languages": set(), "frameworks": set(), "package_managers": set(),
            "test_frameworks": set(), "kind": "app"}
    for f in ["package.json", "pnpm-workspace.yaml", "turbo.json"]:
        if (root / f).exists():
            info["package_managers"].add("pnpm" if "pnpm" in f else "npm/turbo")
    if (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
        info["package_managers"].add("pip")
    if (root / "go.mod").exists():
        info["package_managers"].add("go")
    workspaces = list(root.glob("apps/*/package.json")) + list(root.glob("packages/*/package.json"))
    if workspaces:
        info["kind"] = "monorepo"
    # the root manifest counts too — a single-package repo has no apps/ or packages/
    for ws in workspaces + [root / "package.json"]:
        if not ws.exists():
            continue
        try:
            pkg = json.loads(ws.read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        except Exception:
            deps = {}
        for fw, tag in [("next", "next"), ("fastify", "fastify"), ("express", "express"),
                        ("react", "react"), ("vue", "vue"), ("drizzle-orm", "drizzle"),
                        ("@prisma/client", "prisma"), ("pg-boss", "pg-boss"),
                        ("@nestjs/core", "nestjs"), ("hono", "hono")]:
            if fw in deps:
                info["frameworks"].add(tag)
    return info


def discover_projects(root: pathlib.Path | None = None) -> list[dict]:
    cfg = load_config()
    excluded = set(cfg.get("excluded", []))
    roots = [pathlib.Path(root).expanduser()] if root else \
        [pathlib.Path(r).expanduser() for r in cfg["roots"]]
    projects = []
    for r in roots:
        if not r.is_dir():
            continue
        projects.extend(_discover_in(r, excluded))
    return projects


def _describe(d: pathlib.Path, target: pathlib.Path) -> dict:
    """Build the project descriptor for a directory + its repo dir."""
    slug = d.name.lower().replace(" ", "-")
    files = scan_file_tree(target)
    langs: dict[str, int] = {}
    for f in files:
        ext = pathlib.Path(f).suffix.lstrip(".") or "noext"
        langs[ext] = langs.get(ext, 0) + 1
    top_langs = ",".join(l for l, _ in sorted(langs.items(), key=lambda kv: -kv[1])[:4])
    meta = detect_manifests(target)
    head = git(target, "rev-parse", "HEAD")
    return {
        "id": slug,
        "name": d.name,
        "path": str(d),
        "repo_path": str(target),
        "git_head": head,
        "top_exts": top_langs,
        "file_count": len(files),
        **{k: (",".join(sorted(v)) if isinstance(v, set) else v) for k, v in meta.items()},
    }


def _discover_in(root: pathlib.Path, excluded: set[str]) -> list[dict]:
    # A root may itself be a single repo (cortex init ~/code/myapp).
    if (root / ".git").exists() or (root / "package.json").exists() or \
            any(root.glob("*.toml")):
        return [_describe(root, root)]
    projects = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name in excluded or d.name in EXCLUDED or ignored_dir(d.name):
            continue
        # Nested repo case: select a single manifest-bearing child, not the
        # first directory returned by the filesystem (which may be docs/cache).
        target = d
        if not (d / ".git").exists() and not any(d.glob("*.toml")) and not any(d.glob("package.json")):
            subdirs = sorted(s for s in d.iterdir()
                             if s.is_dir() and not s.name.startswith("."))
            candidates = [s for s in subdirs if (s / ".git").exists()
                          or (s / "package.json").exists() or (s / "go.mod").exists()
                          or any(s.glob("*.toml"))]
            if len(candidates) == 1:
                target = candidates[0]
        proj = _describe(d, target)
        if proj["file_count"] < 3:
            continue
        projects.append(proj)
    return projects


if __name__ == "__main__":
    cfg = load_config()
    if not cfg["roots"]:
        print(f"no roots configured — add one:  cortex init <path>   "
              f"(or set CORTEX_ROOTS, config at {cortex_home() / 'config.json'})")
        sys.exit(0)
    for p in discover_projects():
        print(f"{p['id']:18} files={p['file_count']:5} git={bool(p['git_head'])} kind={p['kind']:8} langs={p['top_exts']}")
