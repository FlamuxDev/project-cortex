"""Language detection, ignore rules, secret redaction."""
import re

IGNORE_DIRS = {
    "node_modules", "dist", "build", ".next", "coverage", ".venv", "venv", "target",
    "vendor", ".cache", ".git", "__pycache__", ".turbo", ".output", ".nuxt", ".svelte-kit",
    "out", ".vercel", ".netlify", "storybook-static", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "htmlcov", ".idea", ".vscode", "generated", "_generated", "pb_migrations",
    "supabase/functions/node_modules", ".wrangler", "playwright-report", "test-results",
}

LANG_BY_EXT = {
    ".ts": "ts", ".tsx": "tsx", ".js": "js", ".jsx": "jsx", ".mjs": "js", ".cjs": "js",
    ".py": "py", ".go": "go", ".sql": "sql", ".prisma": "prisma", ".rs": "rust",
    ".java": "java", ".sh": "shell", ".yaml": "yaml", ".yml": "yaml", ".json": "json",
    ".md": "md", ".toml": "toml",
}
CODE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go", ".sql", ".prisma"}

TEST_PAT = re.compile(r"(^|[/\\])(tests?|__tests__|e2e|spec)([/\\])|[._-]?(test|spec)\.[jtsp]x?$|_test\.go$|\.test\.[tj]sx?$")

# Secrets: never store these. Redact before any text enters the DB.
SECRET_PATTERNS = [
    (re.compile(r"(sk-[A-Za-z0-9]{20,})"), "sk-***REDACTED***"),
    (re.compile(r"(AKIA[0-9A-Z]{16})"), "***REDACTED-AWS-KEY***"),
    (re.compile(r"(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})"), "***REDACTED-GH-TOKEN***"),
    (re.compile(r"(eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})"), "***REDACTED-JWT***"),
    (re.compile(r"(-----BEGIN [A-Z ]*PRIVATE KEY-----)[\s\S]*?(-----END [A-Z ]*PRIVATE KEY-----)"), r"\1***REDACTED***\2"),
    (re.compile(r"\b(password|passwd|secret|api[_-]?key|token|access[_-]?key)\b\s*[:=]\s*['\"]([^'\"]{6,})['\"]", re.I),
     r"\1=***REDACTED***"),
    # unquoted password=hunter22 style
    (re.compile(r"\b(password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token)\s*[:=]\s*([^\s'\"]{6,})", re.I),
     r"\1=***REDACTED***"),
    # creds in URIs: scheme://user:pass@host
    (re.compile(r"\b[a-z][a-z0-9+.-]*://([^:/\s@]{1,64}):([^@\s/]{3,})@", re.I),
     r"***REDACTED-CREDS***@"),
    (re.compile(r"([A-Za-z0-9+/]{40,}={0,2})"), lambda m: "***REDACTED-B64***" if len(m.group(1)) > 60 else m.group(1)),
]


def redact(text: str) -> str:
    if not text:
        return text
    for pat, repl in SECRET_PATTERNS:
        text = pat.sub(repl, text)
    return text


def lang_of(path: str) -> str | None:
    for ext, lang in LANG_BY_EXT.items():
        if path.endswith(ext):
            return lang
    return None


def is_code(path: str) -> bool:
    return f".{lang_of(path)}" in CODE_EXTS


def is_test(path: str) -> bool:
    return bool(TEST_PAT.search(path))


def ignored_dir(name: str) -> bool:
    return name in IGNORE_DIRS or name.startswith(".") and name not in {".github", ".vscode-extensions"}


IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_$]{3,}")
GENERIC_TERMS = {"const","function","return","export","import","default","string","number",
                 "boolean","interface","type","class","async","await","value","params","props",
                 "error","throw","catch","finally","super","this","self","null","true","false",
                 "static","public","private","readonly","extends","implements","require",
                 "module","undefined","object","promise","result","data","item","items"}


def content_terms(text: str, cap: int = 400) -> str:
    """Distinct identifiers in a source file, for lexical retrieval over code bodies."""
    seen: dict[str, None] = {}
    for m in IDENT_RE.findall(text):
        w = m.lower()
        if w not in GENERIC_TERMS and w not in seen:
            seen[w] = None
            if len(seen) >= cap:
                break
    return " ".join(seen)
