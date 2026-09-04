# T21 Safe — Evidence-First Refocus 결정 (Founder)

**일자:** 2026-09-04 (KST)  
**문서 성격:** Founder 의사결정 · Path B / RUO / Shadow · `clinical_validation=false`  
**Eng tip (현재 HEAD):** `edff0f1` (`edff0f1abcf417729fd3029266d2c46e11b2b688`)  
**폐기 관찰 SHA:** `c6806e1` (obsolete — 이후 기록·인용 금지)

> Research Use Only. 진단·치료·투약·closed-loop·FACT 주장 없음.  
> **PROXY ≠ DS 임상 검증.** 공개 ECG fixture PASS는 Master FACT가 아니다.

---

## 1. 왜 Evidence-First로 리셋하는가

Engineering sprint tip이 `edff0f1`에 도달했다. PROXY HYP 하네스·SQI fail-reason·neg-control QA stamp 등 **엔지니어링 준비도**는 축적됐으나, 임상 의사결정(endpoint·population·bradycardia 절대/상대 임계값·windowing·SpO2/Airway·BIDMC usability·FACT elevation)은 대부분 `PI_REQUIRED` / `PI_TO_DEFINE` 상태다.

이 상태에서 tip churn·새 PROXY bench·MCP 확장·RII 튜닝을 계속하면:

1. **증거보다 tip이 앞선다** — Founder/PI가 lock하지 않은 가정 위에 코드가 쌓인다.
2. **PROXY 결과가 DS/임상처럼 읽힐 위험**이 커진다 (`PROHIBITED_CLAIMS.md`).
3. Observation tip(`c6806e1`)처럼 **구 SHA가 문서에 남는 드리프트**가 반복된다.

따라서 Founder가 unfreeze하기 전까지 **코드 tip을 멈추고**, docs/governance·clinical research lock·M0 이슈 백로그만 진행한다.

---

## 2. STOPPED (Founder unfreeze 전까지)

| 중지 항목 | 이유 |
| --- | --- |
| Tip churn / freeze tip 연속 발행 | tip이 증거가 됨을 막기 위함 |
| 신규 PROXY bench·HYP 확장 | PROXY ≠ DS; 허용 claim은 ECG HR-event/SQI 수준으로 이미 충분 |
| MCP 기능 확장·카탈로그 드리프트 유발 작업 | DX는 유지·문서화만; 새 툴/엔드포인트 금지 |
| RII weight·threshold 튜닝 (`config.py` / `deterministic_index.py`) | 임상 lock 전 ENGINEERING_DEFAULT 변경 금지 |
| FACT / clinical_validation 승격 | Path B · RUO · Shadow 유지 |
| dosing / closed-loop / alarm-like UX | 절대 금지 (`PROHIBITED_CLAIMS.md`) |

---

## 3. CONTINUES (허용)

| 계속 항목 | 산출물 |
| --- | --- |
| Docs / governance | 본 문서, freeze 선언, gates, dedup map, M0 backlog |
| Clinical Research Lock | `docs/research/CLINICAL_RESEARCH_LOCK_V0.md` — PI_REQUIRED 표 |
| Evidence roadmap (90일) | `docs/roadmap/90_DAY_EVIDENCE_ROADMAP_KR.md` — M0 우선 |
| Threshold/weight provenance (읽기 전용) | `docs/model/THRESHOLD_WEIGHT_PROVENANCE.md` — 값 변경 없음 |
| 기존 Path B demo/MCP **문서·온보딩** 유지 | 코드 tip 동결; 런북 정정만 |

---

## 4. 명시: PROXY ≠ DS clinical validation

- PROXY (MIT-BIH / Fantasia fixture 등)는 **엔진·SQI·HR-event 정의가 돌아가는지**를 보는 엔지니어링 증거다.
- `clinical_validation=false`이며 **공개 non-DS 데이터는 DS 소아·마취 성능을 대신하지 않는다**.
- Fixture PASS ≠ Master FACT. FACT elevation은 별도 PI/Founder gate (`CLINICAL_RESEARCH_LOCK_V0.md`).
- Observation SHA `c6806e1`는 obsolete. 이후 tip/문서 인용은 **현재 HEAD `edff0f1`** 또는 Founder가 지정한 freeze SHA만 사용한다.

---

## 5. Founder 다음 한 줄 (30일)

**M0:** Clinical Research Lock 표의 PI_REQUIRED 행을 PI와 회의로 options만 좁히고, tip/코드 값은 건드리지 않는다.
