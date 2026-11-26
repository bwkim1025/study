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


# 2026-11-25부터: 과목당 한 항목(paper 또는 review), 중요도 점수 블록 필수.
# 2026-11-26~2026-12-14 회차만 EDITORIAL-PRINCIPLES.md §3.1: 그 날짜·과목 대기열의
# 시험이고 헤드라인이 "(다시 정리)"로 끝나는 paper를 두 번째 항목으로 허용.
ONE_ITEM_FROM = date(2026, 11, 25)
REWRITE_FROM = date(2026, 11, 26)
REWRITE_UNTIL = date(2026, 12, 14)
REWRITE_MARK = "(다시 정리)"
DAY_SPECIALTIES = {
    1: ["NEPHROLOGY", "ENDOCRINOLOGY", "CARDIOLOGY"],
    2: ["INFECTIOUS", "PULMONOLOGY", "GASTROENTEROLOGY"],
    3: ["FAMILY", "RHEUMATOLOGY", "PSYCHIATRY", "GERIATRICS"],
}
REQUIRED_BLOCKS = {
    "paper": ["중요도 점수", "어떤 연구", "초록", "주요 결과", "적용 알고리즘", "한계", "출처"],
    "review": ["중요도 점수", "기전", "진단", "치료", "출처"],
}


def _trial(name: str) -> tuple[tuple[str, ...], ...]:
    """헤드라인에 시험명이 단어로 있어야 한다. FLOWPROMOTE·ALIGNMENT처럼 더 긴 이름은 제외."""
    return ((rf"(?<![A-Za-z0-9]){re.escape(name)}(?![A-Za-z0-9])",),)


# 날짜 → 과목 → 대안(대안마다 정규식 전부가 맞아야 함). §3.1 표와 같은 배정.
REWRITE_QUEUE: dict[date, dict[str, tuple[tuple[str, ...], ...]]] = {
    date(2026, 11, 26): {
        "NEPHROLOGY": _trial("EMPA-KIDNEY"),
        "ENDOCRINOLOGY": _trial("SOUL"),
        "CARDIOLOGY": _trial("FINEARTS-HF"),
    },
    date(2026, 11, 29): {
        "NEPHROLOGY": _trial("FLOW"),
        "ENDOCRINOLOGY": _trial("SURPASS-CVOT"),
        "CARDIOLOGY": _trial("STEP-HFpEF"),
    },
    date(2026, 12, 2): {
        "NEPHROLOGY": _trial("CONFIDENCE"),
        "ENDOCRINOLOGY": (
            (r"(?i)(?<![A-Za-z0-9])semaglutide(?![A-Za-z0-9])", r"투석"),
            (r"세마글루타이드|세마글루티드", r"투석"),
            (r"(?i)(?<![A-Za-z0-9])semaglutide(?![A-Za-z0-9])", r"(?i)dialysis"),
        ),
        "CARDIOLOGY": _trial("VESALIUS-CV"),
    },
    date(2026, 12, 5): {
        "NEPHROLOGY": _trial("FIND-CKD"),
        "ENDOCRINOLOGY": _trial("SURMOUNT-5"),
        "CARDIOLOGY": _trial("CHAMPION-AF"),
    },
    date(2026, 12, 8): {
        "NEPHROLOGY": (
            _trial("CONVINCE")[0],
            (r"Cochrane|코크란", r"대류"),
        ),
    },
    date(2026, 12, 11): {"NEPHROLOGY": _trial("ALIGN")},
    date(2026, 12, 14): {"NEPHROLOGY": _trial("VISIONARY")},
}


def heading_date(text: str) -> date | None:
    lines = text.splitlines()
    if not lines:
        return None
    m = re.match(r"^# (\d{4}-\d{2}-\d{2}) \(Day \d\)\s*$", lines[0])
    if not m:
        return None
    return date.fromisoformat(m.group(1))


def is_rewrite_headline(headline: str) -> bool:
    return headline.rstrip().endswith(REWRITE_MARK)


def rewrite_matches(headline: str, alts: tuple[tuple[str, ...], ...]) -> bool:
    return any(all(re.search(pat, headline) for pat in alt) for alt in alts)


