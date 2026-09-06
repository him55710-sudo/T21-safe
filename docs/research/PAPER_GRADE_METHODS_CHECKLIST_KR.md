# 논문급 방법론 체크리스트 (Silent Shadow용)

문서 상태: Path B RUO — paper-grade readiness 점검표<br>
기준일: 2026-09-06<br>
관련: [`PICOTS.md`](PICOTS.md), [`STATISTICAL_ANALYSIS_PLAN.md`](STATISTICAL_ANALYSIS_PLAN.md), [`LABELING_PROTOCOL.md`](LABELING_PROTOCOL.md), [`CLINICAL_RESEARCH_LOCK_V0.md`](CLINICAL_RESEARCH_LOCK_V0.md)<br>
경로: **Path B / RUO / Shadow / `clinical_validation=false`** — FACT 승격은 Auditor·Founder+PI 전까지 금지

> 이 문서는 “무엇을 미리 고정해야 논문급 silent/shadow 연구가 되는지”를 창업자·연구책임자(PI)·통계가 같이 보는 쉬운 한국어 체크리스트다. **임계값·일차 평가변수·표본 수·성능 수치를 여기서 채우지 않는다.** 빈칸은 `PI_REQUIRED` 또는 `BIOSTAT_REQUIRED`로 표시한다.

## 1. 사용 원칙

| 표기 | 의미 |
| --- | --- |
| `PI_REQUIRED` | 마취·소아/치과마취 등 임상 책임자가 선택·합의해야 함. 엔지니어·PROXY 결과로 채우지 않음 |
| `BIOSTAT_REQUIRED` | 통계가 estimand·표본·검정력·보정·보고 형식을 확정해야 함 |
| `ENGINEERING_DEFAULT` | 코드/문서에 있는 연구용 기본값. 임상 lock이 아님 |
| `AUDITOR_GATE` | 원장/FACT 승격·프로토콜 동결 전 독립 검토 |

체크를 통과해도 **임상 유효성·진료 경보·투약 권고**를 주장하지 않는다. Silent shadow는 임상의에게 환자별 출력을 보여 주지 않는다.

## 2. PICOTS 고정 (`PI_REQUIRED` 중심)

| 항목 | 점검 | 비고 |
| --- | --- | --- |
| Population | [ ] 소아/성인 분리 분석 계획이 있는가 | 통합 계수 하나로 일반화 금지 (`PICOTS`) |
| Population | [ ] DS 확인은 승인된 구조화 진단만 쓰는가 | 자연어·phenotype 추정 금지 |
| Population | [ ] 환자 식별자로 반복 시술을 묶는가 | `PI_REQUIRED` + 데이터 거버넌스 |
| Index | [ ] pipeline release hash·전처리·feature schema가 동결되는가 | Phase 3 silent는 frozen deterministic |
| Comparator | [ ] Phase 1 baseline 내 비교 / Phase 2 matched·weighted control이 사전 정의되는가 | positivity 부족 시 `not estimable` |
| Outcomes | [ ] 생리 event · 중재 · procedure/PACU outcome을 한 복합으로 섞지 않는가 | family 분리 (`LABELING_PROTOCOL`) |
| Timing | [ ] baseline·phase·feature window·prediction horizon 후보가 결과 보기 전 후보로만 있는가 | 30/60/120/300초 등은 PRODUCT_ASSUMPTION |
| Setting | [ ] bedside 경고/치료 workflow와 격리된 research environment인가 | Shadow isolation |

**Primary endpoint family**는 [`CLINICAL_RESEARCH_LOCK_V0.md`](CLINICAL_RESEARCH_LOCK_V0.md)의 Options만 좁힌다. PROXY fixture PASS로 고르지 않는다. → `PI_REQUIRED`

## 3. Estimand (`BIOSTAT_REQUIRED` + `PI_REQUIRED`)

| 점검 | 담당 | 메모 |
| --- | --- | --- |
| [ ] Phase별 estimand가 문장으로 적혀 있는가 (association vs prediction) | BIOSTAT + PI | 치료·DS의 순수 인과효과로 명명 금지 (SAP §4) |
| [ ] 분석 단위가 patient인가 (case/window는 반복 측정) | BIOSTAT | cluster-robust / patient random effect |
| [ ] ATT/ATE 등 matching·weighting estimand가 사전 고정되는가 | BIOSTAT | caliper·ratio·overlap 규칙 포함 |
| [ ] CHD·연령층·procedure·anesthesia context의 effect modification이 사전 지정되는가 | PI + BIOSTAT | CHD는 제거 요인이 아니라 confounder/subgroup |
| [ ] 결측·SQI 실패·제외 사유가 flow diagram으로 보고되는가 | BIOSTAT | outcome을 본 뒤 제외 금지 |

## 4. Adjudication (암맹 판정)

