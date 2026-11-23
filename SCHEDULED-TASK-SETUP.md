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
| 2 | NEPHROLOGY, INFECTIOUS, PULMONOLOGY, GASTROENTEROLOGY |
| 3 | NEPHROLOGY, FAMILY, RHEUMATOLOGY, PSYCHIATRY, GERIATRICS |

## Step 2 — Read editorial principles (canonical format spec)
Read `C:\Users\USER\Documents\GitHub\study\EDITORIAL-PRINCIPLES.md`. Sections 1 (6-month window for news, 5 years for core evidence), 2 (Tier S/A only, and the §2.1 paper gate — CRITICAL), 3 (core topics are repeated on purpose), 4 (nephrology in every briefing), 5 (slots, the `review` item, no empty slots), and 7 (markdown structure) are canonical — follow them exactly. If the file disagrees with this prompt, follow the file (it may have been updated).

Required sections in order:
1. `# YYYY-MM-DD (Day N)` h1 with date and Day N
2. `> <one-line title>` blockquote (e.g., "본인 학습용 — Day 1: 신장 · 내분비/당뇨 · 심혈관")
3. `## SPECIALTY_<KEY>` for each specialty in the day's group. **Few items, each one deep (see §4–§5 of EDITORIAL):**
   - **Every specialty in the day's group, NEPHROLOGY included: exactly 1 item**, filled in this order (EDITORIAL §5): ① a new `paper` from the last 6 months that passes the §2.1 practice-relevance gate (a practice-changing `guideline` update, Tier S/A, also counts); ② if none, **re-do a paper from past briefings** that passes §2.1 — write it in full depth as if new, re-check the source, never copy the old text, end the headline with `(다시 정리)`, and never re-do the same paper twice (search `briefings/` for existing `(다시 정리)` headlines); ③ if neither exists, a `review` (mechanism and treatment of one major disease, in the order of EDITORIAL §5.1).
   - For NEPHROLOGY, prefer what is closest to the owner's practice: hemodialysis, CRRT, vascular access, inpatient AKI and electrolytes.
   - **Regulatory add-on**: a Tier S change that alters prescribing right now (reimbursement, approval, safety) may follow that specialty's item as a short `insurance` / `drug` / `safety` item. At most 2 per briefing; omit if none.
   - **Never write an empty slot.** Do not write `(이번 회차 신규 사항 없음)`. If there is nothing worth including, leave the slot out.
4. `## CASE` (optional, ~once per week — typically Day 1) — single hypothetical clinical scenario, `### <case headline>` followed by 1~2 paragraphs of natural prose. Must end with the disclaimer: "(가상 시나리오, 실제 환자 정보 아님)".
5. `## SELF_CHECK` — 2 or 3 questions in `### Q1.` / `### Q2.` form. Body is multiple-choice options on separate lines, then `#### 답·해설` block with the correct option in **bold** and rationale.
6. `## RECALL_CARD` — **8~10** single-line takeaway bullets
7. `## AUTHOR` — `<Model name> · <model-id> · <YYYY-MM-DD HH:MM KST>`

Total item count per cycle (one item per specialty, plus at most 2 regulatory add-ons):
- **Day 1**: **3 items**
- **Day 2**: **4 items**
- **Day 3**: **5 items**

Item structure rules:
- One-line summary directly under each h3 (no h4 prefix needed for the summary).
- Expanded body uses h4 blocks. Different depth per category:
  - **paper** → `#### 어떤 연구`, `#### 초록`, `#### 주요 결과`, `#### 적용 알고리즘`, `#### 국내 vs 해외`, `#### 출처`
  - **review** → `#### 기전`, `#### 치료`, `#### 적용 알고리즘` (what changes for reduced kidney function and dialysis patients: dose, contraindications, monitoring, when to refer), `#### 금기·주의`, `#### 출처`
  - **guideline** → `#### 어떤 연구`, `#### 적용 알고리즘`, `#### 국내 vs 해외`, `#### 출처`
  - **insurance** → `#### 적용 알고리즘`, `#### 출처` (시행일 명시 필수)
  - **drug** → `#### 적용 알고리즘`, `#### 금기·주의`, `#### 출처`
  - **interaction** → `#### 적용 알고리즘`, `#### 출처`
  - **safety** → `#### 적용 알고리즘`, `#### 출처`
- Item headlines must include distinctive English keyword(s) (drug/trial/agency name) — these are what users skim by.
- DO NOT write a `## DECISION_POINTS` section. The PWA's old DP feature was removed; the SPECIALTY sections themselves are the briefing.

## Step 3 — Source content via web search (with Tier-based selection)

**Search window:** last **6 months** for new papers, guidelines and regulatory changes. For each slot, gather 3~5 candidates and classify each as Tier S / A / B (see EDITORIAL §2). A `paper` must also pass all three gates in EDITORIAL §2.1 (journal list, study design, adult internal-medicine relevance):

- **Tier S** — clinical prescribing changes today, domestic application available or imminent within 6 months. Examples: 식약처/심평원 changes, KSN/KSE updates, KDIGO/ESC/ACC major updates with Korean rollout, FDA black-box that triggers immediate Korean monitoring change.
- **Tier A** — recommendation strength change, domestic application within 6 months. Examples: 적응증 확대, focused updates, phase 3 RCT primary positive likely to enter next guideline.
- **Tier B** — academic value but ≥1 year before clinical impact, or no Korean adoption planned.