def item_structure_problems(spec: str, raw: str) -> tuple[str | None, str, list[str]]:
    head, _, rest = raw.partition("\n")
    problems: list[str] = []
    m = re.match(r"(paper|review)\s*[:：]\s*(.+)", head.strip())
    if not m:
        problems.append(f"{spec}: 항목 유형이 paper/review가 아님 ({head.strip()[:40]})")
        return None, head.strip(), problems
    kind, headline = m.group(1), m.group(2).strip()
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
    return kind, headline, problems


def one_item_problems(text: str, day: int, on: date | None = None) -> list[str]:
    """새 형식 회차의 구조 문제 목록. 비어 있으면 통과.

    평상시는 과목당 1항목이다. on이 2026-11-26~2026-12-14이고 그 날짜·과목이
    §3.1 대기열에 있을 때만 두 번째 paper를 허용한다. 그 헤드라인은
    '(다시 정리)'로 끝나고 그 대기열 시험명이 있어야 한다.
    """
    if on is None:
        on = heading_date(text)
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
    queued_day = REWRITE_QUEUE.get(on, {}) if on is not None and REWRITE_FROM <= on <= REWRITE_UNTIL else {}
    for spec, body in specs:
        items = re.split(r"(?m)^### ", body)[1:]
        queued = queued_day.get(spec)
        if len(items) == 0 or len(items) > 2 or (len(items) == 2 and queued is None):
            problems.append(f"{spec}: 항목 {len(items)}개(정확히 1개여야 함)")
            continue
        for index, raw in enumerate(items):
            kind, headline, item_problems = item_structure_problems(spec, raw)
            problems.extend(item_problems)
            if index == 0 and is_rewrite_headline(headline):
                problems.append(f"{spec}: 첫 항목은 신규 칸이라 '(다시 정리)'로 끝나면 안 됨")
            if index == 1:
                if kind != "paper":
                    problems.append(f"{spec}: 다시 정리 칸은 paper여야 함")
                elif not is_rewrite_headline(headline):
                    problems.append(f"{spec}: 두 번째 항목 헤드라인은 '(다시 정리)'로 끝나야 함")
                elif queued is None or not rewrite_matches(headline, queued):
                    problems.append(f"{spec}: 두 번째 항목이 이 날짜 §3.1 대기열 시험이 아님")
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
        on = date.fromisoformat(m.group(1))
        probs = one_item_problems(path.read_text(encoding="utf-8"), int(m.group(2)), on)
        if probs:
            bad(f"{path.name} 과목당 항목 형식: " + "; ".join(probs[:6]))
    if checked:
        ok(f"one-item format checked on {checked} briefing(s) from {ONE_ITEM_FROM}")
    else:
        ok(f"one-item format: no briefings from {ONE_ITEM_FROM} yet (template only)")
    check_rewrite_examples()


_PAPER_BODY = """한 줄.

#### 중요도 점수
| 항목 | 배점 | 점수 | 근거 |
|---|---|---|---|
| 진료 결정 변화 | 25 | 20 | 예시 |
| 근거 수준 | 20 | 18 | 예시 |
| 가이드라인 반영 | 15 | 10 | 예시 |
| 국내 적용성 | 15 | 12 | 예시 |
| 내 환자군 빈도 | 15 | 10 | 예시 |
| 출처 확정성 | 10 | 8 | 예시 |
| **합계** | **100** | **78** | 예시 |

필수조건: 예시

#### 어떤 연구
예시
#### 초록
예시
#### 주요 결과
예시
#### 적용 알고리즘
예시
#### 한계
예시
#### 출처
예시
"""

_REVIEW_BODY = """한 줄.

#### 중요도 점수
| **합계** | **100** | **40** | 질환 정리 |

필수조건: 해당 없음(질환 정리)

#### 기전
예시
#### 진단
예시
#### 치료
예시
#### 출처
예시
"""


def _sample_edition(on: date, day: int, sections: list[tuple[str, list[tuple[str, str]]]]) -> str:
    parts = [f"# {on.isoformat()} (Day {day})", "> 예시", ""]
    for spec, items in sections:
        parts.append(f"## SPECIALTY_{spec}")
        for kind, headline in items:
            parts.append(f"### {kind}: {headline}")
            parts.append(_PAPER_BODY if kind == "paper" else _REVIEW_BODY)
    parts.extend(["## SELF_CHECK", "### Q1. 예시", "### Q2. 예시", "### Q3. 예시", "## RECALL_CARD", "## AUTHOR", ""])
    return "\n".join(parts)


