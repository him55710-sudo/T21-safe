# 논문용 공개 데이터셋 공백 지도

문서 상태: Path B RUO — engineering QA vs 병원 DS cohort<br>
기준일: 2026-09-06<br>
레지스트리: [`research/dataset_registry.yaml`](../../research/dataset_registry.yaml), [`research/dataset_registry.csv`](../../research/dataset_registry.csv)<br>
관련: [`DATASET_PRIORITY_MATRIX.md`](DATASET_PRIORITY_MATRIX.md), [`DATA_GAP_MAP.md`](DATA_GAP_MAP.md), [`PICOTS.md`](PICOTS.md)

> **핵심:** 공개 데이터는 **generic signal pipeline·재현성·SQI** 검증(engineering QA)에 쓴다. 공개 세트로 **DS-specific 임상 성능·보정·외부 임상 타당성**을 주장하지 않는다. 이 문서는 새 PROXY bench·새 tip을 추가하지 않는다.

## 1. 한 줄 결론

논문에서 “공개 데이터로 무엇을 했고 / 무엇을 병원 DS cohort가 채워야 하는지”를 표로 분리한다. 전자는 **기술 재현**, 후자는 **임상 특성화·silent validation**이다. 둘을 섞어 쓰면 Path B 경계를 넘는다.

## 2. 역할 구분

| 역할 | 허용 | 금지 |
| --- | --- | --- |
| Engineering QA (공개) | ingestion, clock/gap, R-peak/PPG 검출 회귀, SQI, 결정적 재현, 단위·샘플링 점검 | DS 성능·확률·경보·소아 DS 일반화 |
| Hospital DS cohort (필수) | 확인된 DS status, matched control, phase·약물·중재 timeline, adjudicated endpoint, CHD 공변량 | 공개 세트로 대체·추정 |

Phase 0 (공개) ≠ Phase 1–3 (병원). Phase 0 통과는 DS 임상 증거가 아니다 (`PICOTS`).

## 3. 레지스트리 요약 (YAML/CSV와 동일 ID)

아래는 `research/dataset_registry.*`의 `dataset_id` · `recommended_project_role` · `down_syndrome_identifiable`를 논문 Methods/Limitations에 옮기기 위한 요약이다. 샘플 수·성능 수치를 새로 만들지 않는다.

| dataset_id | 권장 역할 (registry) | DS 식별 | 논문에서 쓸 수 있는 말 | 쓰면 안 되는 말 |
| --- | --- | --- | --- | --- |
| `vitaldb-open` | LIVE_DEMO | UNCERTAIN | 성인 비심장 수술 intraoperative 파형·numeric의 bounded ingestion/demo | DS label/성능 추정; bulk 전체 다운로드가 기본인 것처럼 서술 |
| `vitaldb-arrhythmia` | FEATURE_VALIDATION | UNCERTAIN | intraoperative R-peak/부정맥 annotation 회귀 | DS 서맥 임상 성능 |
| `bidmc-ppg-resp` | FEATURE_VALIDATION | NO | ECG/PPG/호흡 정렬·PPG feature 기술 검증 | DS/소아 임상 outcome |
| `ptt-ppg` | FEATURE_VALIDATION | NO | 동기 ECG–다부위 PPG, PTT/운동 조건 QA | 마취 중 BP proxy의 DS 타당성 |
| `propofol-autonomic-dynamics` | FEATURE_VALIDATION | NO | 통제 상태의 autonomic feature 구현 확인 | DS calibration·임상 outcome |
| `mit-bih-arrhythmia` | FEATURE_VALIDATION | NO | R-peak/리듬 detector regression | 마취·DS outcome |
| `fantasia` | FEATURE_VALIDATION | NO | 장시간 resting HRV 구현·연령 stress | 짧은 마취 window 임상 해석 |
| `mimic-iv` | GENERIC_EVENT_MODEL | UNCERTAIN | ICU 임상 이벤트·결측·약물 timeline의 generic stress (credential 후) | 확인되지 않은 Q90 수로 DS cohort 주장 |
| `mimic-iv-waveform` / `mimic-iii-waveform` | SIGNAL_PRETRAINING | UNCERTAIN | 파형 pretraining·SQI (접근 조건 준수) | 병원 DS silent 성능 대체 |
| `mimic-iii-ext-ppg` | FEATURE_VALIDATION | UNCERTAIN | PPG SQI·리듬 조건 feature (credential 후) | DS count/성능 |
| `inspire` | GENERIC_EVENT_MODEL | **NO** | 한국 성인 perioperative numeric(5분) generic 외부 스트레스 | DS 식별(염색체 코드 제외) · DS 성능 |
| `multimodal-surgery-anesthesia` | FEATURE_VALIDATION | UNCERTAIN | 약물/자극 timing과 파생 autonomic index 연구(제한 DUA) | objective nociception GT·DS 성능 |

