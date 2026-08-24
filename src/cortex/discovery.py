"""Project discovery under a root directory."""
from __future__ import annotations
import json, pathlib, subprocess, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cortex.langs import is_code, ignored_dir

DEV_ROOT = pathlib.Path("/home/aboud/Dev")
EXCLUDED = {"pems"}  # SSH keys — never index

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
    for ws in list(root.glob("apps/*/package.json")) + list(root.glob("packages/*/package.json")):
        info["kind"] = "monorepo"
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


def discover_projects(root: pathlib.Path = DEV_ROOT) -> list[dict]:
    projects = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name in EXCLUDED or ignored_dir(d.name):
            continue
        # nested repo case (FARAJ/farj-portfolio)
        target = d
        if not (d / ".git").exists() and not any(d.glob("*.toml")) and not any(d.glob("package.json")):
            subdirs = [s for s in d.iterdir() if s.is_dir() and not s.name.startswith(".")]
            if len(subdirs) >= 1:
                target = subdirs[0]
        slug = d.name.lower().replace(" ", "-")
        files = scan_file_tree(target)
        if len(files) < 3:
            continue
        langs: dict[str, int] = {}
        for f in files:
            ext = pathlib.Path(f).suffix or "noext"
            langs[ext] = langs.get(ext, 0) + 1
        top_langs = ",".join(l for l, _ in sorted(langs.items(), key=lambda kv: -kv[1])[:4])
        meta = detect_manifests(target)
        head = git(target, "rev-parse", "HEAD")
        projects.append({
            "id": slug,
            "name": d.name,
            "path": str(d),
            "repo_path": str(target),
            "git_head": head,
            "top_exts": top_langs,
            "file_count": len(files),
            **{k: (",".join(sorted(v)) if isinstance(v, set) else v) for k, v in meta.items()},
        })
    return projects


if __name__ == "__main__":
    for p in discover_projects():
        print(f"{p['id']:18} files={p['file_count']:5} git={bool(p['git_head'])} kind={p['kind']:8} langs={p['top_exts']}")
