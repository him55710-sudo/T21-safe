# Dataset Priority Matrix

문서 상태: acquisition/use 승인 기준<br>
레지스트리: [`research/dataset_registry.yaml`](../../research/dataset_registry.yaml)<br>
마지막 검토일: 2026-09-02

## Tier A — 즉시 demo와 signal pipeline

| Dataset | Access | 허용 역할 | 금지/주의 |
| --- | --- | --- | --- |
| VitalDB Open/API | OPEN | bounded intraoperative ingestion, timeline, demo, generic event engineering | DS label/성능을 추정하지 않음; case/device availability 편향 |
| BIDMC PPG and Respiration | OPEN | ECG/PPG/resp alignment, respiration/PPG feature 검증 | 53개의 8분 ICU record이며 clinical outcome model 불가 (DOI `10.13026/C2208R`) |
| Pulse Transit Time PPG v1.1.0 | OPEN | synchronized ECG–multi-site PPG, PTT/motion/attachment-force 검증 | 22 healthy adults; anesthesia/DS outcome 불가 (DOI `10.13026/jpan-6n92`) |
| Propofol autonomic dynamics | OPEN | controlled state의 autonomic feature 구현 확인 | 9 healthy volunteers; clinical outcome/DS calibration 불가 (DOI `10.13026/2rbc-1r03`) |
| MIT-BIH Arrhythmia | OPEN | R-peak/beat/rhythm detector regression tests | historical ambulatory enriched cohort; anesthesia outcome 불가 |
| VitalDB Arrhythmia v1.0.0 | OPEN | intraoperative R-peak/arrhythmia annotation 검증 | selected segments; DS label 미확인 (DOI `10.13026/axd6-wm13`) |
| Fantasia | OPEN | 2-hour resting HRV implementation/age stress test | healthy rest only; short anesthesia interpretation 불가 |

Tier A도 전체 bulk 다운로드가 기본이 아니다. `tools/datasets`의 필수 `--sample/--limit`과 checksum manifest를 사용한다.

## Tier B — 접근 승인 후 generic research

| Dataset | Access prerequisite | 허용 역할 | DS 관련 경계 |
| --- | --- | --- | --- |
| MIMIC-IV v3.1 | credential, CITI, DUA | ICU clinical event/missingness/medication timeline, generic model stress test | Q90 가능성과 matched waveform은 별도 질의; count 미확인 |
| MIMIC-III-Ext-PPG v1.1.0 | credential/training/DUA | PPG SQI, rhythm-conditioned feature validation | 6,189 ICU patients의 selected 30-s segments; DS count 미확인 (DOI `10.13026/r6k1-xt76`) |
| INSPIRE v1.4.2 | credential, CITI, Korea DUA | Korean perioperative generic event/external validation, 5-min numeric data | congenital/chromosomal diagnosis가 제외되어 DS 식별 불가 (DOI `10.13026/1eay-yc85`) |
| Multimodal Physiological Indices During Surgery | registered user + restricted DUA | drug/stimulus timing과 derived autonomic index 연구 | 101 surgeries; objective nociception ground truth가 아니며 DS count 미확인 (DOI `10.13026/gs4v-4q80`) |

MIMIC-IV Waveform preview와 MIMIC-III Waveform은 open sample로 signal pretraining에 쓸 수 있지만, 임상 table linkage는 별도 credential/DUA 조건을 따른다.

## Tier C — 병원 협력이 필요한 핵심 데이터

다음은 DS-specific 연구에 필수이며 공개 데이터로 대체하지 않는다.

- clinician-confirmed DS status와 matched non-DS control pool
- 마취/진정 전후 ECG, PPG, BP, SpO2, EtCO2/respiration
- source/device clock과 procedure phase
- 실제 약물 투여 timestamp
- airway intervention
- vasopressor 또는 anticholinergic administration(처치 권고가 아닌 label/context)
- 마취 시작·유도·절개/자극·회복 단계
- 사전 승인 postoperative/PACU outcome
- CHD, age, procedure/anesthesia context와 주요 confounder

Tier C만 `DS_FINE_TUNING`/DS-specific calibration 후보가 될 수 있으며 IRB, DUA, data-quality/adjudication gate와 external validation이 필요하다.

## Module mapping

기호: `P` primary, `S` secondary/stress-test, `—` 부적절 또는 미확인.

| Dataset/source | ingestion | signal quality | R-peak | HRV | PPG morphology | PTT | hypotension label | bradycardia label | respiratory deterioration | drug-response timing | DS calibration |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VitalDB Open | P | P | S | S | P | S | P | P | S | P | — |
| BIDMC PPG/Resp | P | P | S | S | P | S | — | — | P | — | — |
| PTT PPG | P | P | P | S | P | P | — | — | S | — | — |
| Propofol dynamics | S | S | — | P | — | — | — | — | — | S | — |
| MIT-BIH Arrhythmia | S | S | P | S | — | — | — | P | — | — | — |
| VitalDB Arrhythmia | S | P | P | S | — | — | — | P | — | — | — |
| Fantasia | S | S | S | P | — | — | — | — | S | — | — |
| MIMIC-IV clinical | P | S | — | — | — | — | S | S | P | P | — |
| MIMIC-IV Waveform | P | P | P | S | P | S | S | S | P | — | — |
| MIMIC-III Waveform | P | P | P | S | P | S | S | S | P | — | — |
| MIMIC-III-Ext-PPG | P | P | P | S | P | S | — | S | S | — | — |
| INSPIRE | P | S | — | — | — | — | P | P | P | P | — |
| Multimodal surgery indices | S | S | — | P | — | — | S | S | — | P | — |
| Hospital DS cohort | P | P | P | P | P | P | P | P | P | P | P |

## Acquisition decision rule

1. registry version/source/license/access를 다시 확인한다.
2. 연구 질문에 `P/S` 역할이 없으면 다운로드하지 않는다.
3. OPEN은 bounded sample부터, credential 자료는 공식 승인 후에만 접근한다.
4. source/version/license/checksum manifest를 남긴다.
5. patient-level split과 dataset origin을 유지한다.
6. 공개 datasets를 무분별하게 한 cohort로 병합하지 않는다.
7. DS identifiability가 `UNCERTAIN/NO`면 DS 사례로 label하지 않는다.
