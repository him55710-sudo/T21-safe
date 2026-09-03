# ExportManifest PHI-false 파트너 스토리 (KR)

> Freeze cross-link: hospital-demo `v2.0-hospital-demo-ready` · PROXY Analysis Plan `v2.1-proxy-hyp-benches` ([`PROXY_HYP_RESULTS_KR.md`](PROXY_HYP_RESULTS_KR.md); Auditor DUAL-GATE / CODEX-111; `clinical_validation=false`; **no FACT**).


**Status:** Path B / RUO / Shadow  
**clinical_validation:** `false`  
**대상:** 병원 IT·연구 파트너에게 “로컬 export에 PHI가 없다”를 한 장으로 설명  
**금지:** 임상 모니터 claim · 투약/알림 · 클라우드 PHI · VitalDB 등 미포함 데이터셋

영문 1페이지: [`docs/business/export-manifest-phi-false-1p.md`](../business/export-manifest-phi-false-1p.md)  
데모 온보딩: [`HOSPITAL_DEMO_ONBOARDING_KR.md`](HOSPITAL_DEMO_ONBOARDING_KR.md)

미팅 talk track: [`MEETING_ONEPAGER_PROXY_v0.1_KR.md`](MEETING_ONEPAGER_PROXY_v0.1_KR.md) — freeze `v2.3-meeting-onepager`; PROXY v0.1 · ECG HR-event/SQI only · `clinical_validation=false` · **no FACT**.

---

## 한 줄 요약

원커맨드 hospital demo가 만드는 `shadow-capture.jsonl` **마지막 줄**은 `export-manifest/1.0`이며, 스키마상 **`includes_phi`는 항상 false**입니다. 파형·PHI·클라우드 URI 쓰기는 fail-closed입니다.

```bash
bash scripts/run_hospital_demo.sh /tmp/t21-hospital-demo
```

## 파트너에게 보여줄 체크

1. 리포트 JSON: `contains_phi=false`, `clinical_validation=false`, `synthetic_only=true`  
2. ExportManifest: `includes_phi=false`, `includes_waveforms=false`  
3. 저장 위치: 로컬 디렉터리만 (예: `/tmp/t21-hospital-demo`)  
4. 컨트롤 플래그: dosing / closed_loop / EMR write **off**  
5. PROXY 공개 벤치는 **별 라벨(PROXY)** — 이 매니페스트 데모의 필수 입력이 아님  

## 근거 파일

| 구분 | 경로 |
| --- | --- |
| 스키마 | `contracts/export-manifest.schema.json` (`includes_phi` const false) |
| 빌더 | `services/engine/src/t21_engine/streaming/export_manifest.py` |
| 배포 체크리스트 | `docs/security/HOSPITAL_DEPLOYMENT_CHECKLIST.md` |

VitalDB · CapnoBase · PulseDB · MIMIC · 병원 PHI **미포함**.
