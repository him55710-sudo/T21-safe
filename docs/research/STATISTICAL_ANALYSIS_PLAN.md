# Statistical Analysis Plan (SAP)

문서 상태: Protocol draft — final endpoint/threshold pending clinician review<br>
SAP version: `0.1.0`<br>
마지막 검토일: 2026-09-02

## 1. 목적

이 SAP는 Phase 0 기술 검증, Phase 1 DS 후향 characterization, Phase 2 matched comparison, Phase 3 prospective silent validation의 분석 원칙을 사전 정의한다. 임상 효능, 치료 효과, 투약 최적화 또는 사고 예방을 검정하지 않는다.

## 2. Analysis sets

- **Technical set:** 공개 bounded sample 중 ingestion 계약을 충족하는 모든 record. 실패 record도 제외하지 않고 실패율 분모에 포함한다.
- **Eligible clinical set:** IRB eligibility와 데이터 linkage를 충족한 모든 연속 사례.
- **Signal-evaluable set:** 대상 phase/window의 필수 signal과 SQI를 충족한 사례. eligible set 대비 누락률을 함께 보고한다.
- **Adjudicated-event set:** blinded adjudication에서 PRESENT/ABSENT로 결정된 사례/시간. UNCERTAIN과 NOT_ASSESSABLE은 별도 표로 유지한다.
- **Frozen prospective set:** model/threshold freeze 이후 순차 등록된 eligible 사례. 개발 데이터로 되돌리지 않는다.

Primary 결과는 eligible set와 evaluable set의 선택 차이를 함께 보여야 한다.

## 3. Unit, clustering, split

- 독립 단위는 patient다. case와 window는 patient 내 반복 측정이다.
- 같은 환자의 여러 수술/시술은 train, validation, test 중 하나에만 속한다.
- 개발에서는 가능하면 temporal split을 사용하고, 최종적으로 외부 site validation을 수행한다.
- threshold tuning, calibration refit, feature selection은 test/external set에서 하지 않는다.
- resampling/bootstrapping은 patient cluster 단위로 수행한다.
- site가 여러 개면 leave-one-site-out internal-external validation을 우선 검토한다.

## 4. 후보 estimand

### Phase 1

- 단계별 baseline 대비 continuous trajectory의 환자 수준 분포.
- 후보 event 전후의 event-aligned mean/median trajectory와 uncertainty.
- signal-quality/missingness가 환자·단계·장비에 따라 달라지는 정도.

### Phase 2

- DS와 matched non-DS control 간 후보 event의 adjusted risk difference 및 risk ratio.
- baseline 대비 trajectory의 group-by-time contrast.
- CHD, 연령층, procedure family, anesthesia/sedation context의 effect modification.

관찰연구이므로 추정치는 association이며 치료 또는 DS의 순수 인과효과로 명명하지 않는다.

### Phase 3

- frozen RII/model의 adjudicated event discrimination, calibration, alarm burden proxy와 lead time.
- signal-quality gate가 작동하지 않는 비율과 subgroup별 failure.

## 5. Baseline과 window

- baseline 후보는 대상 단계 전 안정된 artifact-free 구간의 median과 robust scale이다.
- 목표 5분 및 30/60/120/300초 feature window는 `PRODUCT_ASSUMPTION`이며 feature별 validity review 후 protocol에 고정한다.
- RMSSD/SD1, SDNN, LF/HF 등은 동일한 최소 RR count를 공유하지 않는다. metric-specific availability flag를 사용한다.
- 모든 transformation, filters, resampling, ectopy handling과 minimum usable fraction을 코드/manifest version으로 고정한다.
- future-aware centered filters 또는 양방향 interpolation은 prospective feature 계산에 금지한다.

## 6. Descriptive analysis

- 환자 수, 사례 수, 관찰 시간, event 수를 모두 보고한다.
- continuous 변수는 분포에 따라 mean/SD와 median/IQR을 함께 제시한다.
- categorical 변수는 n/N과 비율을 제시한다.
- missingness는 변수·site·device·phase·group별로 보고한다.
- DS/control balance는 standardized mean difference와 overlap plot으로 평가하며 p-value만으로 balance를 판단하지 않는다.
- 반복 시술, waveform availability, exclusion flow를 투명하게 표시한다.