def _day1(
    on: date,
    nephro: list[tuple[str, str]],
    endo: list[tuple[str, str]],
    cardio: list[tuple[str, str]],
) -> str:
    return _sample_edition(
        on,
        1,
        [("NEPHROLOGY", nephro), ("ENDOCRINOLOGY", endo), ("CARDIOLOGY", cardio)],
    )


def _expect_ok(label: str, text: str, day: int, on: date) -> None:
    probs = one_item_problems(text, day, on)
    if probs:
        bad(f"{label}: " + "; ".join(probs[:4]))
    else:
        ok(label)


def _expect_has(label: str, text: str, day: int, on: date, needle: str) -> None:
    probs = one_item_problems(text, day, on)
    if any(needle in p for p in probs):
        ok(label)
    else:
        bad(f"{label}: 기대 {needle!r}, 실제 {probs[:4]}")


def _insert_rewrite(text: str, specialty: str, headline: str) -> str:
    """과목에 항목이 하나일 때만 paper 재정리 칸을 섹션 끝에 붙인 사본을 돌려준다."""
    pattern = rf"(?ms)^(## SPECIALTY_{specialty}\b.*?)(?=^## )"
    found = re.search(pattern, text)
    if not found:
        raise RuntimeError(f"섹션 없음: {specialty}")
    if len(re.findall(r"(?m)^### ", found.group(1))) != 1:
        return text
    block = f"### paper: {headline}\n{_PAPER_BODY}"
    return text[: found.end(1)] + block + text[found.end(1) :]


