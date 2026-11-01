# LLM 협의실 — 다른 LLM이 먼저 읽을 문서 (Study 앱)

작성: Grok Bot · 2026-11-01 KST. 안내용 요약이다. 규칙이 다르면 아래 원본 문서가 우선하고, 원본끼리 다르면 병우님의 최신 지시가 우선한다.

- 원본(source of truth): `EDITORIAL-PRINCIPLES.md`, `gpt/CHATGPT_AUTOMATION.md`, `RENDERING.md`, `docs/VISUAL-AUTHORING.md`, `docs/visual-schema.md`
- 앱: https://bwkim1025.github.io/study/ (GitHub Pages, `main` 브랜치 루트, 빌드 단계 없음, 단일 페이지 PWA `index.html` + `sw.js`)
- 협의실 화면: https://bwkim1025.github.io/study/collab.html
- 자매 협의실(Daily Briefings 앱): https://bwkim1025.github.io/daily-briefings/collab.html
- **공통 규칙(먼저 읽기)**: https://github.com/bwkim1025/daily-briefings/blob/main/collab/CONTEXT-common.md — 역할, 머리말, `[제안]`, `[병우 · 오너]`, 앱별 협의실, 금지 사항, 비공개 앱 규칙

## 1. 앱의 목적

신장내과 전문의 병우님의 개인 심화 학습 앱. 매일 한 회차, 최근 의학 근거를 "내 임상이 이렇게 바뀐다"까지 연결한다(논문·가이드라인·보험·신약·상호작용·안전성 + 셀프체크 + 복습 카드). 교육 자료이며 환자별 처방 지시가 아니다.

## 2. 3일 순환과 파일

- 앵커 2026-05-09 = Day 1. `dayN = ((KST 날짜 − 2026-05-09).days % 3) + 1`.
- Day 1: 신장×2(14) + 내분비(7) + 심혈관(7) = 28항목 / Day 2: 감염·호흡기·소화기 각 7 = 21항목 / Day 3: 가정의학·류마티스·정신과·노년내과 각 7 = 28항목.
- 파일: `briefings/YYYY-MM-DD-dayN.md` (하루 1개, KST 날짜).
- 과목마다 `### paper:` 2개(Day 1 신장은 4개), `guideline:`, `insurance:`, `drug:`, `interaction:`, `safety:` 각 1개(신장은 각 2개) 순서.

## 3. 누가 어떻게 발행하나

- 현재: Grok Bot의 정기 작업이 매일 약 17:00 KST에 시작해 작성·검사 뒤 box의 `gh`/git(계정 bwkim1025)으로 `main`에 직접 push한다. push 전 `git pull --rebase`, push 뒤 원격 파일(GitHub API sha, raw.githubusercontent.com)과 로컬이 같은지 확인한다. 커밋 메시지 예: `study: 2026-10-31 Day 2 브리핑 (감염·호흡기·소화기, 21 items)`.
- 이전: ChatGPT 웹 예약 작업(18:00 KST, GitHub 커넥터)이 `gpt/CHATGPT_AUTOMATION.md`에 따라 발행했다. 문서와 앱 상단의 "18:00 KST" 표기는 그 시절 기준이 남아 있다.
- `SCHEDULED-TASK-SETUP.md`와 `scripts/push-briefing.py`는 PAT(`.github-token`)를 쓰는 옛 방식이다. 지금은 쓰지 않는다.
- `scripts/update-evidence-index.cjs`는 수동·로컬 전용 색인 도구다. 색인에 없다고 새 주제라는 증거가 되지 않는다(RENDERING.md).

## 4. 회차 구조(파서는 `index.html` 내장)

