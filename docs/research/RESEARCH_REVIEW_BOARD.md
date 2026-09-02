# T21 Safe Research Review Board

문서 상태: 순차 내부 역할검토 기록<br>
기준일: 2026-09-02<br>
적용 범위: `agent/research-data` 산출물<br>
전체 판정: **CONDITIONAL PASS — RUO/shadow 연구 준비 문서로만 사용 가능**

이 검토는 한 연구팀 내 네 역할을 순서대로 적용한 문서 검토이며, 독립된 네 명의 인간 전문가 승인이나 IRB·규제기관 결정을 뜻하지 않는다. 각 후속 reviewer는 앞선 reviewer의 쟁점과 산출물을 입력으로 검토했다.

## Reviewer A — Clinical Evidence Reviewer

### 검토 범위

- seed 문헌 8편과 HRV 방법론 문헌
- [Evidence Ledger](EVIDENCE_LEDGER.csv), [Evidence Summary](EVIDENCE_SUMMARY.md), [Clinical Questions](CLINICAL_QUESTIONS.md)
- 과장, 인과 추론, 연령·마취제·환경 일반화 여부

### 확인 결과

1. 소아 sevoflurane 유도 관찰연구들은 DS군에서 서맥 또는 더 큰 심박수 감소를 보고한다(PMID 40376277, 21109130, 20736433). 이는 해당 표본·마취법·관찰창에 대한 `VERIFIED_CLINICAL_EVIDENCE`다.
2. 이 결과를 모든 연령, 모든 마취제, 모든 수술·진정 환경으로 일반화할 근거는 없다. `LIMITED_EVIDENCE`다.
3. 최근 전향연구는 sympathetic failure와 서맥의 연관을 보고했으나(PMID 40376277), vagal excess 단일기전이나 인과를 확정하지 않는다. `VERIFIED_CLINICAL_EVIDENCE` + `LIMITED_EVIDENCE`다.
4. 작은 비마취 연구는 baroreflex/autonomic 차이를 보고했지만(PMID 16331125, 20307953), 마취 중 개인별 예측성은 입증하지 않는다. `LIMITED_EVIDENCE`다.
5. HRV 메타분석에서 resting RMSSD 차이가 보고됐으나(PMID 30005737), resting HRV 단독 위험판정은 지지되지 않는다. 초단기 SDNN·LF·HF·LF/HF는 창 길이·호흡·stationarity에 민감하다(PMID 8598068, 23431279, 21496161, 16960742, 29863781, 41946377).
6. 일부 sevoflurane 연구에서 CHD 유무와 별개인 연관이 보고됐지만(PMID 21109130, 20736433), CHD 효과가 일반적으로 배제됐다는 의미는 아니다.
7. 단일기관 후향연구의 전체 perioperative complication 2.98%(51/1,713 anesthetics)는 내부 비교군이 없어 DS의 전반적 위험상승을 입증하지 않는다(PMID 40363932).
8. atropine hypersensitivity, 구체적 마취제 감량비율, 특정 약물 우선사용은 검증 근거가 부족하여 `UNSUPPORTED_OR_REJECTED`로 남겼다.

### 판정

- `PASS`: seed 문헌을 PMID/DOI로 추적했고 상충·제한을 함께 기록함.
- `CONDITIONAL PASS`: 현재 문구는 연구근거 설명용으로 적합하나 임상 주장에는 사용 불가.
- `FAIL`: 임상 유효성, 임상 확률, 예방·치료 효과를 주장하는 모든 해석.
- `UNRESOLVED QUESTIONS`: 연령별 cutoff, 다른 마취제, 진정/수술 차이, 기전의 인과성, 기관별 baseline.
- `REQUIRED HUMAN REVIEW`: 소아마취 전문의가 endpoint·마취 단계·임상적으로 의미 있는 변화와 제외기준을 승인해야 함.

## Reviewer B — Dataset Curator

