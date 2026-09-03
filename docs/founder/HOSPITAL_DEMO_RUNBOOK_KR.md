# Hospital Demo 런북 (KR)

**Status:** Path B / RUO / Shadow · hospital-demo freeze tip `v2.0-hospital-demo-ready`  
**Also see:** PROXY Analysis Plan freeze tip `v2.1-proxy-hyp-benches` + Auditor DUAL-GATE wording (CODEX-111)  
**clinical_validation:** `false`  
**목적:** Founder/파트너 앞에서 **브라우저 카드까지** 한 번에 보여 주는 실행 순서  
**금지:** PHI · 파형 · VitalDB/CapnoBase/PulseDB · 투약/알림/closed-loop · 임상 claim · Kim/PI 메일 대행 · Airway/BIDMC를 hospital-demo에 끼워 넣기

관련: [`HOSPITAL_DEMO_ONBOARDING_KR.md`](HOSPITAL_DEMO_ONBOARDING_KR.md) · [`EXPORT_MANIFEST_PHI_FALSE_KR.md`](EXPORT_MANIFEST_PHI_FALSE_KR.md) · [`PROXY_HYP_RESULTS_KR.md`](PROXY_HYP_RESULTS_KR.md) (Auditor: HYP-01 PARTIALLY_SUPPORTED; HYP-03/07 STRETCH/neg-control-QA; **no FACT**)

미팅 talk track: [`MEETING_ONEPAGER_PROXY_v0.1_KR.md`](MEETING_ONEPAGER_PROXY_v0.1_KR.md) — freeze `v2.3-meeting-onepager`; PROXY v0.1 · ECG HR-event/SQI only · `clinical_validation=false` · **no FACT**.

---

## 원커맨드 체인 (권장)

```bash
make hospital-demo
# 동일: bash scripts/run_hospital_demo_chain.sh /tmp/t21-hospital-demo /tmp/t21-hospital-demo-partner-pack
```

팩만 다시 만들 때:

```bash
make hospital-demo-pack
```

순서:

1. `scripts/run_hospital_demo.sh` — synthetic hospital demo + ExportManifest 게이트  
2. `scripts/generate_hospital_demo_showcard_html.py` — 브라우저용 HTML show-card  
3. `scripts/pack_hospital_demo_partner.sh` — 파트너 zip (shadow JSONL/파형 **미포함**)

열기:

```bash
# macOS
open /tmp/t21-hospital-demo/showcard.html
# Linux
xdg-open /tmp/t21-hospital-demo/showcard.html
```

---

## 산출물 체크

| 경로 | 확인 |
| --- | --- |
| `hospital-demo-report.json` | `clinical_validation=false`, `contains_phi=false` |
| `showcard.html` | 브라우저에서 게이트 표 + QC (이미지/파형 없음) |
| `t21-hospital-demo-partner-pack.zip` | 리포트·docs·showcard (EN/KR 1페이지) |

PROXY 공개 벤치(BIDMC/MIT-BIH/Fantasia)는 **별도 PROXY 라벨** — 이 체인 필수 입력 아님.

---


## 파트너 zip에 들어가는 문서

`scripts/pack_hospital_demo_partner.sh`는 존재할 때만 복사합니다.

- `export-manifest-phi-false-1p.md`
- `research-node-one-pager.md`
- `research-overview-2p.md`
- `safety-local-first-1p.md`
- `HOSPITAL_POC_ONEPAGER.md` (있으면)
- HTML show-card (`showcard.html`) — 브라우저에서 열고 **인쇄** 가능 (CODEX-096)

shadow JSONL · 파형 · PHI는 zip에 **넣지 않습니다**.

## 단계별 (디버그)

```bash
bash scripts/run_hospital_demo.sh /tmp/t21-hospital-demo
python3 scripts/generate_hospital_demo_showcard_html.py \
  /tmp/t21-hospital-demo/hospital-demo-report.json \
  -o /tmp/t21-hospital-demo/showcard.html
bash scripts/pack_hospital_demo_partner.sh /tmp/t21-hospital-demo
```

예시 HTML: [`hospital-demo-showcard.example.html`](hospital-demo-showcard.example.html)
