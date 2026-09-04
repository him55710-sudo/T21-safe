# 첫 연구 프로토콜 스텁 (KR)

**상태:** STUB · Path B · RUO · Shadow Mode
**목적:** **실현 가능성(feasibility)** · 자료 품질·재현성 — **예측·진단·처치 권고 아님**
**임상 임계값:** 전부 `PI_TO_DEFINE`

> 임상 연구 결정의 canonical source는 [`CLINICAL_RESEARCH_LOCK_V0.md`](CLINICAL_RESEARCH_LOCK_V0.md)다. 이 문서는 해당 결정이 승인·반영되기 전까지 `STUB`이다.

---

## 한 문장

다운증후군(T21) 환자의 마취·진정 **과거 생체신호**를 병원 로컬에서 정렬·품질 확인·연구 export하는 **관찰·연구** 절차의 초안이다.

## 하는 일 / 하지 않는 일

| 함 | 안 함 |
| --- | --- |
| 시계 정렬, SQI, 누락/잡음 보고 | 서맥·저혈압·심정지 **예측** |
| 단계(phase) 타임라인 연구 기록 | 투약·용량·시술 **권고** |
| 로컬 non-PHI 연구 export | 펌프/EMR **제어**, 클라우드 PHI |

## PI_TO_DEFINE

- [ ] 포함/제외 기준 (연령, 시술, DS 확인 방식)
- [ ] 일차·이차 **실현가능성** 지표 (예측 성능 지표 금지)
- [ ] IRB / 동의 / waiver 경로
- [ ] 비교군 필요 여부

## 공개 데이터와의 관계

공개 non-DS 벤치(BIDMC 등)는 **엔진 PROXY 스모크**일 뿐이며, 본 프로토콜의 DS 임상 검증을 대체하지 않는다 (`clinical_validation=false`).

## 참고

- `docs/research/IRB_PROTOCOL_DRAFT.md`, `PICOTS.md`, `HOSPITAL_DATA_REQUEST_SPEC.md`
- `docs/business/HOSPITAL_POC_ONEPAGER.md`
