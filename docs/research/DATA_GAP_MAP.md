# Data Gap Map

문서 상태: 데이터 획득·연구 go/no-go용<br>
마지막 검토일: 2026-09-02

## 핵심 결론

공개 데이터는 **generic signal pipeline**의 상당 부분을 검증할 수 있지만, DS-specific calibration·clinical validation·external site validation을 채울 수 없다. 특히 “진단 코드가 있을 수 있음”과 “동일 encounter의 고품질 waveform이 있음”은 별개다.

## 질문별 공백

| Gap ID | 필요한 근거/데이터 | 공개 데이터 상태 | 남은 공백 | 필요한 조치 | 공백 상태에서 금지할 주장 |
| --- | --- | --- | --- | --- | --- |
| G-01 | 충분한 DS 마취/진정 waveform cohort | VitalDB DS label 미확인; INSPIRE chromosomal diagnoses 제외; MIMIC Q90-waveform 교집합 미확인 | DS 사례 수, 대표성, signal coverage | 병원 IRB cohort query와 waveform 교집합 | DS-specific model 성능/확률 |
| G-02 | 소아 DS ECG/PPG/BP/EtCO2 | 공개 intraoperative 자료는 주로 성인 | 연령·장비·생리 distribution shift | 소아 협력기관 수집/검증 | 성인 모델의 소아 임상 적용 |
| G-03 | baseline·유도·시술·회복 phase | 공개 자료의 phase/event granularity 불균일 | 표준 phase anchors | anesthesia record/device marker linkage | event lead-time 임상 주장 |
| G-04 | age-appropriate bradycardia/hypotension ground truth | 공개 annotation 제한 | 임계값, 지속시간, source hierarchy | 임상의 consensus+adjudication pilot | “정확한 서맥/저혈압 예측” |
| G-05 | medication/airway indication | timing 또는 dose가 일부 자료에만 존재 | indication, chart latency, prophylaxis | MAR/pump/event audit와 blinded review | 약물 반응 인과/권고 |
| G-06 | CHD·OSA·airway·comorbidity | 코드 granularity/누락 | residual confounding | structured clinical covariates와 subgroup plan | CHD와 완전 독립이라는 보편 주장 |
| G-07 | multi-site/device external validation | 대다수 단일기관 | site/device drift | 별도 기관·장비 prospective validation | 일반화 가능한 성능 |
| G-08 | prospective real-time availability | retrospective corrected data가 많음 | latency, clock, missingness, outage | frozen shadow deployment audit | 실시간 사용 가능성 |
| G-09 | false alarm burden/human factors | 공개 replay로 일부 가능 | 임상의 이해·overreliance·workflow | replay/simulation study | 임상 유용성/안전성 |
| G-10 | clinical utility/outcome effect | 관찰·silent 단계 | intervention effect/equipoise | 별도 규제·IRB advisory trial | 사고 예방/outcome 개선 |
| G-11 | privacy/fairness in rare population | 공개 deidentified data로 제한적 | 재식별·낙인·접근 제한 위험 | site governance, community/ethics review | 환자/기관 eligibility score |
| G-12 | frequency-domain HRV in anesthesia | healthy/resting methods evidence | ventilation/nonstationarity validity | metric/window-specific prospective validation | LF/HF=교감/부교감 균형 |

## 모듈별 공개 데이터 충족도

| Module | 공개 데이터로 가능한 것 | 공개 데이터로 불가능/부족한 것 |
| --- | --- | --- |
| ingestion | WFDB/VitalDB/HDF/CSV adapters, units/clock/gap handling | 병원 vendor/AIMS 고유 schema 완전 검증 |
| signal quality | ECG/PPG motion/noise, ICU/intraop artifacts | DS/소아/특정 sensor에서의 failure distribution |
| R-peak detection | MIT-BIH, VitalDB Arrhythmia annotations | DS 유도 중 저관류/airway artifact 성능 |
| HRV feature | Fantasia/propofol/ECG reference 구현 | 짧은 비정상 마취 window의 임상 의미 |
| PPG morphology | BIDMC/MIMIC/PTT PPG | 소아 DS 말초관류/센서 환경 calibration |
| PTT | synchronized healthy ECG/PPG engineering validation | 마취 중 BP proxy의 DS 임상 validity |
| hypotension label | VitalDB/INSPIRE/MIMIC의 generic operational labels | age/context-specific DS label과 adjudication |
| bradycardia label | VitalDB Arrhythmia/ECG detector validation | DS-specific age/stage definition과 outcome linkage |
| respiratory deterioration | BIDMC respiration, ICU waveform | dental anesthesia airway intervention context |
| drug-response timing | VitalDB/INSPIRE/restricted surgery dataset 일부 | DS indication, exact administration, confounding |
| DS-specific calibration | 사실상 없음 | 병원 DS cohort 필수 |

## Distribution shifts to measure

- adult → pediatric
- ICU/ambulatory/healthy → anesthesia/sedation
- non-DS → DS
- noncardiac OR → dental/procedural sedation
- invasive ABP → intermittent cuff BP
- one hospital/device/firmware → another
- retrospective corrected timestamp → prospective available-at time
- high-SQI selected samples → consecutive clinical cases

각 shift는 feature distribution, missingness/SQI, event prevalence, calibration과 error mode로 따로 측정한다. 단순 pooled training으로 숨기지 않는다.

## 데이터 획득 우선순위

1. 병원 feasibility aggregate: unique patients/cases와 waveform 교집합.
2. IRB/DUA가 허용한 1–3 case deidentified schema/clock pilot.
3. DS retrospective consecutive cohort와 label feasibility.
4. matched control pool/overlap audit.
5. 별도 site prospective silent validation.

각 단계가 실패하면 이후 단계 데이터를 더 받는 것으로 자동 해결하지 않고 질문·scope를 재평가한다.
