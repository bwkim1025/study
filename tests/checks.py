#!/usr/bin/env python3
"""Dependency-free structural checks for the study repo. App code is not modified."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KST = timezone(timedelta(hours=9))
ANCHOR = date(2026, 5, 9)
BRIEFING_PAT = re.compile(r"^(\d{4}-\d{2}-\d{2})-day([123])\.md$")

# Hard expectations (parser = 2nd <script> in index.html; v3 = 3rd)
PARSER_BYTES, PARSER_SHA1 = 27986, "ae5404ec"
V3_BYTES, V3_SHA1 = 21235, "719157d2"
MANIFEST_START_URL = "./"
MANIFEST_SCOPE = "./"

PASS = 0
FAIL = 0
WARN = 0


def ok(msg: str) -> None:
    global PASS
    PASS += 1
    print(f"OK   {msg}")


def bad(msg: str) -> None:
    global FAIL
    FAIL += 1
    print(f"FAIL {msg}")


def warn(msg: str) -> None:
    global WARN
    WARN += 1
    print(f"WARN {msg}")


def check_inline_scripts() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    scripts = re.findall(r"<script\b([^>]*)>(.*?)</script>", html, flags=re.I | re.S)
    inline: list[tuple[int, str]] = []
    for attrs, body in scripts:
        if re.search(r"\bsrc\s*=", attrs, flags=re.I):
            continue
        raw = body.encode("utf-8")
        inline.append((len(raw), hashlib.sha1(raw).hexdigest()[:8]))

    if len(inline) < 2:
        bad(f"index.html inline scripts < 2 (got {len(inline)})")
        return

    got_b, got_s = inline[0]
    if got_b == PARSER_BYTES and got_s == PARSER_SHA1:
        ok(f"parser script (2nd <script>): {got_b}B sha1={got_s}")
    else:
        bad(
            f"parser script (2nd <script>): got {got_b}B sha1={got_s}, "
            f"want {PARSER_BYTES}B sha1={PARSER_SHA1}"
        )

    got_b, got_s = inline[1]
    if got_b == V3_BYTES and got_s == V3_SHA1:
        ok(f"v3 script (3rd <script>): {got_b}B sha1={got_s}")
    else:
        bad(
            f"v3 script (3rd <script>): got {got_b}B sha1={got_s}, "
            f"want {V3_BYTES}B sha1={V3_SHA1}"
        )


def check_manifest() -> None:
    data = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    start = data.get("start_url")
    scope = data.get("scope")
    if start == MANIFEST_START_URL:
        ok(f"manifest.start_url={start!r}")
    else:
        bad(f"manifest.start_url={start!r} want {MANIFEST_START_URL!r}")
    if scope == MANIFEST_SCOPE:
        ok(f"manifest.scope={scope!r}")
    else:
        bad(f"manifest.scope={scope!r} want {MANIFEST_SCOPE!r}")


def check_sw() -> None:
    sw_path = ROOT / "sw.js"
    text = sw_path.read_text(encoding="utf-8")
    if re.search(r"\bCACHE_VERSION\b", text):
        m = re.search(r"CACHE_VERSION\s*=\s*`[^`]*v(\d+)`|CACHE_VERSION\s*=\s*['\"][^'\"]*v(\d+)", text)
        ver = (m.group(1) or m.group(2)) if m else "?"
        ok(f"sw.js CACHE_VERSION present (v{ver})")
    else:
        bad("sw.js CACHE_VERSION missing")

    # Collect string literals that look like app-shell / precache file paths
    literals = re.findall(r"['\"]([^'\"]+)['\"]", text)
    rel_files: set[str] = set()
    for lit in literals:
        path = lit.split("?", 1)[0]
        if not path or path.endswith("/"):
            continue
        if path.startswith("http://") or path.startswith("https://"):
            continue
        if any(
            path.endswith(ext)
            for ext in (
                ".html",
                ".js",
                ".css",
                ".json",
                ".png",
                ".svg",
                ".ico",
                ".webp",
            )
        ):
            # strip leading ./
            path = path[2:] if path.startswith("./") else path
            if "/" not in path and path not in {
                "index.html",
                "manifest.json",
                "collab.html",
                "favicon.ico",
                "apple-touch-icon.png",
                "icon-192.png",
                "icon-512.png",
                "icon-512-maskable.png",
                "icon.svg",
                "icon-maskable.svg",
            }:
                # bare name without known shell file — keep if it looks like asset
                if not path.startswith("assets/"):
                    continue
            rel_files.add(path)

    # Always require APP_SHELL essentials
    required = {"index.html"}
    missing = sorted(p for p in (rel_files | required) if not (ROOT / p).exists())
    if missing:
        bad("APP_SHELL/precache paths missing: " + ", ".join(missing))
    else:
        ok(f"APP_SHELL/precache paths exist ({len(rel_files | required)} files)")


def expected_day(d: date) -> int:
    return ((d - ANCHOR).days % 3) + 1


def check_briefings() -> None:
    files = sorted((ROOT / "briefings").glob("*.md"))
    bad_names: list[str] = []
    mismatches: list[str] = []
    present: set[date] = set()

    for path in files:
        m = BRIEFING_PAT.match(path.name)
        if not m:
            bad_names.append(path.name)
            continue
        d = date.fromisoformat(m.group(1))
        day = int(m.group(2))
        present.add(d)
        exp = expected_day(d)
        if day != exp:
            mismatches.append(f"{path.name} (want day{exp})")

    if bad_names:
        bad(f"briefings name format: {len(bad_names)} bad — " + ", ".join(bad_names[:5]))
    else:
        ok(f"briefings name format YYYY-MM-DD-dayN ({len(files)} files)")

    if mismatches:
        bad(f"briefings day cycle vs 2026-05-09=Day1: {len(mismatches)} — " + ", ".join(mismatches[:5]))
    else:
        ok("briefings day cycle matches 3-day rotation")

    today = datetime.now(KST).date()
    missing: list[str] = []
    for i in range(14):
        d = today - timedelta(days=i)
        if d not in present:
            missing.append(d.isoformat())
    if missing:
        warn("last 14 days missing: " + ", ".join(missing))
    else:
        ok("last 14 days: no missing dates")


def main() -> int:
    check_inline_scripts()
    check_manifest()
    check_sw()
    check_briefings()
    print()
    print(f"summary: PASS={PASS} FAIL={FAIL} WARN={WARN}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
