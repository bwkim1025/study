# Study 브리핑 편집 원칙

> 본인(병우, 신장내과) 개인 학습용. 매일 18:00 KST, Day 1/2/3 3일 사이클로 자동 작성.

## 핵심 원칙: 임상 직결 심화 학습

**"오늘 의료계는 어떻게 변했나" → "내 임상이 이렇게 바뀐다"** 까지 연결하는 능동적 학습 자료. 단순 큐레이션이 아니라 적용 알고리즘과 셀프체크까지.

## 1. 시간 우선순위

- **1순위 (필수):** 24시간 이내 발생·발표·공시된 이벤트
- **2순위 (조건부):** 전일 발표·공시 (KST 기준)
- **3순위 (제한적):** 24시간 이상 지난 사건이라도 새 진전(추가 보도·정책 반응·발언 추가)이 오늘 있으면 가능

학술지·가이드라인은 자연스럽게 주 단위 사이클이라 위 1·2순위를 너무 엄격히 적용하지 않아도 됨. 다만 본문에 정확한 일자(예: "5월 7일 오전", "5월 6일 종가", "직전 분기")를 명시할 것. 모호한 표현 ("최근", "한동안", "근래") 지양.

## 2. 재등장 규칙

- **30일 내** 같은 과목에서 다룬 토픽이 **새 진전**(추가 보도·정책 반응·가격 변동·발언 추가 등)이 있을 때만 재등장
- 단순 재언급("어제 발표된 X")은 제외
- 재등장 토픽은 DECISION_POINTS에서 `[재등장]` 태그로 표시
- 작성 시 `briefings/` 폴더의 최근 30일 파일을 읽어 중복 확인

## 3. 과목 그룹핑 (3일 사이클)

| Day | 과목 그룹 | 항목 수 |
|---|---|---|
| **Day 1** | 신장내과(NEPHROLOGY) · 내분비/당뇨(ENDOCRINOLOGY) · 심혈관(CARDIOLOGY) | 3 × 6 = 18 |
| **Day 2** | 감염내과(INFECTIOUS) · 호흡기(PULMONOLOGY) · 소화기/간(GASTROENTEROLOGY) | 3 × 6 = 18 |
| **Day 3** | 가정의학(FAMILY) · 류마티스(RHEUMATOLOGY) · 정신과(PSYCHIATRY) · 노년내과(GERIATRICS) | 4 × 6 = 24 |

앵커: 2026-05-09 = Day 1. `daysFromAnchor = (today_KST - 2026-05-09).days`, `dayN = (daysFromAnchor % 3) + 1`.

## 4. 과목별 6개 카테고리 (각 1항목씩)

1. `paper`: 최근 주요 논문 — top-tier 저널(NEJM·Lancet·JAMA·KI·Circulation 등)
2. `guideline`: 진료 가이드라인 변화 — 국내(KSN·KSE 등) + 해외(KDIGO·ACC/AHA 등)
3. `insurance`: 보험심사 변경 — 심평원 고시·급여 기준 변경
4. `drug`: 신약 정보 — 식약처/FDA 승인, 적응증 확대, 약가 등재
5. `interaction`: 약물 상호작용 — 입원 환자 다과 처방에서 위험 조합·대체
6. `safety`: 안전성 경보 — 식약처/FDA black-box·자진 회수·금기 추가

해당 과목에서 그날 신규 사항이 없는 카테고리는 헤드라인을 `(이번 회차 신규 사항 없음)`으로 적고 본문 생략. 억지로 채우지 말 것.

## 5. 작성 흐름 (필수 순서)

1. **먼저 SPECIALTY 항목 18(또는 24)개 작성** — 과목 × 카테고리 = 1 항목
2. **그 중 임상 영향 큰 12~18개를 골라 DECISION_POINTS로 압축** — 영향도 태그(`[즉시]`/`[변경]`/`[참고]`/`[재등장]`)와 함께
3. **DECISION_POINTS는 [즉시] → [변경] → [참고] → [재등장] 순으로 정렬**
4. CASE / SELF_CHECK / RECALL_CARD 작성