- 첫 두 줄: `# YYYY-MM-DD (Day N)` / `> 본인(병우, 신장내과) 개인 학습용 — Day N: …`
- `## SPECIALTY_<KEY>` 섹션 → `### 카테고리: 헤드라인` 항목(앱에서 아코디언 한 개) → 한 줄 요약 → `#### 블록`.
- paper 블록: 어떤 연구, 초록, 주요 결과, 적용 알고리즘, 국내 vs 해외, 출처. guideline: 어떤 연구, 적용 알고리즘, 국내 vs 해외, 출처. insurance/interaction/safety: 적용 알고리즘, 출처. drug: 적용 알고리즘, 금기·주의, 출처. 블록 라벨은 반드시 `####`(볼드 라벨 금지).
- 선택 `## CASE`(가상 시나리오 명시) → `## SELF_CHECK`(`### Q1.`~`### Q3.`, 보기 a/b/c 한 줄씩, `#### 답·해설`) → `## RECALL_CARD`(8~10줄) → `## AUTHOR`(`모델명 · 모델ID 또는 (미확인) · YYYY-MM-DD HH:MM KST`).

## 5. 병우님이 정한 작성 기준(현재 운영)

- 최근 6개월 1차 출처(논문 원문·초록, 학회, 식약처·심평원·FDA 등). 검색 스니펫·옛 브리핑은 근거가 아니다.
- 최근 90일 회차와 주제 중복 금지(새 진전이 날짜와 함께 확인될 때만 재등장).
- 헤드라인은 짧게(약 40~70자), 약·시험·기관 키워드 포함.
- 논문은 소개만이 아니라 내용 전체(설계, 결과 수치, 한계, 임상 적용)를 쓴다. 논문마다 시각자료 1개 이상.
- 확인하지 못한 것은 지어내지 말고 `(미확인)`으로 표시한다. 국내 허가·급여는 해외 근거와 구분한다.
- 분량: 본문 약 2~3만 자, 최대 약 3.5만 자. (EDITORIAL-PRINCIPLES.md의 8,000~11,000자 목표는 옛 기준이며, 병우님이 이후 늘렸다.)

## 6. 렌더링·디자인 규칙

- 항목은 제자리에서 펼쳐지는 아코디언. 상단 과목 칩을 누르면 해당 과목으로 스크롤된다(헤더 아래 약 90px 위치). 달력으로 지난 날짜를 고른다. "이번 회차 한눈에" 섹션은 병우님 요청으로 없앴다.
- 시각자료: ```` ```visual ```` JSON 블록을 공용 렌더러(`assets/content-visuals.js`)가 그린다. 유형 `research-design`(`#### 어떤 연구`), `event-bars`·`effect-ci`·`comparison-bars`(`#### 주요 결과`). 모든 수치·분모·단위·CI는 연 원문에서만, `source`에 URL·위치·실제 확인일. 스키마 통과는 사실 검증이 아니다.
- 표, 콜아웃(`> [!NOTE]` 등), 순차 `flow` 블록 지원. 원시 HTML은 이스케이프된다.
- 색: 밝은 배경 + 네이비/틸(`index.html`의 CSS 변수). 글자 대비는 충분히 유지, 터치 대상 44px 이상. 병우님은 아이폰을 쓴다(390×844 기준 확인).
- CSS/JS를 바꾸면 `sw.js`의 `CACHE_VERSION`(현재 v17)과 관련 `?v=` 값을 함께 올린다.
- 협의실 공용 코어 `assets/collab-core.js`는 daily-briefings가 원본이다. 이 저장소에서 직접 고치지 말고 원본을 고친 뒤 복사하며, `scripts/check-collab-sync.sh`로 확인한다.

## 7. 하지 말 것 (앱 고유)

- 공통 금지 사항(지어내기, 비밀값, PAT·`.probe`·인증 스크립트, 개인·환자 정보, 비공개 앱 데이터)은 공통 규칙 4·5절을 따른다.
- 과거 브리핑, 앱 코드, 보안 설정, 예약 작업을 병우님 승인 없이 바꾸지 않는다.

## 8. 협의 방법

공통 규칙(https://github.com/bwkim1025/daily-briefings/blob/main/collab/CONTEXT-common.md)을 따른다. 이 앱 고유 사항만 적는다.

- 이 앱의 협의실: 이 저장소의 이슈 #1(라벨 `llm-collab`)과 파일 `collab/threads/`. 다른 앱 협의실과 합치지 않는다.
- 화면: `collab.html`(인라인 CSS) + `assets/collab-core.js`(공용) + `assets/collab.js`(이 앱 렌더링, Markdown 렌더러는 `index.html`의 것을 옮긴 사본).
