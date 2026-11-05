#!/usr/bin/env bash
# briefings/*.md 파일명만 모아 briefings/index.json 을 만든다.
# 앱(index.html 파서)은 이 파일을 읽지 않는다. 일일 게시·점검용 목록이다.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 - <<'PY'
from __future__ import annotations
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(".")
BRIEFINGS = ROOT / "briefings"
OUT = BRIEFINGS / "index.json"
PAT = re.compile(r"^(\d{4}-\d{2}-\d{2})-day([123])\.md$")
KST = timezone(timedelta(hours=9))

items = []
for path in sorted(BRIEFINGS.glob("*.md")):
    m = PAT.match(path.name)
    if not m:
        continue
    items.append({
        "date": m.group(1),
        "day": int(m.group(2)),
        "file": path.name,
    })

payload = {
    "generatedAt": datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S+09:00"),
    "count": len(items),
    "files": items,
}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(items)} files)")
PY