def check_rewrite_examples() -> None:
    """§3.1 형태가 통과하고, 대기열 밖·표기 오류는 거절되는지 예시로 확인한다."""
    new_n = ("paper", "신규 신장 논문 (KI 2026-11)")
    new_e = ("review", "부신기능저하 — 성인 하이드로코르티손")
    new_c = ("paper", "신규 심혈관 논문 (NEJM 2026-11)")
    nov26 = date(2026, 11, 26)
    edition = _day1(
        nov26,
        [new_n, ("paper", "EMPA-KIDNEY, 신장 보호 (NEJM 2023) (다시 정리)")],
        [new_e, ("paper", "SOUL, 경구 semaglutide (NEJM 2025) (다시 정리)")],
        [new_c, ("paper", "FINEARTS-HF, finerenone (NEJM 2024) (다시 정리)")],
    )
    _expect_ok("예시 2026-11-26: EMPA-KIDNEY·SOUL·FINEARTS-HF (다시 정리) 통과", edition, 1, nov26)
    _expect_ok("예시 2026-11-26: 재정리 없이 신규 1항목 유지", _day1(nov26, [new_n], [new_e], [new_c]), 1, nov26)
    _expect_has(
        "예시: 대기열 밖 시험은 거절",
        _day1(nov26, [new_n, ("paper", "DAPA-CKD (다시 정리)")], [new_e], [new_c]),
        1,
        nov26,
        "대기열 시험이 아님",
    )
    _expect_has(
        "예시: '(다시 정리)'로 끝나지 않으면 거절",
        _day1(nov26, [new_n, ("paper", "EMPA-KIDNEY (다시 정리) 메모")], [new_e], [new_c]),
        1,
        nov26,
        "끝나야 함",
    )
    _expect_has(
        "예시: 항목 3개는 거절",
        _day1(
            nov26,
            [new_n, ("paper", "EMPA-KIDNEY (다시 정리)"), ("paper", "EMPA-KIDNEY 추가 (다시 정리)")],
            [new_e],
            [new_c],
        ),
        1,
        nov26,
        "항목 3개",
    )
    _expect_has(
        "예시: 재정리만 있고 신규 칸이 없으면 거절",
        _day1(nov26, [("paper", "EMPA-KIDNEY (다시 정리)")], [new_e], [new_c]),
        1,
        nov26,
        "신규 칸",
    )
    _expect_has(
        "예시: 재정리를 첫 항목에 두면 거절",
        _day1(nov26, [("paper", "EMPA-KIDNEY (다시 정리)"), new_n], [new_e], [new_c]),
        1,
        nov26,
        "신규 칸",
    )
    _expect_has(
        "예시: 다시 정리 칸이 review이면 거절",
        _day1(nov26, [new_n, ("review", "EMPA-KIDNEY (다시 정리)")], [new_e], [new_c]),
        1,
        nov26,
        "paper여야 함",
    )
    _expect_has(
        "예시: 2026-11-25는 과목당 1항목",
        edition,
        1,
        date(2026, 11, 25),
        "정확히 1개여야 함",
    )
    day2 = _sample_edition(
        date(2026, 11, 27),
        2,
        [
            ("INFECTIOUS", [new_n, ("paper", "EMPA-KIDNEY (다시 정리)")]),
            ("PULMONOLOGY", [new_c]),
            ("GASTROENTEROLOGY", [new_e]),
        ],
    )
    _expect_has("예시: Day 2 회차는 재정리 칸 없음", day2, 2, date(2026, 11, 27), "정확히 1개여야 함")
    _expect_has(
        "예시: FLOWPROMOTE는 FLOW 대기열이 아님",
        _day1(
            date(2026, 11, 29),
            [new_n, ("paper", "FLOWPROMOTE (다시 정리)")],
            [("paper", "SURPASS-CVOT (다시 정리)")],
            [("paper", "STEP-HFpEF (다시 정리)")],
        ),
        1,
        date(2026, 11, 29),
        "대기열 시험이 아님",
    )
    _expect_ok(
        "예시 2026-12-02: 투석 당뇨 semaglutide 관찰연구",
        _day1(
            date(2026, 12, 2),
            [new_n, ("paper", "CONFIDENCE (다시 정리)")],
            [new_e, ("paper", "투석 당뇨 semaglutide 관찰연구 (다시 정리)")],
            [new_c, ("paper", "VESALIUS-CV (다시 정리)")],
        ),
        1,
        date(2026, 12, 2),
    )
    _expect_ok(
        "예시 2026-12-08: CONVINCE와 Cochrane 대류투석",
        _day1(
            date(2026, 12, 8),
            [new_n, ("paper", "Cochrane 대류투석과 CONVINCE (다시 정리)")],
            [new_e],
            [new_c],
        ),
        1,
        date(2026, 12, 8),
    )
    _expect_ok(
        "예시 2026-12-08: Cochrane 대류투석만 적어도 같은 대기열",
        _day1(date(2026, 12, 8), [new_n, ("paper", "Cochrane 대류투석 (다시 정리)")], [new_e], [new_c]),
        1,
        date(2026, 12, 8),
    )
    _expect_has(
        "예시 2026-12-08: 내분비 재정리 칸은 없음",
        _day1(date(2026, 12, 8), [new_n], [new_e, ("paper", "SOUL (다시 정리)")], [new_c]),
        1,
        date(2026, 12, 8),
        "정확히 1개여야 함",
    )
    _expect_has(
        "예시: 2026-12-15 이후는 과목당 1항목",
        _day1(date(2026, 12, 17), [new_n, ("paper", "VISIONARY (다시 정리)")], [new_e], [new_c]),
        1,
        date(2026, 12, 17),
        "정확히 1개여야 함",
    )

    live = ROOT / "briefings" / "2026-11-26-day1.md"
    if not live.exists():
        bad("예시: briefings/2026-11-26-day1.md 없음")
        return
    augmented = live.read_text(encoding="utf-8")
    augmented = _insert_rewrite(augmented, "NEPHROLOGY", "EMPA-KIDNEY, 신장 보호 (다시 정리)")
    augmented = _insert_rewrite(augmented, "ENDOCRINOLOGY", "SOUL, 경구 semaglutide (다시 정리)")
    augmented = _insert_rewrite(augmented, "CARDIOLOGY", "FINEARTS-HF, finerenone (다시 정리)")
    _expect_ok(
        "예시: 오늘 11/26 파일에 EMPA-KIDNEY·SOUL·FINEARTS-HF (다시 정리)를 붙인 형태",
        augmented,
        1,
        nov26,
    )


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
