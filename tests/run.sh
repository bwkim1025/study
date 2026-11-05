#!/usr/bin/env bash
# 땡이네 공부 — 의존성 없는 기본 점검 (앱 코드는 수정하지 않음)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== 땡이네 공부 기본 테스트 =="
echo "cwd: $ROOT"

python3 tests/checks.py
status=$?

echo
echo "== collab-core 동기화 =="
if bash scripts/check-collab-sync.sh; then
  echo "OK   check-collab-sync.sh"
else
  echo "FAIL check-collab-sync.sh"
  status=1
fi

if [[ $status -eq 0 ]]; then
  echo
  echo "ALL PASS"
else
  echo
  echo "FAILED"
fi
exit "$status"