DECISION_POINTS는 SPECIALTY 항목보다 적거나 같음. 한 SPECIALTY 항목이 결정 포인트 0~2개를 만들 수 있다 (파급력 큰 항목은 2개도 가능, 미미한 항목은 0개).

## 6. DECISION_POINTS ↔ SPECIALTY 매칭 규칙 (PWA 자동 매칭, 필수)

PWA는 결정 포인트 클릭 시 매칭되는 SPECIALTY 항목 본문을 **그 자리에서 인라인 아코디언으로 펼친다**. 이 매칭은 영문 약어·약물명·기관명 토큰 점수 기반 자동 알고리즘이라, **양쪽 헤드라인에 동일 키워드 1~2개를 반드시 공유**해야 정확히 매칭된다.

**필수 공유 키워드 (최소 1~2개):**
- 약물명 (SGLT2i, GLP-1 RA, Tirzepatide, Tacrolimus, Voriconazole, Aficamten 등)
- 시험명 (SURPASS-CVOT, STEP-HFpEF, FIDELIO 등)
- 기관·가이드라인 (KDIGO, KSN, ADA, ESC, FDA 등)
- 질환 약어 (HFpEF, T2DM, CKD 등)도 도움이 됨

**좋은 예 (매칭 성공):**
- DP: `[즉시] SGLT2i, eGFR 20까지 처방 가능 — KDIGO 2026`
- SPECIALTY headline: `### paper: SGLT2i, CKD stage 4에서도 신기능 보존 (NEJM 2026-05)`
- → 공유 키워드: `SGLT2i` → 자동 매칭 ✓

**나쁜 예 (매칭 실패):**
- DP: `[즉시] 신기능 저하 환자 신약 처방 가능`
- → 약물명·기관명 없음 → 매칭 실패 → "매칭되는 항목 없음" 표시

**규칙 요약:** 결정 포인트 한 줄에는 그 출처 SPECIALTY 항목 헤드라인의 핵심 명사(영문 약어 우선)를 그대로 포함시킬 것.

## 7. 카테고리별 펼친 분량 가이드

| 카테고리 | 필수 블록 | 분량 |
|---|---|---|
| paper | 어떤 연구 + 초록 + 주요 결과 + 적용 알고리즘 + 국내 vs 해외 + 출처 | 깊게 (각 블록 2~4문장) |
| guideline | 어떤 연구(변경 전→후) + 적용 알고리즘 + 국내 vs 해외 + 출처 | 중간 (각 블록 2~3문장) |
| insurance | 변경 + 시행일 + 영향 + 출처 | 짧게 (총 2~3문장) |
| drug | 적응증 + 용량 + 금기·주의 + 적용 알고리즘 + 출처 | 중간 (각 블록 1~3문장) |
| interaction | 위험 조합 + 기전 + 대체 + 적용 알고리즘 + 출처 | 중간 (각 블록 1~2문장) |
| safety | 무엇·왜·언제부터 + 적용 알고리즘 + 출처 | 짧게 (총 2~3문장) |

전체 회차 분량 목표: **본문 5,000~7,500자**. 책상에서 0.5~1시간 안에 소화 가능한 양. 늘리지 말 것.

## 8. 마크다운 구조 (필수 형식)

