# study-briefing 스케줄드 태스크 등록 가이드

> 이 파일은 Cowork에서 새 스케줄드 태스크 `study-briefing`을 등록할 때 사용하는 **프롬프트 + 메타데이터**입니다.
> 한 번 등록 후엔 매일 18:00 KST에 자동 실행됩니다.

## 등록 방법

1. Cowork에서 **새 대화창**을 엽니다 (지금처럼 스케줄드 태스크 안에서 시작된 세션이 아닌, 일반 대화창).
2. 다음과 같이 요청하세요:

   > "아래 명세대로 `study-briefing` 스케줄드 태스크를 등록해줘. cron은 `0 18 * * *` (매일 18:00 KST)."
   >
   > (그리고 이 파일의 "프롬프트" 섹션 전체를 붙여넣기)

3. Claude가 `create_scheduled_task` 도구로 등록하면 끝.

---

## 메타데이터

- **taskId:** `study-briefing`
- **description:** 의학 심화 학습 브리핑 — 매일 18:00 KST, 3일 사이클로 과목별 논문·가이드라인·심사·신약·상호작용·안전경보 자동 작성
- **cronExpression:** `0 18 * * *` (매일 18:00 로컬 = KST)
- **notifyOnCompletion:** `true` (각 회차 완료 시 알림)

---

## 프롬프트 (그대로 등록)

```
You are running the **study-briefing** scheduled task — a personal medical-study briefing for 김병우 (신장내과 전문의), produced daily at 18:00 KST on a 3-day rotation cycle. Output is consumed by a static-site PWA at https://bwkim1025.github.io/study/.

## Repository
- Local path on user's machine: `C:\Users\USER\Documents\GitHub\study`
- GitHub: `bwkim1025/study`
- Output target: `briefings/YYYY-MM-DD-dayN.md` (one file per run, at the repo root)

## Step 1 — Determine today's Day cycle
Use today's date in KST (UTC+9). Compute:
  daysFromAnchor = (today_KST_date - 2026-05-09).days   // anchor: 2026-05-09 = Day 1
  dayN = (daysFromAnchor % 3) + 1   // result: 1, 2, or 3

Then map to the day's specialty group:

| Day | Specialties (use these exact KEYS in `## SPECIALTY_<KEY>`) |
|---|---|
| 1 | NEPHROLOGY, ENDOCRINOLOGY, CARDIOLOGY |
| 2 | INFECTIOUS, PULMONOLOGY, GASTROENTEROLOGY |
| 3 | FAMILY, RHEUMATOLOGY, PSYCHIATRY, GERIATRICS |

## Step 2 — Read editorial principles (canonical format spec)
Read `C:\Users\USER\Documents\GitHub\study\EDITORIAL-PRINCIPLES.md`. Sections 1 (6-month window), 2 (Tier S/A/B priority — CRITICAL), 3 (90-day dedup), 4 (Day 1 nephrology ×2), 5 (categories), and 7 (markdown structure) are canonical — follow them exactly. If the file disagrees with this prompt, follow the file (it may have been updated).

Required sections in order:
1. `# YYYY-MM-DD (Day N)` h1 with date and Day N
2. `> <one-line title>` blockquote (e.g., "본인 학습용 — Day 1: 신장×2 · 내분비/당뇨 · 심혈관")
3. `## SPECIALTY_<KEY>` for each specialty in the day's group. **Item count per category depends on the specialty (see §4 of EDITORIAL):**
   - **Day 1 NEPHROLOGY** (kidney is doubled): `paper × 4`, `guideline × 2`, `insurance × 2`, `drug × 2`, `interaction × 2`, `safety × 2` = **14 items** in this order
   - **All other specialties** (Day 1 Endo/Cardio + all of Day 2/3): `paper × 2` + `guideline × 1` + `insurance × 1` + `drug × 1` + `interaction × 1` + `safety × 1` = **7 items** in this order
   - When multiple papers, use repeated `### paper:` headings; the topics must be distinct (e.g., positive trial vs safety/negative, or core kidney vs cardiorenal).
4. `## CASE` (optional, ~once per week — typically Day 1) — single hypothetical clinical scenario, `### <case headline>` followed by 1~2 paragraphs of natural prose. Must end with the disclaimer: "(가상 시나리오, 실제 환자 정보 아님)".
5. `## SELF_CHECK` — 2 or 3 questions in `### Q1.` / `### Q2.` form. Body is multiple-choice options on separate lines, then `#### 답·해설` block with the correct option in **bold** and rationale.
6. `## RECALL_CARD` — **8~10** single-line takeaway bullets
7. `## AUTHOR` — `<Model name> · <model-id> · <YYYY-MM-DD HH:MM KST>`

Total item count per cycle:
- **Day 1**: 14 (nephrology) + 7 + 7 = **28 items**
- **Day 2**: 7 + 7 + 7 = **21 items**
- **Day 3**: 7 + 7 + 7 + 7 = **28 items**

Item structure rules:
- One-line summary directly under each h3 (no h4 prefix needed for the summary).
- Expanded body uses h4 blocks. Different depth per category:
  - **paper** → `#### 어떤 연구`, `#### 초록`, `#### 주요 결과`, `#### 적용 알고리즘`, `#### 국내 vs 해외`, `#### 출처`
  - **guideline** → `#### 어떤 연구`, `#### 적용 알고리즘`, `#### 국내 vs 해외`, `#### 출처`
  - **insurance** → `#### 적용 알고리즘`, `#### 출처` (시행일 명시 필수)
  - **drug** → `#### 적용 알고리즘`, `#### 금기·주의`, `#### 출처`
  - **interaction** → `#### 적용 알고리즘`, `#### 출처`
  - **safety** → `#### 적용 알고리즘`, `#### 출처`
