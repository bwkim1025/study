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
PARSER_BYTES, PARSER_SHA1 = 29943, "ac88deac"  # 2026-11-24: review·중요도 점수 블록
V3_BYTES, V3_SHA1 = 21184, "195f1948"
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


# 2026-11-25부터: 과목당 한 항목(paper 또는 review), 중요도 점수 블록 필수 (EDITORIAL-PRINCIPLES.md §2·§4·§5·§7)
ONE_ITEM_FROM = date(2026, 11, 25)
DAY_SPECIALTIES = {
    1: ["NEPHROLOGY", "ENDOCRINOLOGY", "CARDIOLOGY"],
    2: ["INFECTIOUS", "PULMONOLOGY", "GASTROENTEROLOGY"],
    3: ["FAMILY", "RHEUMATOLOGY", "PSYCHIATRY", "GERIATRICS"],
}
REQUIRED_BLOCKS = {
    "paper": ["중요도 점수", "어떤 연구", "초록", "주요 결과", "적용 알고리즘", "한계", "출처"],
    "review": ["중요도 점수", "기전", "진단", "치료", "출처"],
}


def one_item_problems(text: str, day: int) -> list[str]:
    """새 형식(과목당 한 항목) 회차의 구조 문제 목록. 비어 있으면 통과."""
    problems: list[str] = []
    lines = text.splitlines()
    if not lines or not re.match(rf"^# \d{{4}}-\d{{2}}-\d{{2}} \(Day {day}\)\s*$", lines[0]):
        problems.append(f"첫 줄이 '# YYYY-MM-DD (Day {day})' 형식이 아님")
    sections = re.split(r"(?m)^## ", text)
    specs: list[tuple[str, str]] = []
    others: set[str] = set()
    for sec in sections[1:]:
        name, _, body = sec.partition("\n")
        name = name.strip()
        m = re.match(r"SPECIALTY[_ ](\S+)", name)
        if m:
            specs.append((m.group(1), body))
        else:
            others.add(name.split()[0] if name else "")
    got = [s for s, _ in specs]
    if got != DAY_SPECIALTIES[day]:
        problems.append(f"과목 순서 {got} ≠ Day {day} {DAY_SPECIALTIES[day]}")
    for spec, body in specs:
        items = re.split(r"(?m)^### ", body)[1:]
        if len(items) != 1:
            problems.append(f"{spec}: 항목 {len(items)}개(정확히 1개여야 함)")
            continue
        head, _, rest = items[0].partition("\n")
        m = re.match(r"(paper|review)\s*[:：]\s*(.+)", head.strip())
        if not m:
            problems.append(f"{spec}: 항목 유형이 paper/review가 아님 ({head.strip()[:40]})")
            continue
        kind, headline = m.group(1), m.group(2)
        if "신규 사항 없음" in headline:
            problems.append(f"{spec}: 빈칸 제목은 쓰지 않음")
        labels = [x.strip() for x in re.findall(r"(?m)^#### (.+)$", rest)]
        for need in REQUIRED_BLOCKS[kind]:
            if need not in labels:
                problems.append(f"{spec}: {kind}에 '#### {need}' 없음")
        sm = re.search(r"(?ms)^#### 중요도 점수\s*$(.*?)(?=^#### |\Z)", rest)
        if sm:
            block = sm.group(1)
            if "합계" not in block:
                problems.append(f"{spec}: 중요도 점수 블록에 '합계' 없음")
            if "필수조건" not in block:
                problems.append(f"{spec}: 중요도 점수 블록에 '필수조건' 줄 없음")
    for need in ("SELF_CHECK", "RECALL_CARD", "AUTHOR"):
        if need not in others:
            problems.append(f"'## {need}' 없음")
    if len(re.findall(r"(?m)^### Q\d+\.", text)) != 3:
        problems.append("SELF_CHECK 문항이 3개가 아님")
    return problems


def check_one_item_format() -> None:
    tpl = ROOT / "docs" / "BRIEFING-TEMPLATE.md"
    if not tpl.exists():
        bad("docs/BRIEFING-TEMPLATE.md missing")
    else:
        m = re.search(r"```markdown\n(.*?)\n```", tpl.read_text(encoding="utf-8"), flags=re.S)
        probs = one_item_problems(m.group(1), 3) if m else ["템플릿 코드 블록 없음"]
        if probs:
            bad("BRIEFING-TEMPLATE 형식: " + "; ".join(probs[:6]))
        else:
            ok("BRIEFING-TEMPLATE: Day 3 과목당 1항목 형식 통과")
    checked = 0
    for path in sorted((ROOT / "briefings").glob("*.md")):
        m = BRIEFING_PAT.match(path.name)
        if not m or date.fromisoformat(m.group(1)) < ONE_ITEM_FROM:
            continue
        checked += 1
        probs = one_item_problems(path.read_text(encoding="utf-8"), int(m.group(2)))
        if probs:
            bad(f"{path.name} 과목당 1항목 형식: " + "; ".join(probs[:6]))
    if checked:
        ok(f"one-item format checked on {checked} briefing(s) from {ONE_ITEM_FROM}")
    else:
        ok(f"one-item format: no briefings from {ONE_ITEM_FROM} yet (template only)")


def main() -> int:
    check_inline_scripts()
    check_manifest()
    check_sw()
    check_briefings()
    check_one_item_format()
    print()
    print(f"summary: PASS={PASS} FAIL={FAIL} WARN={WARN}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