### 검토 범위

- [Dataset Registry YAML](../../research/dataset_registry.yaml)과 [CSV](../../research/dataset_registry.csv)
- [Dataset Priority Matrix](DATASET_PRIORITY_MATRIX.md), [Data Gap Map](DATA_GAP_MAP.md)
- 접근등급, 라이선스, DS 식별성, modality, 사용목적과 leakage

### 확인 결과

1. 13개 데이터셋이 동일한 30개 필드로 등록됐고 OPEN, CREDENTIAL_REQUIRED, INSTITUTIONAL을 구분했다.
2. VitalDB에서 DS 진단 라벨을 확인할 수 있다고 가정하지 않았다. INSPIRE는 현재 공개 설명상 congenital/chromosomal diagnosis가 제외되어 DS 식별을 `NO`로 기록했다.
3. MIMIC에서 Q90 코드 조회 가능성과 같은 환자의 고해상도 matched waveform 존재를 별개로 두고 DS 식별을 `UNCERTAIN`으로 기록했다.
4. ICU-수술실, 성인-소아, 건강인-환자 distribution shift를 명시했고, healthy-volunteer 자료를 outcome model 용도로 추천하지 않았다.
5. OPEN 자료도 프로젝트 역할을 제한했다. 제한자료는 credential·교육·DUA를 우회하지 않으며 병원자료는 IRB/DUA 전 접근하지 않는다.

### 판정

- `PASS`: 최소 12개, 동일 schema, 공식 URL, 접근·라이선스·용도·DS 식별성 필드를 충족함.
- `CONDITIONAL PASS`: registry는 2026-09-02 스냅샷이며 실제 사용 직전 버전·라이선스·접근조건 재검증 필요.
- `FAIL`: 서로 다른 cohort를 환자 수준에서 무근거 병합하거나 non-DS/성인 자료로 DS 소아 임상성능을 주장하는 사용.
- `UNRESOLVED QUESTIONS`: MIMIC Q90 실제 사례수와 waveform match, 각 병원의 DS 사례·파형 coverage·기기 metadata.
- `REQUIRED HUMAN REVIEW`: 데이터보호 책임자·기관 데이터관리자·라이선스 담당자가 IRB/DUA와 export 범위를 승인해야 함.

## Reviewer C — Biostatistician

### 검토 범위

- [PICOTS](PICOTS.md), [Labeling Protocol](LABELING_PROTOCOL.md), [Statistical Analysis Plan](STATISTICAL_ANALYSIS_PLAN.md)
- [Validation Roadmap](VALIDATION_ROADMAP.md), [IRB Protocol Draft](IRB_PROTOCOL_DRAFT.md)
- leakage, split, imbalance, sample size, metric·threshold 계획

### 확인 결과

1. endpoint는 candidate로 유지했고 최종 임상 판정 전 확정하지 않았다.
2. feature window, index time, prediction horizon은 parameterized protocol로 두었으며 post-index 처치·결과의 feature 유입을 금지했다.
3. 동일 환자의 반복 수술이 train/test에 분산되지 않는 patient-level split을 요구하고 temporal 및 external-site validation을 계획했다.
4. threshold는 development set에서 고정하고 test set에서 조정하지 않는다. AUROC만이 아니라 AUPRC, fixed false-alarm sensitivity, false alerts/hour, lead time, calibration, Brier, decision curve, subgroup, missingness/SQI failure를 요구했다.
5. 표본수는 확정값이 아니라 예상 사건률·목표 정밀도·cluster/반복측정·탈락 가정을 입력하는 계산식과 시나리오로 남겼다.

### 판정

