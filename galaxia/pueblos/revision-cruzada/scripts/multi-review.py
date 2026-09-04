#!/usr/bin/env python3
"""
multi-review.py — Cross-family LLM code review
Calls 3 different model families in parallel and synthesises a verdict.

Models (all free via OpenRouter):
  Google   → google/gemma-4-31b-it:free          (262k ctx)
  NVIDIA   → nvidia/nemotron-3-super-120b-a12b:free (262k ctx, 120B params)
  Poolside → poolside/laguna-m.1:free             (131k ctx, code-specialist)

Usage:
  python scripts/multi-review.py                        # reviews git diff HEAD
  python scripts/multi-review.py --context "auth refactor"
  python scripts/multi-review.py --diff-file patch.diff
  python scripts/multi-review.py --last-commit          # reviews HEAD~1..HEAD

Exit codes:
  0  All families agree → safe to merge
  1  Disagreement or partial → review findings
  2  Critical issues found → do not merge
  3  Setup error (missing keys, no diff, API down)
"""

import asyncio
import json
import os
import subprocess
import io
import sys
import textwrap
import time
from pathlib import Path
from typing import Optional

# Windows terminals default to cp1252 — force UTF-8 for emoji output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Run: pip install httpx")
    sys.exit(3)

# ── Config ──────────────────────────────────────────────────────────────────

def load_env() -> dict:
    """Load API keys from env vars or workspace .env file."""
    env = {}
    env_paths = [
        Path.home() / ".config" / "multi-review" / ".env",
        Path(__file__).parent.parent / ".env",
    ]
    for path in env_paths:
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip()
            break

    if os.environ.get("OPENROUTER_API_KEY"):
        env["OPENROUTER_API_KEY"] = os.environ["OPENROUTER_API_KEY"]

    return env

OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"

REVIEWERS = [
    {
        "id": "gemini",
        "label": "Gemini 2.0 Flash",
        "family": "Google",
        "color": "\033[94m",   # blue
        "via": "cli",          # uses `gemini` CLI subprocess (OAuth quota)
    },
    {
        "id": "nemotron",
        "label": "NVIDIA Nemotron 120B",
        "family": "NVIDIA",
        "color": "\033[92m",   # green
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
    },
    {
        "id": "poolside",
        "label": "Poolside Laguna M.1",
        "family": "Poolside",
        "color": "\033[95m",   # magenta
        "model": "poolside/laguna-m.1:free",
    },
]

MAX_DIFF_CHARS = 12_000  # ~3k tokens — keeps cost zero on free tier

# ── Colours ─────────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
DIM    = "\033[2m"

def c(color: str, text: str) -> str:
    return f"{color}{text}{RESET}"

# ── Diff helpers ─────────────────────────────────────────────────────────────

def get_diff(diff_file: Optional[str], last_commit: bool) -> str:
    if diff_file:
        return Path(diff_file).read_text(encoding="utf-8")

    try:
        if last_commit:
            result = subprocess.run(
                ["git", "diff", "HEAD~1", "HEAD"],
                capture_output=True, text=True, cwd=Path(__file__).parent.parent
            )
        else:
            result = subprocess.run(
                ["git", "diff", "HEAD"],
                capture_output=True, text=True, cwd=Path(__file__).parent.parent
            )
            if not result.stdout.strip():
                result = subprocess.run(
                    ["git", "diff", "--cached"],
                    capture_output=True, text=True, cwd=Path(__file__).parent.parent
                )
        return result.stdout
    except Exception:
        return ""

# ── Review prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""
You are a senior software engineer doing a focused code review.
Be direct. Look for real problems, not style preferences.

Respond ONLY with this exact XML structure (no prose before or after):

<review>
  <verdict>agree|partial|disagree</verdict>
  <confidence>high|medium|low</confidence>
  <summary>One concise paragraph: what this change does and your overall take.</summary>
  <findings>
    <!-- List only real issues. Leave empty if none. -->
    <finding severity="critical|high|medium|low">
      <location>file:line or component name</location>
      <issue>What is wrong</issue>
      <fix>Concrete fix suggestion</fix>
    </finding>
  </findings>
</review>

Verdict rules:
- agree: change is correct, safe to merge
- partial: merge ok but address medium findings first
- disagree: critical/high issues — do not merge
""").strip()

AUDIT_SYSTEM_PROMPT = textwrap.dedent("""
You are a senior frontend design engineer auditing a React codebase for visual and UX quality.
Focus on what makes the UI look generic, AI-generated, or low-effort. Be specific and brutal.

Design system rules for THIS project (edit this block to match your own conventions before running):
- Typography: <your body typeface> + <your code/label typeface>. No system-default fonts if your
  project requires a distinct look.