## 7. Comparative models

- binary event: 사전 정의 confounder를 포함한 log-binomial/Poisson robust model 또는 logistic model. estimand에 맞게 risk ratio/difference 또는 odds ratio를 명확히 구분한다.
- repeated case/window: patient random intercept 또는 cluster-robust standard error. site 수가 적으면 small-sample correction/기술통계를 사용한다.
- continuous trajectory: spline time term을 포함한 mixed-effects/GEE 후보. knot와 degrees of freedom은 결과 확인 전 고정한다.
- matching/weighting: propensity score를 결과를 보지 않고 설계하며 caliper/ratio/estimand(ATT/ATE)를 사전 고정한다. positivity 부족 시 해당 비교를 중단한다.
- CHD는 제거 요인이 아니라 prespecified confounder/subgroup이다.

## 8. Prediction model development

- 첫 모델은 transparent penalized logistic/discrete-time model 또는 명시적 deterministic score를 우선한다.
- 복잡한 ML은 sample size와 external performance가 정당화할 때 challenger로만 검토한다.
- 후보 parameter 수는 basis expansion과 interaction의 모든 자유도를 센다.
- feature selection, imputation, scaling, calibration은 각 training fold 안에서 수행한다.
- RII는 임상적으로 검증된 확률로 표시하지 않는다. 확률 calibration 주장은 별도 prospective 검증과 intended-use 변경이 필요하다.
- LLM은 feature 생성, 실시간 inference, threshold 변경 또는 patient-specific output에 사용하지 않는다.

## 9. Performance metrics

모든 point estimate에는 patient-cluster를 보존한 95% confidence interval을 제시한다.

- AUROC
- AUPRC와 event prevalence reference
- 사전 고정 false-alarm rate에서 sensitivity
- 시간당 false alarms 및 case당 false alarm episodes
- median/IQR lead time; 감지하지 못한 event 비율 포함
- calibration intercept와 slope
- calibration plot와 flexible calibration curve
- Brier score 및 가능하면 scaled Brier score
- decision curve analysis — 단, 임상 threshold probability가 정당화되지 않으면 exploratory로 명시
- subgroup performance와 CI
- missingness 및 SQI failure rate

alarm episode는 연속 score exceedance의 병합/refractory 규칙을 포함해 사전 정의한다. window 수를 분모로 사용한 false-positive rate가 실제 시간당 부담을 숨기지 않게 한다.

## 10. Class imbalance

- random undersampling으로 prevalence를 왜곡한 test 성능을 보고하지 않는다.
- training weighting/oversampling을 쓰면 fold 내부에서만 적용하고 원 prevalence에서 calibration을 재평가한다.
- AUPRC를 prevalence와 함께 보고한다.
- rare subgroup의 점추정만 강조하지 않고 CI와 사례 수를 표시한다.

## 11. Missing data와 signal quality

- 결측 원인(미측정, 장비 미연결, artifact, linkage failure, 임상 선택)을 구분한다.
- outcome/DS status를 추정해 채우지 않는다.
- 임상 공변량 multiple imputation은 outcome과 clustering을 포함한 적절한 model로 training/development 내 수행하고 complete-case sensitivity analysis와 비교한다.
- raw waveform 결측을 긴 보간으로 가짜 생리 신호로 만들지 않는다.
- SQI gate failure 자체를 secondary operational outcome으로 분석한다.

## 12. Leakage audit

각 feature에 `available_at`, `source_clock`, `lookback_start`, `lookback_end`, `uses_future`, `label_dependency` 메타데이터를 둔다. 다음은 금지한다.

- prediction time 이후 signal/record
- event 후 medication/airway/PACU 정보
- discharge diagnosis 또는 retrospective coding을 실시간 predictor로 사용
- 동일 환자/인접 overlapping window의 split 간 분산
- 전 데이터로 수행한 imputation/scaling/feature selection
- test set을 보고 정한 threshold

## 13. Sample size framework

고정된 단일 표본 수를 선언하지 않는다. 임상의가 endpoint, prevalence, 허용 정밀도, 후보 parameter 수를 승인한 뒤 다음 중 가장 큰 요구량을 사용한다.