| 점검 | 담당 | 메모 |
| --- | --- | --- |
| [ ] label schema version이 고정되는가 (`candidate-labels/…`) | PI | 후보 임계값은 승인 전 미확정 |
| [ ] algorithmic candidate와 reviewer 판정이 분리되는가 | PI | `PRESENT/ABSENT/UNCERTAIN/NOT_ASSESSABLE` |
| [ ] dual review + adjudicator 규칙이 있는가 | PI | 불일치·UNCERTAIN 처리 표 |
| [ ] 중재(vasopressor 등)를 생리 ground truth proxy로 자동 쓰지 않는가 | PI | indication 별도 adjudication |
| [ ] Git에 실제 patient/case key·자유서술 PHI를 넣지 않는가 | 전원 | PHI 금지 |

→ endpoint 임계값·연령별 절대 HR 기준: **`PI_REQUIRED`** (ENGINEERING_DEFAULT 인용 금지)

## 5. Leakage · Patient-level split

| 점검 | 담당 | 메모 |
| --- | --- | --- |
| [ ] 같은 환자의 모든 시술이 train/val/test 중 하나에만 속하는가 | BIOSTAT + Eng | patient-level split 필수 |
| [ ] threshold tuning·calibration refit·feature selection을 test/external에서 하지 않는가 | BIOSTAT | SAP §3 |
| [ ] future-aware filter·양방향 interpolation이 prospective feature에 금지되는가 | Eng | SAP §5 |
| [ ] 사건 이후 약물·미래 샘플·동일 신호에서 파생한 label 누수가 감사되는가 | Eng + BIOSTAT | dataset_registry `leakage_risks` 참고 |
| [ ] 공개 데이터셋끼리 무분별 병합·DS label 추정하지 않는가 | Eng | `down_syndrome_identifiable=NO/UNCERTAIN`면 DS로 표기 금지 |
| [ ] silent 실행 시점에 없던 delayed adjudication/record correction을 feature에 쓰지 않는가 | Eng | ground truth side만 (`PICOTS` Phase 3) |

## 6. Calibration · Discrimination · Alarm burden (Silent Shadow)

보고 후보(수치 채우기 금지 — 결과 확정 전):

- AUROC / AUPRC
- fixed false-alarm-rate sensitivity
- false alarms/hour (또는 동등 burden proxy)
- median lead time
- calibration intercept/slope, Brier score
- missingness / SQI failure rate

| 점검 | 담당 | 메모 |
| --- | --- | --- |
| [ ] 위 지표의 정의·분모·시간 단위가 SAP에 사전 적히는가 | BIOSTAT | 발명 수치·목표 AUC 금지 |
| [ ] calibration plot·subgroup(연령·CHD·장비·site) 계획이 있는가 | BIOSTAT | 단순 pooled 성능만으로 일반화 금지 |
| [ ] eligible set vs signal-evaluable set 차이를 함께 보여주는가 | BIOSTAT | SAP §2 |
| [ ] frozen prospective set를 개발 데이터로 되돌리지 않는가 | 전원 | Phase 3 lock |
| [ ] UI에 확률·진단·경보·치료 임계값 문구가 없는가 | Founder + Eng | RUO 라벨만 |

RII watch/elevated/high bins·절대/상대 HR 임계값: **`PI_REQUIRED`** / ENGINEERING_DEFAULT — 본 체크리스트에서 확정하지 않음. RII tip·PROXY bench 확장 없음.

## 7. 보고·거버넌스

| 점검 | 담당 |
| --- | --- |
| [ ] IRB/DUA·동의 범위와 추출 최소성이 문서화되는가 | PI + Founder |
| [ ] 금지 주장 목록(`PROHIBITED_CLAIMS`)과 RUO 문장이 논문·초록·발표에 반영되는가 | Founder |
| [ ] 새 문헌 수치를 Auditor FACT 승격 전에 지식베이스/원장에 넣지 않는가 | Auditor gate |
| [ ] 공개 데이터 결과는 “engineering QA”로만 표기하고 DS 임상 성능으로 쓰지 않는가 | 전원 |

## 8. Go / No-Go (요약)

**Go (논문급 silent shadow 설계로 진행 가능 — 임상 유효성 주장 아님):** PICOTS·estimand·adjudication schema·patient-level split·leakage audit·calibration 계획이 결과 보기 전에 글로 고정되고, `clinical_validation=false`가 유지될 때.

**No-Go:** endpoint를 PROXY PASS로 고름, 공개 non-DS 성능으로 DS 주장, PHI 커밋, FACT 무단 승격, 임상의에게 환자별 shadow 출력 노출.

## 9. 변경 규칙

- 본 표의 빈칸을 엔지니어가 숫자로 채우지 않는다.
- PI 세션은 Options를 좁히는 방식으로만 개정한다 (`CLINICAL_RESEARCH_LOCK_V0`).
- FACT·`clinical_validation=true`는 Master checklist + Auditor + Founder/PI 서명 전 금지.