```markdown
# 2026-05-09 (Day 1)
> 본인(병우, 신장내과) 개인 학습용 — Day 1: 신장 · 내분비/당뇨 · 심혈관

## DECISION_POINTS
- [즉시] SGLT2i, eGFR 20까지 처방 가능 — KDIGO 2026 갱신
- [즉시] Tacrolimus + voriconazole 30% 감량 필수
- [변경] HbA1c 7.5 (75세 이상 frail) — KSN 2026
- [변경] SGLT2i 급여 기준 변경 (2026-06-01 시행)
- [참고] HFpEF Aficamten 5년 사망률 −18% — Circulation
- [재등장] Tolvaptan FDA black-box 강화 (LFT 4주 간격)

## SPECIALTY_NEPHROLOGY
### paper: SGLT2i, CKD stage 4에서도 신기능 보존 (NEJM 2026-05)
eGFR 20~30 환자에서도 통계적으로 유의한 신기능 보존 확인.
#### 어떤 연구
...
#### 초록
...
#### 주요 결과
- 1차 결과: eGFR slope -1.8 vs -3.6 mL/min/y (p<0.001)
- 2차 결과: 투석 진입률 12% vs 19% (HR 0.62)
#### 적용 알고리즘
1. eGFR 20~30 + DM2 환자 외래 시 SGLT2i 추가 검토
2. 처방 시작 1개월 후 eGFR + electrolyte + lactate 체크
3. 볼륨 감소 환자는 이뇨제 25~50% 감량 동시
#### 국내 vs 해외
KDIGO 2026: eGFR 20까지 권고 / KSN 2025: eGFR 30까지. 국내 처방 시 심평원 삭감 위험.
#### 출처
- NEJM 2026-05 [https://www.nejm.org/doi/...]

### guideline: KDIGO 2026 — albuminuria target 50→30
...

### insurance: SGLT2i 급여 기준 변경 (2026-06-01 시행)
...

### drug: Aficamten FDA 승인 — HFpEF
...

### interaction: Tacrolimus + voriconazole — 30% 감량
...

### safety: Tolvaptan FDA black-box 강화
...

## SPECIALTY_ENDOCRINOLOGY
... (위와 같은 6개 카테고리 구조)

## SPECIALTY_CARDIOLOGY
... (위와 같은 6개 카테고리 구조)

## CASE
### 65세 남성, eGFR 28 + DM type 2 + EF 35%
65세 남성, 6년 전 DM2 진단, 4년 전 CKD stage 4 진행. 6개월 전부터 호흡곤란 NYHA II~III, EF 35% 확인. 외래 방문 시 Cr 2.4, K+ 4.8, ACE 사용 중. SGLT2i 추가 검토 중인데 eGFR 28에서 KSN 가이드라인 미준수 우려와 KDIGO 2026 신규 권고 사이에서 결정해야 함. 본 케이스는 본 회차 paper 항목과 직결되며, 적용 알고리즘 1단계가 그대로 적용된다 — 환자 동의 + 사유 차트 명시 후 처방 시작 + 1개월 모니터링. (가상 시나리오, 실제 환자 정보 아님)

## SELF_CHECK
### Q1. eGFR 22인 환자에 SGLT2i를 추가할 때 가장 적절한 모니터링 계획은?
a) 1주 후 BUN/Cr만
b) 1개월 후 eGFR + electrolyte + lactate
c) 6개월 후 albuminuria만
#### 답·해설
**b)** 1개월 후 eGFR + electrolyte + lactate. 이유: 초기 eGFR dip은 보통 1개월 내 발생, 케톤산증·전해질 이상 동반 가능. 1주는 너무 이르고 6개월은 너무 늦음.

### Q2. ...
#### 답·해설
...

## RECALL_CARD
- SGLT2i — eGFR 20까지 처방 가능 (KDIGO 2026 / KSN 30까지)
- HbA1c — 75세 이상 frail은 7.5 목표
- HFpEF — Aficamten 신규 승인, EF 50~60% 적응
- Tacrolimus + voriconazole — 30% 감량 필수
- Tolvaptan — black-box 갱신, LFT 4주 간격
- Finerenone — 1·4·이후 4개월 K+/eGFR 모니터링
- SGLT2i 급여 — 2026-06-01부터 eGFR 30 이상 + UACR ≥200 필수
- Aficamten 국내 — 식약처 검토 단계 ('25년 말~'26 초)

## AUTHOR
Claude Opus 4.7 · claude-opus-4-7 · 2026-05-09 18:00 KST
```