- Colors: <your convention — CSS variables, design tokens, tailwind config>. No stray hardcoded
  values if your project forbids them.
- Theme: <your theming mechanism, if any>.
- Spacing/layout: <your scale>.
- Motion: <your animation library/convention>.
- Components: <your composition rules>.

Anti-patterns to flag as critical/high (generic defaults — keep or adjust):
- Hardcoded colors instead of your design tokens
- Utility classes that bypass your design system
- rounded-full on rectangular cards
- shadow-lg everywhere (overused depth)
- Generic empty states ("No data available")
- Lorem ipsum or placeholder copy
- Icon-only buttons without aria-label
- Missing loading/error states
- Duplicate motion boilerplate copy-pasted across components

Respond ONLY with this exact XML structure:

<review>
  <verdict>agree|partial|disagree</verdict>
  <confidence>high|medium|low</confidence>
  <summary>One paragraph: overall visual quality assessment and main problems.</summary>
  <findings>
    <finding severity="critical|high|medium|low">
      <location>file:line or component name</location>
      <issue>What looks generic, broken, or wrong</issue>
      <fix>Concrete fix — specific class, CSS var, or code snippet</fix>
    </finding>
  </findings>
</review>

Verdict:
- agree: UI is polished, design-system-compliant, no AI-generic patterns
- partial: mostly ok but specific components need fixes
- disagree: significant visual debt, generic AI look, design system violations
""").strip()


def collect_frontend_files(audit_path: str, max_chars: int = 18_000) -> str:
    """Read .jsx/.tsx/.css files from path, concatenate up to max_chars."""
    root = Path(audit_path)
    extensions = {".jsx", ".tsx", ".js", ".ts", ".css", ".scss"}
    skip_dirs = {"node_modules", ".git", "dist", "build", "__pycache__"}

    files = []
    for f in sorted(root.rglob("*")):
        if f.is_file() and f.suffix in extensions:
            if not any(p in f.parts for p in skip_dirs):
                files.append(f)

    # Prioritise: components > views > hooks > rest
    def priority(p: Path) -> int:
        s = str(p).lower()
        if "component" in s: return 0
        if "view" in s or "page" in s or "screen" in s: return 1
        if "hook" in s: return 2
        return 3

    files.sort(key=priority)

    chunks = []
    total = 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
            header = f"// ── {f.name} ({'─'*40}\n"
            block = header + text + "\n"
            if total + len(block) > max_chars:
                remaining = max_chars - total
                if remaining > 200:
                    chunks.append(block[:remaining] + "\n// [truncated]\n")
                break
            chunks.append(block)
            total += len(block)
        except Exception:
            continue

    return "".join(chunks)


def build_user_prompt(diff: str, context: str) -> str:
    diff_trimmed = diff[:MAX_DIFF_CHARS]
    if len(diff) > MAX_DIFF_CHARS:
        diff_trimmed += f"\n\n[diff truncated — {len(diff) - MAX_DIFF_CHARS} chars omitted]"

    parts = []
    if context:
        parts.append(f"## Task context\n{context}")
    parts.append(f"## Code diff\n```diff\n{diff_trimmed}\n```")
    return "\n\n".join(parts)


def build_audit_prompt(code: str, context: str) -> str:
    parts = []
    if context:
        parts.append(f"## Audit scope\n{context}")
    parts.append(f"## Source files\n```jsx\n{code}\n```")
    return "\n\n".join(parts)

# ── API caller ────────────────────────────────────────────────────────────────

async def call_openrouter(client: httpx.AsyncClient, model: str, api_key: str,
                           user_prompt: str, system_prompt: str = SYSTEM_PROMPT) -> dict:
    for attempt in range(2):
        try:
            resp = await client.post(
                OPENROUTER_BASE,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://github.com/",
                    "X-Title": "Multi-Review",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_prompt},
                    ],
                    "max_tokens": 1600,
                    "temperature": 0.2,
                },
                timeout=60.0,
            )
            if resp.status_code == 429 and attempt == 0:
                await asyncio.sleep(5)
                continue
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            return {"ok": True, "text": text}
        except Exception as e:
            if attempt == 1:
                return {"ok": False, "error": str(e)}
            await asyncio.sleep(3)
    return {"ok": False, "error": "max retries exceeded"}


_GEMINI_JS = (
    Path.home() / "AppData" / "Roaming" / "npm" / "node_modules"
    / "@google" / "gemini-cli" / "bundle" / "gemini.js"
)

def _run_gemini_cli_sync(full_prompt: str) -> dict:
    """Blocking subprocess — calls node directly to bypass cmd.exe arg limits."""
    import shutil, subprocess as _sp

    node = shutil.which("node")
    if not node:
        return {"ok": False, "error": "node not in PATH"}
    if not _GEMINI_JS.exists():
        return {"ok": False, "error": f"gemini.js not found at {_GEMINI_JS}"}

    import tempfile, os
    tmp_dir = tempfile.gettempdir()  # neutral cwd — no project scanning

    try:
        result = _sp.run(
            [node, str(_GEMINI_JS), "-p", full_prompt],
            stdin=_sp.DEVNULL,
            capture_output=True,
            timeout=90,
            encoding=None,
            cwd=tmp_dir,
        )
        text = result.stdout.decode("utf-8", errors="replace").strip()
        if not text:
            err = result.stderr.decode("utf-8", errors="replace").strip()
            return {"ok": False, "error": err[:300] or "empty response"}
        return {"ok": True, "text": text}
    except _sp.TimeoutExpired:
        return {"ok": False, "error": "gemini timed out (90s)"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def call_gemini_cli(user_prompt: str, system_prompt: str = SYSTEM_PROMPT) -> dict:
    """Async wrapper — asyncio.to_thread avoids ProactorEventLoop pipe issues on Windows."""
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    return await asyncio.to_thread(_run_gemini_cli_sync, full_prompt)


# ── XML parser ────────────────────────────────────────────────────────────────

import re

def parse_review(text: str) -> dict:
    """Extract verdict, confidence, summary, findings from XML response."""
    def tag(name: str) -> str:
        m = re.search(rf"<{name}>(.*?)</{name}>", text, re.DOTALL)
        return m.group(1).strip() if m else ""

    verdict    = tag("verdict").lower()
    confidence = tag("confidence").lower()
    summary    = tag("summary")

    findings = []
    for m in re.finditer(
        r'<finding severity="([^"]+)">(.*?)</finding>', text, re.DOTALL
    ):
        severity = m.group(1)
        block = m.group(2)
        loc   = re.search(r"<location>(.*?)</location>", block, re.DOTALL)
        issue = re.search(r"<issue>(.*?)</issue>", block, re.DOTALL)
        fix   = re.search(r"<fix>(.*?)</fix>", block, re.DOTALL)
        findings.append({
            "severity": severity,
            "location": loc.group(1).strip() if loc else "",
            "issue":    issue.group(1).strip() if issue else "",
            "fix":      fix.group(1).strip() if fix else "",
        })

    if verdict not in ("agree", "partial", "disagree"):
        verdict = "partial"

    return {
        "verdict": verdict,
        "confidence": confidence,
        "summary": summary,
        "findings": findings,
        "raw": text,
    }

# ── Display ───────────────────────────────────────────────────────────────────

SEVERITY_COLOR = {
    "critical": RED + BOLD,
    "high":     RED,
    "medium":   YELLOW,
    "low":      DIM,
}

VERDICT_COLOR = {
    "agree":    GREEN,
    "partial":  YELLOW,
    "disagree": RED,
}

VERDICT_ICON = {
    "agree":    "✅",
    "partial":  "⚠️ ",
    "disagree": "🛑",
}

def print_reviewer(reviewer: dict, result: dict, review: dict):
    col = reviewer["color"]
    print(f"\n{col}{BOLD}{'─'*60}{RESET}")
    print(f"{col}{BOLD}  {reviewer['label']} ({reviewer['family']}){RESET}")
    print(f"{col}{'─'*60}{RESET}")

    if not result["ok"]:
        print(f"  {RED}ERROR: {result['error']}{RESET}")
        return

    vc = VERDICT_COLOR.get(review["verdict"], "")
    vi = VERDICT_ICON.get(review["verdict"], "")
    print(f"  Verdict:    {vc}{BOLD}{vi} {review['verdict'].upper()}{RESET}  "
          f"{DIM}({review['confidence']} confidence){RESET}")

    if review["summary"]:
        wrapped = textwrap.fill(review["summary"], width=70,
                                initial_indent="  ", subsequent_indent="  ")
        print(f"\n{wrapped}")

    if review["findings"]:
        print(f"\n  {BOLD}Findings:{RESET}")
        for f in review["findings"]:
            sc = SEVERITY_COLOR.get(f["severity"], "")
            print(f"  {sc}[{f['severity'].upper()}]{RESET} {f['location']}")
            print(f"    {f['issue']}")
            if f["fix"]:
                print(f"    {DIM}→ {f['fix']}{RESET}")
    else:
        print(f"\n  {DIM}No findings.{RESET}")


def print_synthesis(results: list[dict], reviews: list[dict], elapsed: float):
    verdicts = [r["verdict"] for r in reviews if r.get("verdict")]
    has_critical = any(
        f["severity"] in ("critical", "high")
        for r in reviews for f in r.get("findings", [])
    )

    agree_count    = sum(1 for v in verdicts if v == "agree")
    disagree_count = sum(1 for v in verdicts if v == "disagree")

    if disagree_count > 0 or has_critical:
        exit_code = 2
        icon = "🛑"
        label = "DO NOT MERGE — critical issues"
        col = RED
    elif agree_count == len(verdicts):
        exit_code = 0
        icon = "✅"
        label = "CONSENSUS — safe to merge"
        col = GREEN
    else:
        exit_code = 1
        icon = "⚠️ "
        label = "PARTIAL — address findings first"
        col = YELLOW

    ok_count = len([r for r in results if r["ok"]])
    print(f"\n{'═'*62}")
    print(f"  {col}{BOLD}{icon}  {label}{RESET}")
    print(f"  {DIM}({elapsed:.1f}s · {ok_count} of {len(results)} reviewers responded){RESET}")
    print(f"{'═'*62}\n")
    return exit_code

# ── Main ──────────────────────────────────────────────────────────────────────

async def run(context: str, diff_file: Optional[str], last_commit: bool,
              audit_path: Optional[str] = None):
    env = load_env()
    openrouter_key = env.get("OPENROUTER_API_KEY", "")

    if not openrouter_key:
        print(f"{RED}OPENROUTER_API_KEY not set. Add it to ~/.config/multi-review/.env{RESET}")
        sys.exit(3)

    if audit_path:
        code = collect_frontend_files(audit_path)
        if not code.strip():
            print(f"{YELLOW}No frontend files found in {audit_path}{RESET}")
            sys.exit(3)
        user_prompt = build_audit_prompt(code, context)
        active_system = AUDIT_SYSTEM_PROMPT
        mode_label = f"Frontend Audit — {audit_path}"
        size_info = f"code: {len(code):,} chars"
    else:
        diff = get_diff(diff_file, last_commit)
        if not diff.strip():
            print(f"{YELLOW}No diff found. Stage changes or use --last-commit.{RESET}")
            sys.exit(3)
        user_prompt = build_user_prompt(diff, context)
        active_system = SYSTEM_PROMPT
        mode_label = "Code Review"
        size_info = f"diff: {len(diff):,} chars"

    print(f"\n{BOLD}🔍 Multi-LLM {mode_label}{RESET}  {DIM}(3 families in parallel){RESET}")
    print(f"{DIM}  {size_info} · context: {context or '(none)'}{RESET}")
    print(f"  Reviewers: {', '.join(r['label'] for r in REVIEWERS)}")
    print(f"  {DIM}Waiting...{RESET}", end="", flush=True)
    t0 = time.monotonic()

    async with httpx.AsyncClient() as client:
        coros = []
        for rv in REVIEWERS:
            if rv.get("via") == "cli":
                coros.append(call_gemini_cli(user_prompt, active_system))
            else:
                coros.append(call_openrouter(client, rv["model"], openrouter_key,
                                             user_prompt, active_system))
        raw_results = await asyncio.gather(*coros)

    elapsed = time.monotonic() - t0
    print(f"\r  Done in {elapsed:.1f}s                    ")

    reviews = []
    for rv, result in zip(REVIEWERS, raw_results):
        review = parse_review(result["text"]) if result["ok"] else {
            "verdict": "partial", "confidence": "low",
            "summary": f"Error: {result.get('error', 'unknown')}",
            "findings": [], "raw": ""
        }
        reviews.append(review)
        print_reviewer(rv, result, review)

    exit_code = print_synthesis(raw_results, reviews, elapsed)

    summary_json = {
        "exit_code": exit_code,
        "reviewers": [
            {"id": rv["id"], "family": rv["family"], "verdict": r["verdict"],
             "findings_count": len(r["findings"]),
             "has_critical": any(f["severity"] in ("critical", "high")
                                 for f in r["findings"])}
            for rv, r in zip(REVIEWERS, reviews)
        ]
    }
    print(json.dumps(summary_json), file=sys.stderr)
    sys.exit(exit_code)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="multi-LLM code review")
    p.add_argument("--context",     default="", help="Task description / what changed")
    p.add_argument("--diff-file",   default=None, help="Path to diff file (instead of git)")
    p.add_argument("--last-commit", action="store_true", help="Review HEAD~1..HEAD")
    p.add_argument("--audit-path",  default=None,
                   help="Frontend audit: path to src dir (e.g. src/mi-proyecto/frontend/src)")
    args = p.parse_args()

    asyncio.run(run(args.context, args.diff_file, args.last_commit, args.audit_path))
