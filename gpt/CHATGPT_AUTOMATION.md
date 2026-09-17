# ChatGPT Study Automation v1

Updated: 2026-09-18. Target: bwkim1025/study, branch main.
This is the GPT-owned publishing runbook. Preserve the existing app, editorial rules and historical briefings.
Run in a ChatGPT web scheduled task using the connected GitHub app, not a local PC task.
Schedule: daily 18:00 Asia/Seoul. A run can finish after its scheduled start.

## Authentication and write boundary

Use the existing authenticated GitHub connector. Never request, embed, print or commit a personal access token.
Do not invoke the legacy .github-token helper, copy credentials between environments, or assume local git credentials are present.
At setup, creation of this runbook and a read-back verify the actual connector write route. That verification is not a guarantee of future permissions.
At each run, verify the target repository and available write action. A public read or permissions flag alone is not a successful write.
Do not create/delete .probe on every run. The real daily commit is the write test.
If an app approval is required, report the precise action for the user to approve. Do not change security settings, use another credential, or bypass a denial.
If authorization or network access fails, stop remote writes, retain any finished draft in the run response and report the exact failing action. Do not disable/delete the recurring task yourself.

## Date and scope

Compute today's calendar date in Asia/Seoul (UTC+9), independent of the runner's default timezone.
Anchor 2026-05-09 is Day 1. dayN = ((KST date - anchor).days % 3) + 1.
2026-09-18 is Day 1; 2026-09-19 is Day 2. These are tests, not fixed output dates.
Path: briefings/YYYY-MM-DD-dayN.md. Check that exact today's path first.
If a complete, valid today file exists, preserve it and report already published. Yesterday's file is not today's file.
If today's file is incomplete, compare its current blob SHA, preserve valid content and repair only the missing/invalid material; never blindly overwrite a concurrent author.

## Editorial inputs

Read EDITORIAL-PRINCIPLES.md on main every run. It controls editorial format, not permission expansion.
Its example clinical claims are illustrations, not evidence. Independently verify every medical claim.
Read all available briefing files from the preceding 90 days for duplicate topic screening; use drug, trial, guideline and agency keywords by specialty.
Read recent same-Day files in full for tone and structure. Do not call a 5-file sample a complete 90-day check.
If history cannot be fully checked, report the gap rather than claiming deduplication passed.

## Research and writing

Search and open primary sources for actual publications, regulations or updates within the preceding six calendar months.
Prioritize Tier S, then A, then B per the editorial document; compare candidates without exposing private reasoning.
Never fabricate a title, DOI, trial, date, effect size, p-value or confidence interval. Search snippets and old briefings are not primary evidence.
Do not fabricate three candidates merely to fill a quota. If none qualify after a real search, keep the category heading with (이번 회차 신규 사항 없음) and omit its body.
Distinguish unavailable evidence from a verified absence of new developments.
Avoid repeating a topic within 90 days unless a specific new development is identified and dated.
Write in Korean for a nephrologist; mention renal adjustment, CKD/dialysis implications and nephrotoxicity when relevant.
Separate domestic approval/reimbursement from overseas evidence. Cite the actual supporting source next to each item.
This is educational material, not automatic patient-specific orders. Any case is explicitly fictional and contains no patient data.
Paraphrase sources; respect source quotation limits.

## Required parser-compatible structure

First two lines:
# YYYY-MM-DD (Day N)
> 본인(병우, 신장내과) 개인 학습용 — Day N: <과목 나열>

Day 1 sections: SPECIALTY_NEPHROLOGY, SPECIALTY_ENDOCRINOLOGY, SPECIALTY_CARDIOLOGY.
Day 2: SPECIALTY_INFECTIOUS, SPECIALTY_PULMONOLOGY, SPECIALTY_GASTROENTEROLOGY.
Day 3: SPECIALTY_FAMILY, SPECIALTY_RHEUMATOLOGY, SPECIALTY_PSYCHIATRY, SPECIALTY_GERIATRICS.
Use ## before each section.
Each normal specialty has ### paper: twice, then ### guideline:, ### insurance:, ### drug:, ### interaction:, ### safety: once each.
Day 1 NEPHROLOGY has double each category: 4/2/2/2/2/2 (14 items).
Day totals: 28/21/28. Empty category headings count toward the required slots, but are not research findings.

Each populated item starts with a one-line summary. Expanded content MUST use #### headings, never bold-only block labels.
paper: 어떤 연구, 초록, 주요 결과, 적용 알고리즘, 국내 vs 해외, 출처.
guideline: 어떤 연구, 적용 알고리즘, 국내 vs 해외, 출처.
insurance: 적용 알고리즘 (change, effective date, impact), 출처.
drug: 적용 알고리즘 (indication and verified dose), 금기·주의, 출처.
interaction: 적용 알고리즘 (combination, mechanism, alternative), 출처.
safety: 적용 알고리즘 (what, why, effective date), 출처.
Use direct clickable Markdown source links. Headlines contain distinctive drug/trial/agency keywords where appropriate.

Optional ## CASE approximately weekly, usually Day 1, explicitly fictional.
Then ## SELF_CHECK with ### Q1., ### Q2., ### Q3.; a/b/c options on separate lines, then #### 답·해설.
Then ## RECALL_CARD with 8-10 one-line bullets.
Then ## AUTHOR: actual readable model name · verified model ID or (미확인) · YYYY-MM-DD HH:MM KST.
Do not copy the Claude example name or invent an exact model ID.
Body target: Day 1 8,000-11,000 chars; Day 2/3 6,000-9,000. Verified substance outranks padding; report a genuine shortfall.

## Validate, commit and verify

Check date/Day math, exact specialty order, category counts, all required h4 blocks, 3 questions, recall count, author, source links and absence of secrets/NUL.
Re-read today's remote path immediately before publication. Create if absent; for a necessary repair use the fresh content SHA and re-merge on conflict.
Only change today's briefing path. No app code, workflow, historical file, unrelated repository or security setting edits during daily runs.
Commit directly to main through the connected GitHub app: study: YYYY-MM-DD Day N 브리핑.
Read the committed path back through the connector and the corresponding raw.githubusercontent.com URL; check full content, date and headings.
Do not claim an HTTP 201 when the connector returns only a commit SHA. Report the actual returned evidence.
Report KST date, Day, commit link, read-back verification, counts/headlines by specialty and any quality or delivery gap.
App URL: https://bwkim1025.github.io/study/