- `PASS`: 데이터누출 통제, 환자단위 분할, 독립검증과 다면적 평가계획을 포함함.
- `CONDITIONAL PASS`: 사건정의·효과크기·허용 false-alert burden·목표 CI가 인간 검토 후 사전등록되어야 함.
- `FAIL`: test-set threshold tuning, 사례 단위 무작위분할, post-index treatment leakage, AUROC 단독 성공판정.
- `UNRESOLVED QUESTIONS`: 실제 사건률, usable waveform 비율, 반복수술 상관, 허용 민감도/경보부담, 다기관 heterogeneity.
- `REQUIRED HUMAN REVIEW`: 독립 생물통계가와 임상판정위원회가 SAP·표본수·결측·중지규칙을 승인해야 함.

## Reviewer D — Regulatory and Safety Reviewer

### 검토 범위

- 앞선 Reviewer A–C 결과
- [Intended Use](../regulatory/INTENDED_USE_DRAFT.md), [MFDS Questions](../regulatory/MFDS_REGULATORY_QUESTIONS.md), [FDA CDS Analysis](../regulatory/FDA_CDS_ANALYSIS.md), [Standards Map](../regulatory/STANDARDS_MAP.md)
- [Hazard Analysis](../safety/HAZARD_ANALYSIS.md), [Risk Register](../safety/RISK_REGISTER.md), [Clinical Safety Boundaries](../safety/CLINICAL_SAFETY_BOUNDARIES.md)

### 확인 결과

1. 현재 intended use는 RUO/silent shadow이며 진단·치료·투약·기기제어·임상 확률 주장을 제외한다.
2. RUO 표지만으로 규제 면제가 자동 보장된다고 쓰지 않았다.
3. FDA 2026 CDS 지침상 생체신호 패턴 분석은 520(o)(1)(E) 첫 기준을 충족하기 어려우며, 독립검토 설명만으로 비기기 CDS가 되지 않는다는 잠정 분석을 기록했다.
4. MFDS 품목·등급을 확정하지 않고 사전상담 질문과 제출 패키지를 만들었다.
5. LLM을 환자 inference에서 배제하고, 낮은 신호품질·stale·mismatch·버전불일치에서 fail-silent하도록 안전계약을 정의했다.
6. 위험통제는 설계상 요구일 뿐 아직 검증·수용되지 않았음을 명시했다.

### 판정

- `PASS`: 현재 문서 경계는 RUO/shadow 연구 준비와 내부 개발검토에 적합함.
- `CONDITIONAL PASS`: IRB/기관 정보보호 승인 및 shadow 격리 E2E 검증 후 연구를 시작할 수 있음.
- `FAIL`: 임상의 실시간 노출, 임상 경보/확률, 치료권고, 의료기기 제어, LLM inference를 현재 범위에 넣는 변경.
- `UNRESOLVED QUESTIONS`: MFDS 제품 해당성·품목·등급·임상시험 절차, FDA product code/제출경로, 적용표준 범위, 허용 잔여위험.
- `REQUIRED HUMAN REVIEW`: MFDS/FDA 규제전문가, IRB, 임상안전 책임자, 품질·보안 책임자의 공식 검토와 승인.

## 전체 결론과 릴리스 게이트

**CONDITIONAL PASS**는 문서와 데이터 거버넌스 구조가 다음 단계의 인간 검토를 받을 준비가 됐다는 뜻이다. 임상 성능, 안전성, 규제 적합성 또는 의료기기 허가를 뜻하지 않는다.

현재 허용:

- 공개 non-DS 데이터의 generic signal pipeline 시험
- 승인된 후향 DS 연구 준비
- IRB/DUA와 E2E 격리가 완료된 전향 silent validation 준비

현재 금지:

- 치료팀에 환자별 출력 노출
- 임상 유효성·예방·정확한 예측 주장
- 약물/치료/기기제어 기능
- LLM 기반 환자 inference

다음 gate는 인간 검토자가 각 `REQUIRED HUMAN REVIEW`를 서명하고, [Risk Register](../safety/RISK_REGISTER.md)의 연구단계 차단위험을 해소하며, 프로토콜을 기관 절차에 맞게 사전등록하는 것이다.