- Item headlines must include distinctive English keyword(s) (drug/trial/agency name) — these are what users skim by.
- DO NOT write a `## DECISION_POINTS` section. The PWA's old DP feature was removed; the SPECIALTY sections themselves are the briefing.

## Step 3 — Source content via web search (with Tier-based selection)

**Search window:** last **6 months** (not 30 days). For each specialty × category, gather 3~5 candidate items from the priority sources below, then classify each candidate as Tier S / A / B (see EDITORIAL §2):

- **Tier S** — clinical prescribing changes today, domestic application available or imminent within 6 months. Examples: 식약처/심평원 changes, KSN/KSE updates, KDIGO/ESC/ACC major updates with Korean rollout, FDA black-box that triggers immediate Korean monitoring change.
- **Tier A** — recommendation strength change, domestic application within 6 months. Examples: 적응증 확대, focused updates, phase 3 RCT primary positive likely to enter next guideline.
- **Tier B** — academic value but ≥1 year before clinical impact, or no Korean adoption planned.

**Slot fill rule:** For each category slot, pick the highest-Tier candidate available. Fill all S first, then A, then B. If only B candidates exist for a slot, use B; if no candidates at all, write `(이번 회차 신규 사항 없음)` and omit body.

Do **NOT** show Tier labels in the output — Tier classification is the author's selection criterion only.

Priority sources:
- Journals: NEJM, Lancet, JAMA, BMJ, Circulation, Kidney International, Diabetes Care, AJRCCM, Gut, Hepatology, Annals of Rheumatic Diseases, Lancet Infectious Diseases, JAGS (geriatrics), etc.
- Guidelines: KDIGO, ACC/AHA, ESC, ADA/EASD, IDSA, GINA, GOLD, ACR, AGA, ACG, EULAR; 국내 학회 — KSN, KSE, KDA, KAFM, 대한감염학회, 대한결핵및호흡기학회, 대한소화기학회, 대한류마티스학회, 대한노인의학회 등
- Insurance/regulatory: 심평원 (HIRA, www.hira.or.kr), 식약처 (MFDS), FDA, EMA
- For 국내 vs 해외 comparison: always include domestic society or 심평원 stance when applicable

For `interaction` and `safety` items: prioritize clinically actionable cross-specialty issues (입원 환자에서 신·간 기능별 용량 조정, QT 연장 약물 조합, 신독성, CYP3A4 강력 저해/유도, 면역억제제 모니터링 등).

## Step 4 — Write the markdown file
Construct the full markdown following the format spec above. Length target:
- **Day 1**: ~8,000~11,000 characters of body content (28 items, kidney doubled)
- **Day 2/3**: ~6,000~9,000 characters

Per item 200~400 chars on expanded body.

**Avoid duplication (90-day window):** a topic that was covered within the past **90 days** should only re-appear if there is a genuine new development (additional reporting, policy reaction, price/dose update, regulatory action). Plain re-statement is not allowed. Check by reading all files in `briefings/` matching the past 90 days and matching by drug/trial/agency keyword.

The PWA renders SPECIALTY sections in the order they appear, with each item collapsible (click to expand the body blocks). Headlines should stand alone — the user skims headlines, then taps to deep-read.

## Step 5 — Save and commit
1. Write the file to: `C:\Users\USER\Documents\GitHub\study\briefings\YYYY-MM-DD-dayN.md` (use Linux mount path if needed: `/sessions/<id>/mnt/study/briefings/...`).
2. Use bash to: `cd` into the repo, create a git branch named `claude/study-YYYYMMDD-dayN`, `git add` the new file, `git commit -m "Study briefing YYYY-MM-DD (Day N)"`, `git push -u origin <branch>`.
3. Use the GitHub CLI (`gh pr create`) to open a pull request titled `Study briefing YYYY-MM-DD (Day N)` against `main`. If the repo has `.github/workflows/auto-merge-briefing.yml`, PRs from `claude/`-prefixed branches will auto-merge. Otherwise the user merges manually.
4. Log success and the published URL `https://bwkim1025.github.io/study/` in the run output.

## Self-identification (AUTHOR field)
Read your own model from the env section of your system prompt at runtime. Format: `<human-readable name> · <api-model-id> · <YYYY-MM-DD HH:MM KST>`. Examples:
- `Claude Opus 4.7 · claude-opus-4-7 · 2026-05-12 18:00 KST`
- `Claude Sonnet 4.6 · claude-sonnet-4-6 · 2026-05-12 18:00 KST`

If the model id cannot be determined with certainty, use `(미확인)` for the id token but still provide your best human-readable name.

## Quality bar (non-negotiable)
- All factual claims (study results, guideline numbers, regulatory dates, drug names) must come from a real, citable web source. Do NOT fabricate statistics, paper titles, or trial names.
- If a category has no fresh content for a specialty in the past 30 days, write `(이번 회차 신규 사항 없음)` as that one item's headline and omit its expanded body — do NOT invent material to fill the slot.
- Korean medical terminology preferred. Drug names: standard abbreviations OK (SGLT2i, GLP-1 RA, ACEi 등) without translation.
- Be precise with numbers, p-values, confidence intervals when reported in the source. Round only when source rounds.
- Avoid sensational language ("획기적", "혁명적" 등). Stick to clinical tone.

## Constraints (strict)
- Write ONLY to `briefings/`. Do NOT touch root `index.html`, `sw.js`, `manifest.json`, `EDITORIAL-PRINCIPLES.md`, or any other infrastructure file.
- The CASE section is hypothetical — no real patient data, no PHI.
- If web search fails or returns insufficient results across multiple specialties, abort the run and report the failure rather than producing a low-quality briefing.
```