## 9. 분량 목표

- 한 회차 18 항목(Day 1/2) 또는 24 항목(Day 3) + DECISION_POINTS 12~18 + CASE 0~1 + SELF_CHECK 2~3 + RECALL_CARD 8~10
- 총 본문 5,000~7,500자
- 책상에서 0.5~1시간 안에 소화 가능한 양
- 늘리지 말 것

## 10. SELF_CHECK 형식 가이드

- `### Q1.` / `### Q2.` 헤딩으로 시작 (필수)
- 본문에 객관식 옵션 a/b/c (or a/b/c/d) — 한 줄씩, 들여쓰기 없이
- `#### 답·해설` 헤딩 아래 정답과 해설 (PWA가 토글 hidden 처리)
- 정답 옵션은 `**b)**` 식으로 굵게 표시 권장

## 11. CASE 형식 가이드

- 주 1회 권장, 주로 Day 1
- `### <환자 한 줄 묘사>` (예: `### 65세 남성, eGFR 28 + DM type 2 + EF 35%`)
- 본문은 prose 한~두 단락. 병력·검사·감별진단·의사결정을 자연스러운 산문으로 (강제 마커 X)
- 본 회차의 어느 SPECIALTY 항목과 직결되는지 한 줄 명시 권장
- 가상 시나리오 명시 ("가상 시나리오, 실제 환자 정보 아님") — PHI 절대 금지

## 12. 작성 모델 표기 (필수)

파일 끝에 `## AUTHOR` 섹션 반드시 포함.

**형식 (한 줄):**
```
## AUTHOR
Claude Opus 4.7 · claude-opus-4-7 · 2026-05-09 18:00 KST
```

- 첫 토큰: 사람이 읽기 쉬운 모델명 (예: `Claude Opus 4.7`, `Claude Sonnet 4.6`)
- 둘째 토큰: API에서 사용된 정확한 모델 ID (예: `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`)
- 셋째 토큰: 작성 시각 (KST, `YYYY-MM-DD HH:MM KST`)

**자기 식별:** 스케줄드 태스크는 자신이 실행 중인 모델 ID를 시스템 컨텍스트(env)에서 읽어 적는다. 모델 ID를 임의로 만들지 말 것. 확실하지 않으면 사람이 읽는 이름만 적고 ID 자리는 `(미확인)`로 표시.

## 13. 품질 기준 (non-negotiable)

- 모든 사실 주장(연구 결과, 가이드라인 수치, 규제 일자, 약물명)은 실제로 인용 가능한 웹 소스에서 와야 함. 통계·논문 제목·시험명을 **fabricate 금지**.
- 한 과목의 한 카테고리에 30일 내 신규 사항 없으면 헤드라인 `(이번 회차 신규 사항 없음)`으로 두고 본문 생략. 억지로 채우지 말 것.
- 한국 의학 용어 우선. 약물명: 표준 약어(SGLT2i, GLP-1 RA, ACEi 등) 번역 없이 사용 가능.
- 숫자, p-value, 신뢰구간은 소스에 보고된 그대로 정확히. 소스가 반올림한 경우에만 반올림.
- 선정성 표현 ("획기적", "혁명적" 등) 회피. 임상 톤 유지.
- DECISION_POINTS 한 줄에는 매칭되는 SPECIALTY 항목 헤드라인의 핵심 영문 키워드(약물명·시험명·기관명) 1~2개를 반드시 포함 — PWA 자동 매칭의 전제 (6번 참조).

## 14. 파일명 규칙

- `briefings/2026-05-09-day1.md` (Day 번호 명시, 캘린더와 라우터가 자동 인식)
- 매일 1개. Day 1/2/3 사이클로 반복.

---

> 작성: 2026-05-09 | 정비: 2026-05-09 (매칭 규칙 + 작성 흐름 명시 + UI 동작 갱신)
