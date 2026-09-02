# Competitor and Reference-Monitor Patterns

문서 상태: 공식 제조사 자료 기반 UX/reference study<br>
마지막 검토일: 2026-09-02<br>
분류: 모든 제품 사양은 `VERIFIED_OFFICIAL_INFORMATION`; 제조사 성능·효과 문구는 독립 임상 검증으로 간주하지 않음

## 시장 framing

“경쟁사가 없다”는 표현은 사용하지 않는다. 2026-09-02 현재 검토한 공식 자료에서 **DS-specific direct competitor는 확인되지 않았지만**, 범용 hemodynamic prediction, PK/PD decision support, processed EEG, nociception/autonomic monitoring 제품은 명확한 간접 경쟁·reference 군이다. 지역별 허가, indication, model/firmware는 변할 수 있으므로 구매·규제 판단 전 최신 IFU를 다시 확인한다.

## 1. Edwards/BD Acumen Hypotension Prediction Index (HPI)

- **분류:** 범용 predictive hemodynamic monitoring / 간접 경쟁.
- **Input:** Acumen IQ arterial-line sensor 또는 compatible finger cuff가 제공하는 동맥압 waveform과 hemodynamic parameters.
- **Output:** 0–100 HPI parameter; 높은 값은 hypotensive event 쪽으로 trend할 가능성이 높음을 뜻한다고 제조사가 설명한다. secondary screen은 MAP, CO/CI, SVR, PR, SV, SVV/PPV, dP/dt, dynamic arterial elastance 등을 preload/contractility/afterload 관계로 구성한다.
- **Update cadence:** 공식 제품 페이지는 HPI와 advanced parameter를 **20초마다** 갱신한다고 설명한다.
- **Visualization hierarchy:** 큰 단일 index → color/alert state → 원인 탐색용 relationship view → 개별 hemodynamic trend.
- **Alert design:** 공식 Edwards 페이지는 HPI >85가 두 번 연속 20초 update되거나 100이면 high-alert popup을 설명한다. 이는 해당 제품의 proprietary/configured rule이며 T21 Safe에 복제하지 않는다.
- **Explainability:** potential contributor를 preload, contractility, afterload로 그룹화해 drill-down한다. 인과 원인을 확정하는 것은 아니다.
- **Hardware dependency:** HemoSphere/Alta 계열 monitor와 Acumen sensor/cuff ecosystem.
- **Intended population:** 공식 BD setup 자료는 advanced hemodynamic monitoring을 받는 surgical 및 non-surgical patients를 명시한다. 정확한 지역/연령 indication은 현행 IFU 확인이 필요하다.
- **Limitations:** arterial/finger pressure quality와 hardware에 의존; proprietary algorithm; target event 정의·population shift·intervention study design을 분리해 봐야 한다.
- **참고할 UX pattern:** score보다 먼저 signal/source 상태를 명확히 하고, 큰 요약값 뒤에 구성요소와 raw trend를 단계적으로 제공.
- **복제 금지:** HPI 명칭, 0–100 의미, 85/100 alert rule, “몇 분 전 예측”, preload/afterload/contractility 원인 주장과 제조사 정확도/효과 claim.
- **공식 자료:** [BD Acumen HPI product page](https://www.bd.com/en-uk/products-and-solutions/products/product-families/acumen-hpi-software), [Edwards HPI product description](https://www.edwards.com/gb/healthcare-professionals/products-services/predictive-monitoring/hpi), [BD setup guide](https://academy.bd.com/en-us/document/236/Acumen-Hypotension-Prediction-Index-HPI-Software-Setup-Guide).

## 2. Dräger SmartPilot View

- **분류:** anesthesia drug PK/PD decision support / 기능적으로 인접하지만 T21 Safe Path B와 의도적으로 다른 범위.
- **Input:** anesthesia workstation/infusion system의 intravenous 및 volatile anesthetic drug administration, 환자 demographics와 optional vital/BIS context.
- **Output:** population PK/PD model 기반 current anesthesia level, hypnotic–analgesic balance, NSRI, effect-site concentration trends, wake-up estimate와 “what-if” preview.
- **Update cadence/horizon:** 공식 자료는 과거 40분, 현재, 미래 **20분**의 calculated concentration/level display를 설명한다. 정확한 numerical refresh interval은 공개 product sheet에서 확인되지 않아 현행 IFU 확인이 필요하다.
- **Visualization hierarchy:** 2D interaction/isobole map → current point/history → forward trajectory → drug-specific concentration/trend.
- **Alert design:** 전통 alarm보다 advisory visualization/forecast 중심. 실제 configuration은 software/IFU에 의존한다.
- **Explainability:** 약물별 effect-site concentration과 population model 상 interaction을 보여주지만 patient-specific true drug effect의 직접 측정은 아니다.
- **Hardware dependency:** compatible Dräger anesthesia device, pumps/interfaces, workstation/software.
- **Intended population:** SmartPilot View SW 3.12.n IFU는 trained OR personnel과 **adult only**, 18–90세, 150–200 cm, 40–140 kg의 model demographic range를 명시한다.
- **Limitations:** population-model 범위, 데이터 입력 정확성, supported drug/device에 의존. 특정 환자의 pharmacodynamics를 직접 측정하지 않는다.
- **참고할 UX pattern:** 현재 상태와 과거/미래를 분리하고, model-derived 값과 observed vital을 시각적으로 구분.
- **복제 금지:** NSRI, isobole design, proprietary PK/PD model, effect-site/what-if dosing, wake-up estimate, 약물 최적화 claim. T21 Safe는 dose simulation 자체를 금지한다.
- **공식 자료:** [Dräger SmartPilot View product information](https://www.draeger.com/Content/Documents/Products/SmartPilot-View-pi-102079-en-MASTER.pdf), [SmartPilot View SW 3.12.n IFU](https://www.draeger.com/Content/Documents/Products/smart312-ifu-9511248-en.pdf).

## 3. Medtronic BIS

- **분류:** processed EEG brain monitoring / 간접 경쟁·UI reference.
- **Input:** forehead sensor가 수집하는 frontal raw EEG; bilateral sensor/system에 따라 channel 구성.
- **Output:** BIS index 0–100, raw EEG, EMG, Signal Quality Index(SQI), suppression ratio/time, median frequency, spectral edge frequency, DSA(software/configuration에 따라).
- **Update cadence:** 공식 product guide는 결과가 continuously calculated/displayed된다고 설명하지만 정확한 refresh seconds는 public page에서 확인되지 않았다.
- **Visualization hierarchy:** 큰 BIS numeric → SQI/EMG와 alarm range → suppression/frequency metrics → raw EEG/trend/DSA.
- **Alert design:** user-programmed alarm range를 index와 함께 표시할 수 있다.
- **Explainability:** raw EEG 및 SQI/EMG/suppression을 함께 보여 index가 artifact 또는 burst suppression과 겹치는지 검토 가능하다. algorithm 자체는 proprietary다.
- **Hardware dependency:** BIS monitor/module, patient interface cable, single-use sensor.
- **Intended population:** anesthetic effect/brain state monitoring. 정확한 성인·소아/setting별 indication은 jurisdiction-specific current IFU 확인이 필요하다.
- **Limitations:** sensor contact, EMG/artifact, drug/age/neurologic context, proprietary processing의 영향을 받는다; MRI/환경 등 hardware warnings는 IFU를 따른다.
- **참고할 UX pattern:** primary index 옆에 SQI와 raw source를 같은 hierarchy에 두고, 계산 불가/저품질을 숫자 대신 명확히 표시.
- **복제 금지:** BIS 상표/index, numeric target ranges, proprietary EEG algorithm, dosing/outcome marketing claim.
- **공식 자료:** [Medtronic BIS Advance monitor](https://www.medtronic.com/en-us/healthcare-professionals/products/patient-monitoring/brain-monitoring/brain-channel-monitoring/bis-advance-monitor.html), [BIS monitoring system](https://www.medtronic.com/en-us/healthcare-professionals/products/patient-monitoring/brain-monitoring/brain-channel-monitoring/bis-monitoring-system.html).

## 4. Masimo SedLine

- **분류:** bilateral processed EEG brain function monitoring / 간접 경쟁·UI reference.
- **Input:** 네 채널 frontal/prefrontal EEG를 adult/pediatric SedLine sensor로 획득.
- **Output:** enhanced Patient State Index(PSi), four raw EEG waveforms, left/right DSA 또는 Multitaper DSA, spectral edge/burst-suppression 관련 display와 signal context.
- **Update cadence:** 공식 quick-reference 자료에서 정확한 seconds cadence는 확인되지 않았다. insufficient EEG면 PSi 숫자 대신 `--`를 표시한다.
- **Visualization hierarchy:** PSi numeric/trend → color-coded configurable limits → bilateral DSA → four raw EEG channels.
- **Alert design:** user-configurable lower/upper limits와 trend 색상; signal insufficiency를 missing numeric으로 표현.
- **Explainability:** bilateral symmetry/spectral view와 raw channels가 processed PSi를 보완한다. PSi 계산은 proprietary processing이다.
- **Hardware dependency:** SedLine module/sensor와 Masimo Root platform; O3 등 다른 module과 통합 가능.
- **Intended population:** anesthesia 중 brain monitoring; pediatric application/sensor가 공식 자료에 있으나 지역별 indication은 최신 manual 확인 필요.
- **Limitations:** EEG/EMG artifact, sensor, age/drug/neurologic condition; public product claim을 독립 검증으로 간주하지 않는다.
- **참고할 UX pattern:** 계산 불가 시 마지막 값을 유지하지 않고 `--`; bilateral/raw/spectral data로 drill-down.
- **복제 금지:** PSi, DSA proprietary rendering/algorithm, target ranges, anesthetic delivery/outcome claim.
- **공식 자료:** [Masimo SedLine product page](https://professional.masimo.com/products/continuous/root/root-sedline/), [SedLine quick-reference guide](https://professional.masimo.com/siteassets/us/documents/pdf/plm-10355c_quick_reference_guide_sedline_english.pdf), [SedLine manuals index](https://techdocs.masimo.com/products/device/sedline-module-and-patient-cable-kit/).

## 5. Medasense NOL PMD-200

- **분류:** multimodal nociception/pain-response monitoring / 간접 경쟁·multimodal UX reference.
- **Input:** finger probe PPG, skin temperature, 3-axis accelerometer, bio-impedance galvanic skin response; derived physiological parameters.
- **Output:** proprietary nonlinear NOL index 0–100, trend, raw input signal panes, signal-quality alerts와 event annotations.
- **Update cadence:** “continuous” index/trend를 제공한다. public user manual에서 exact numeric refresh interval은 확인되지 않았다. patient calibration은 최대 30초가 걸릴 수 있고, movement 시 index를 30초 freeze하는 상황이 설명되어 있다.
- **Visualization hierarchy:** signal/status bar → NOL numeric/color bar → continuous trend/threshold → raw PPG/GSR/temperature/movement → event annotation/review.
- **Alert design:** low signal quality면 index를 사용하지 말라는 alert를 표시하고 계산 불가가 30초보다 길면 숫자를 숨기고 trend를 중단한다. user-defined threshold와 visual notification이 있다.
- **Explainability:** raw signal/quality, event annotation, trend를 함께 제공하지만 index algorithm은 proprietary다.
- **Hardware dependency:** PMD-200 monitor, reusable finger probe, single-use GSR sensor; selected Philips/Mindray integration.
- **Intended population:** 의료시술·마취·수술·회복 등에서 pain-level change assessment의 adjunct로 공식 manual이 설명한다. trained licensed practitioner supervision을 요구한다.
- **Limitations:** severe arrhythmia, CPR/cardioversion 등의 contraindication, movement/low perfusion/electrocautery/hypothermia/sensor interference, autonomic/volemic confounding이 IFU에 있다.
- **참고할 UX pattern:** 초기 calibration, quality failure 시 숫자 제거, raw input 확인, event timeline annotation.
- **복제 금지:** NOL 명칭/0–100 의미, threshold/color rule, analgesic guidance, proprietary sensor fusion/algorithm 및 제조사 outcome claim.
- **공식 자료:** [PMD-200 product page](https://medasense.com/pmd-200/), [PMD-200 EU user manual revision 4](https://medasense.com/wp-content/uploads/EU-User-Manual-2.2.1-MK2U-02-378-Medasense-PMD-200.pdf).

## 6. ANI-family monitor

- **분류:** ECG/RR-based parasympathetic/analgesia-nociception monitoring / 간접 경쟁·HRV caution reference.
- **Input:** ECG-derived normal non-ectopic R-R intervals와 respiratory pattern component.
- **Output:** ANI 0–100, instantaneous/mean trends와 normalized RR-series display. 제조사는 relative parasympathetic tone/anticipated hemodynamic reactivity와 연결해 설명한다.
- **Update cadence/window:** ANI Monitor V2 manual은 각 ANI가 **64초 window**, ANIi가 이전 **120초 평균**, ANIm이 이전 **240초 평균**이라고 설명한다.
- **Visualization hierarchy:** ANI numeric(s) → RR/respiratory-pattern visual → trend/quality/context.
- **Alert design:** 제품/manual version별 threshold interpretation이 있으나 T21 Safe에 복제하지 않는다.
- **Explainability:** normalized/filtered RR series와 window를 보여주지만 ANI calculation은 proprietary이며 ECG cardiac monitor가 아니라고 manual이 경고한다.
- **Hardware dependency:** dedicated ANI monitor/electrodes 또는 compatible integration.
- **Intended population:** 정확한 현행 지역·연령 indication은 최신 IFU에서 확인해야 한다.
- **Limitations:** ectopy/arrhythmia, respiration/ventilation, autonomic-active drug와 nonstationarity의 영향을 받는다. LF/HF 또는 HRV를 직접 교감/부교감 계량기로 단순화할 수 없다.
- **참고할 UX pattern:** 산출 window와 smoothing horizon을 명시하고 instantaneous/slow trend를 구분.
- **복제 금지:** ANI/ANIi/ANIm, parasympathetic-tone claim, threshold/analgesic guidance, proprietary RR transform/algorithm.
- **공식 자료:** [ANI Monitor V2 user manual](https://www.mdoloris.com/wp-content/uploads/2024/06/ANI-MONITOR-V2-User-Manual-V10-EN.pdf).

## Cross-product UX patterns — 채택 가능 원칙

| Pattern | T21 Safe 적용 방식 |
| --- | --- |
| 요약 → trend → source detail | RII를 첫 화면의 결론으로 두지 않고 SQI, component, raw trend로 drill-down |
| 품질과 값의 동시 표시 | quality 실패 시 score를 숨기고 reason code 표시; stale value 금지 |
| 현재/과거/예측 분리 | observed data, derived feature, research horizon, post-hoc label을 lane/color로 분리 |
| 초기 calibration | baseline quality·duration을 표시하고 불충분 시 unavailable |
| event annotation | medication/stimulus/airway를 model cause가 아닌 별도 timeline lane으로 기록 |
| configurable view | 연구 replay scale만 변경; 임상 threshold를 임의 설정하는 기능은 Path B에서 금지 |
| provenance | device/source/algorithm/version/window를 export와 화면 metadata에 노출 |

## T21 Safe가 의도적으로 하지 않는 것

- HPI처럼 clinical prediction/alert를 주장하지 않는다.
- SmartPilot처럼 약물 effect-site/what-if/dosing을 계산하지 않는다.
- BIS/PSi/NOL/ANI처럼 proprietary clinical index의 의미 또는 target range를 재사용하지 않는다.
- 경쟁 제품 UI를 pixel/색/명칭/threshold 수준으로 복제하지 않는다.
- 제조사 마케팅 수치나 효과 문구를 T21 Safe 임상 근거로 전이하지 않는다.

## 확인 필요

- 각 제품의 한국 허가상 intended use와 현재 모델/소프트웨어 version
- pediatric/DS subpopulation validation과 contraindication
- exact update cadence가 public source에 없는 제품의 최신 IFU
- patent/trademark/FTO 검토
- DS-specific direct competitor의 지속적 landscape scan