### 13.1 사건률 정밀도

예상 event proportion을 `π`, 양측 신뢰수준의 정규 분위수를 `z`, 허용 half-width를 `d`라 하면 초기 근사는 다음과 같다.

`N_prevalence = z² × π(1−π) / d²`

희귀 사건과 작은 표본에서는 exact/score interval 또는 simulation으로 확인한다.

### 13.2 Sensitivity 정밀도

목표 sensitivity를 `Se`, event 수 기준 허용 half-width를 `d_Se`라 하면 필요한 event 수의 초기 근사는:

`E_sensitivity = z² × Se(1−Se) / d_Se²`

총 사례 수는 `N ≈ E_sensitivity / π`이며 dropout, unevaluable waveform, clustering을 추가한다. 가정 범위를 여러 scenario로 표로 제시한다.

### 13.3 Model development

단순 “10 events per variable”을 확정 규칙으로 쓰지 않는다. Riley 등의 접근(PMID 32188600; DOI `10.1136/bmj.m441`)에 따라 다음을 사전 지정하고 `pmsampsize` 또는 재현 가능한 식/코드로 계산한다.

- target population event proportion `π`
- 모든 basis/interaction을 포함한 candidate parameter 수 `P`
- 보수적인 예상 Cox-Snell `R²`
- 목표 global shrinkage(후보 0.90 이상)
- apparent/adjusted Nagelkerke `R²` 차이의 허용 optimism(후보 0.05 이하)
- overall risk/intercept 정밀도

이는 방법론적 후보값이며 최종 설계값은 biostatistician이 승인한다.

### 13.4 External validation

전체 N이 아니라 event/non-event 수, calibration intercept/slope와 target metric의 CI 폭을 simulation한다. site clustering, multiple cases per patient, expected SQI failure와 consent/record loss를 반영한다.

### 13.5 Feasibility stop

예상 accrual로 사전 정한 precision을 달성할 수 없으면 model 개발을 강행하지 않고 characterization/feasibility study로 축소한다. 이 축소는 임상 성능 주장을 약화하는 것이 아니라 잘못된 모델 개발을 중단하는 안전 gate다.

## 14. Subgroup analysis

후보 subgroup은 pediatric/adult, age bands, CHD, OSA/airway risk, procedure family, anesthesia vs sedation, site, monitor type, invasive vs noninvasive BP다. 각 subgroup 정의는 결과를 보기 전 고정한다. interaction CI를 우선하고 다중 비교와 낮은 검정력을 명시한다.

## 15. Sensitivity analysis

- alternative clinically approved event definitions
- invasive BP only vs mixed BP source
- high-SQI only vs all evaluable
- first case per patient vs all clustered cases
- complete case vs multiple imputation
- exclusion of prophylactic intervention labels
- different clock-alignment tolerance
- intended metric-specific window lengths
- adjudication UNCERTAIN을 negative/positive로 두는 bounds analysis

## 16. Multiplicity와 reporting

하나의 primary endpoint/primary horizon은 clinician review 후 지정한다. 나머지는 secondary/exploratory로 구분하고 false discovery 또는 family-wise strategy를 필요에 따라 지정한다. 선택적 성능 보고를 금지하며 모든 frozen model run과 실패를 model registry에 남긴다.

보고는 TRIPOD 계열 원칙과 prediction-model risk-of-bias 점검(PROBAST; DOI `10.7326/M18-1376`)을 따른다. 개발과 external validation을 같은 결과로 합치지 않는다.

## 17. Stop criteria

- DS status 또는 outcome을 신뢰성 있게 확인할 수 없음
- signal/linkage/SQI failure로 유효 표본이 사전 기준 미달
- leakage-free timeline 재구성이 불가능
- subgroup에서 심각한 성능 불균형 또는 calibration failure
- false alarms/hour가 사전 human-factors 허용 범위를 초과
- frozen prospective 성능이 pre-specified futility gate 미달
- protocol deviation 또는 보안/프라이버시 incident

수치 gate는 Phase 3 protocol과 regulatory/human-factors review 후 고정한다.