**Slot fill rule:** Use **Tier S and A only. Never use Tier B.** If a slot has no S/A candidate in the last 6 months: for nephrology ① revisit a core paper from the last 5 years; for nephrology ② and other specialties write a `review`; for nephrology ③ leave the slot out. Never write `(이번 회차 신규 사항 없음)`.

Do **NOT** show Tier labels in the output — Tier classification is the author's selection criterion only.

Priority sources:
- Journals: NEJM, Lancet, JAMA, BMJ, Circulation, Kidney International, Diabetes Care, AJRCCM, Gut, Hepatology, Annals of Rheumatic Diseases, Lancet Infectious Diseases, JAGS (geriatrics), etc.
- Guidelines: KDIGO, ACC/AHA, ESC, ADA/EASD, IDSA, GINA, GOLD, ACR, AGA, ACG, EULAR; 국내 학회 — KSN, KSE, KDA, KAFM, 대한감염학회, 대한결핵및호흡기학회, 대한소화기학회, 대한류마티스학회, 대한노인의학회 등
- Insurance/regulatory: 심평원 (HIRA, www.hira.or.kr), 식약처 (MFDS), FDA, EMA
- For 국내 vs 해외 comparison: always include domestic society or 심평원 stance when applicable

For `interaction` and `safety` items: prioritize clinically actionable cross-specialty issues (입원 환자에서 신·간 기능별 용량 조정, QT 연장 약물 조합, 신독성, CYP3A4 강력 저해/유도, 면역억제제 모니터링 등).

## Step 4 — Write the markdown file
Construct the full markdown following the format spec above. Length target:
- **Every day**: ~4,000~6,500 characters of body content. Only 3~5 items, so write each one in depth.

Per item: `paper` and `review` 1,000~1,500 chars of expanded body (results with absolute risk difference, number needed to treat, confidence interval, main adverse events and limitations; who to apply it to and who to leave out); regulatory add-ons 200~400 chars.

**Repetition (EDITORIAL §3):** important papers from past briefings are re-done on purpose, in full depth, with `(다시 정리)` at the end of the headline. One SELF_CHECK question should come from a core item 1 week to 3 months old. What is still not allowed is presenting the same news again as *new* without a genuine new development. Check by reading all files in `briefings/` matching the past 90 days and matching by drug/trial/agency keyword.

The PWA renders SPECIALTY sections in the order they appear, with each item collapsible (click to expand the body blocks). Headlines should stand alone — the user skims headlines, then taps to deep-read.

## Step 5 — Save and push (GitHub Contents API, NOT git push)
The scheduled-task sandbox has no persistent GitHub credentials, so `git push` and `gh` will both fail. Push the file directly through the GitHub Contents API instead:

1. Write the file to: `C:\Users\USER\Documents\GitHub\study\briefings\YYYY-MM-DD-dayN.md` (Linux mount path: `/sessions/<id>/mnt/study/briefings/...`).

2. Run the helper script — it reads the PAT from `./.github-token`, base64-encodes the file, PUTs it to `https://api.github.com/repos/bwkim1025/study/contents/briefings/YYYY-MM-DD-dayN.md` on the `main` branch, and syncs the local working copy:
   ```bash
   cd /sessions/<id>/mnt/study
   python3 scripts/push-briefing.py briefings/YYYY-MM-DD-dayN.md "Study briefing YYYY-MM-DD (Day N)"
   ```
   On success the script prints `OK: created|updated <path> → commit <sha>` and the GitHub blob URL.

3. If push fails (HTTP 401/403 → token bad or expired; HTTP 404 → token lacks Contents:write on the repo), abort the run and surface the error to the user rather than retrying. Do NOT fall back to `git push` — it will not work.

4. Log success and the published URL `https://bwkim1025.github.io/study/` in the run output.

### One-time setup (already done if `.github-token` exists at the repo root)
- Create a fine-grained PAT on GitHub: Settings → Developer settings → Fine-grained personal access tokens.
  - Repository access: only `bwkim1025/study`
  - Repository permissions: **Contents: Read and write**, Metadata: Read
  - Expiration: 1 year
- Save the token (one line, no trailing newline) to `C:\Users\USER\Documents\GitHub\study\.github-token`. The file is `.gitignore`d.
- Confirm `scripts/push-briefing.py` exists and is executable.

## Self-identification (AUTHOR field)
Read your own model from the env section of your system prompt at runtime. Format: `<human-readable name> · <api-model-id> · <YYYY-MM-DD HH:MM KST>`. Examples:
- `Claude Opus 4.7 · claude-opus-4-7 · 2026-05-12 18:00 KST`
- `Claude Sonnet 4.6 · claude-sonnet-4-6 · 2026-05-12 18:00 KST`

If the model id cannot be determined with certainty, use `(미확인)` for the id token but still provide your best human-readable name.

## Quality bar (non-negotiable)
- All factual claims (study results, guideline numbers, regulatory dates, drug names) must come from a real, citable web source. Do NOT fabricate statistics, paper title