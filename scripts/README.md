# scripts

- `bash scripts/build-index.sh` — `briefings/*.md` 파일명으로 `briefings/index.json`을 만든다(date/day/file만, 글자수 없음). 앱의 달력이 이 목록을 우선 읽고, 당일 항목이 빠지면 GitHub 목록도 확인한다. 일일 브리핑 게시 직후 한 번 호출하면 된다.
- `bash scripts/check-collab-sync.sh` — 협의실 공용 코어가 daily-briefings와 같은지 확인한다.
- `bash tests/run.sh` — 파서/v3 바이트·manifest·SW·브리핑 파일명·협의실 동기화 기본 점검.

- `node --test tests/reading-flow.test.cjs` — 외부 접속 없이 재생 칸의 글자 처리·날짜 전환·주소 조각을 점검한다.