Tier·모듈 매핑의 상세는 [`DATASET_PRIORITY_MATRIX.md`](DATASET_PRIORITY_MATRIX.md)를 따른다. 다운로드는 bounded `--sample/--limit`·checksum manifest 원칙을 유지한다.

## 4. 공개로 채울 수 있는 것 / 없는 것

| 모듈·질문 | 공개로 가능 (QA) | 병원 DS cohort가 공급해야 함 |
| --- | --- | --- |
| Ingestion / clock | WFDB·VitalDB 등 adapter, gap/unit | 병원 vendor/AIMS 고유 schema |
| SQI / R-peak | MIT-BIH, VitalDB Arrhythmia 등 | DS 유도 중 저관류·airway artifact 분포 |
| HRV 구현 | Fantasia·propofol 등 resting/통제 | 짧은 비정상 마취 window의 **임상 의미** |
| PPG / PTT | BIDMC, PTT-PPG | 소아 DS 말초·센서 환경 calibration |
| Generic hypo/brady label 공학 | VitalDB/INSPIRE/MIMIC operational 후보 | age/context DS 정의 + blinded adjudication |
| DS-specific calibration | **사실상 없음** | clinician-confirmed DS + control + CHD 등 |
| Prospective silent | 공개 replay는 일부 burden 추정만 | frozen shadow, 실시간 가용성·clock audit |

공백 ID G-01~G-12의 서술 틀은 [`DATA_GAP_MAP.md`](DATA_GAP_MAP.md)와 맞춘다.

## 5. 병원 DS cohort가 논문에 반드시 공급할 항목 (Tier C)

레지스트리·우선순위 문서와 동일 목록을 창업자용으로 재진술한다.

1. 임상의가 확인한 DS status와 동일 기관·시기 matched non-DS control pool  
2. 마취/진정 전후 ECG, PPG, BP, SpO2, EtCO2/respiration (가능 범위)  
3. source/device clock과 procedure phase anchors  
4. 실제 약물 투여 timestamp (처치 권고가 아닌 context/label)  
5. airway intervention 등 중재 기록  
6. 사전 승인 postoperative/PACU outcome (해당 시)  
7. CHD, age, procedure/anesthesia context 등 주요 confounder  

이 항목 없이 “DS 모델 성능” 표를 넣지 않는다.

## 6. 분포 이동 (논문 Limitations에 명시)

측정·보고할 shift (공개 → 병원으로 숨기지 않음):

- adult → pediatric  
- ICU/ambulatory/healthy → anesthesia/sedation  
- non-DS → DS  
- noncardiac OR → dental/procedural sedation  
- invasive ABP → intermittent cuff BP  
- 단일 기관/장비 → 다른 site/device  
- retrospective corrected time → prospective available-at time  
- 고SQI 선택 샘플 → 연속 임상 사례  

각 shift는 feature 분포, missingness/SQI, event prevalence, calibration·error mode로 **따로** 적는다.

## 7. 논문 문장 템플릿 (RUO)

**허용**

- “공개 데이터셋은 signal processing pipeline의 기술 검증에 사용했으며, Down syndrome 특화 성능 평가에는 사용하지 않았다.”
- “DS 식별이 불가하거나 미확인인 레지스트리 항목(`down_syndrome_identifiable=NO/UNCERTAIN`)은 DS 사례로 표기하지 않았다.”
- “임상 특성화와 silent validation은 협력병원 IRB/DUA 범위의 DS cohort에서만 수행한다(계획).”

**금지**

- 공개 세트 AUROC/AUPRC를 DS 임상 성능처럼 제시  
- INSPIRE 등에서 DS를 추론  
- 새 PROXY bench·FACT 언어·발명 시장/성능 수치  
- 공개 결과로 `clinical_validation=true` 암시  

## 8. 변경 규칙

- 데이터셋 추가·역할 변경은 `dataset_registry.yaml`/`csv`를 먼저 갱신한 뒤 본 문서를 맞춘다.  
- 본 문서는 Path B tip·PROXY 확장 지시서가 아니다.  
- Auditor FACT 승격 전, 공개 QA 결과를 임상 근거 원장에 넣지 않는다.
