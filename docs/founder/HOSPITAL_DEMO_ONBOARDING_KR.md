# Founder용 Hospital Demo 온보딩 (KR)

**Status:** Path B / RUO / Shadow  
**clinical_validation:** `false`  
**목적:** 파트너·내부 데모용 **원커맨드 synthetic hospital** 실행과 리포트 읽기  
**금지:** 환자 PHI · VitalDB/CapnoBase/PulseDB · 투약/알림/closed-loop · 임상 claim

영문 상세: [`docs/DEMO.md`](../DEMO.md)  
체크리스트: [`RESEARCH_NODE_DEMO_CHECKLIST_KR.md`](RESEARCH_NODE_DEMO_CHECKLIST_KR.md)

---

## 1분 실행

레포 루트에서:

```bash
bash scripts/run_hospital_demo.sh /tmp/t21-hospital-demo
```

성공 시 터미널에 `HOSPITAL DEMO PASS`와 함께 다음이 찍힙니다.

- `clinical_validation=false`
- `includes_phi=false` / `contains_phi=false`
- `synthetic_only`
- 로컬 `shadow-capture.jsonl` + `export-manifest/1.0` 마지막 줄

산출물:

| 파일 | 내용 |
| --- | --- |
| `/tmp/t21-hospital-demo/hospital-demo-report.json` | 정렬/QC/리플레이 요약 JSON |
| `/tmp/t21-hospital-demo/shadow-capture.jsonl` | 메타데이터 전용 shadow + ExportManifest |

클라우드 URI(`s3://` 등)는 fail-closed입니다. 로컬 경로만 사용하세요.

---

## 리포트 읽는 법 (데모 설명용)

1. **status = PASS** — synthetic hospital alignment + replay QC 통과  
2. **clinical_validation = false** — 임상 검증/모니터 claim 없음 (RUO)  
3. **contains_phi / includes_phi = false** — PHI·파형 미포함 export  
4. **mode = OBSERVE_ONLY_SHADOW** — 관찰 전용 Shadow Mode  
5. PROXY 공개 벤치(BIDMC/MIT-BIH/Fantasia)는 **별도 CI/MCP**이며, 이 원커맨드 데모의 필수 입력은 **아닙니다**. PROXY는 항상 **PROXY**로 라벨합니다.

---

## Show-card (데모 화면용)

리포트 JSON으로 PHI-false Markdown 카드 생성:

```bash
python3 scripts/generate_hospital_demo_showcard.py \
  /tmp/t21-hospital-demo/hospital-demo-report.json \
  -o /tmp/t21-hospital-demo/showcard.md
```

예시: [`hospital-demo-showcard.example.md`](hospital-demo-showcard.example.md)

## 다음에 볼 문서

- ExportManifest PHI-false 파트너 1페이지: [`EXPORT_MANIFEST_PHI_FALSE_KR.md`](EXPORT_MANIFEST_PHI_FALSE_KR.md)
- Eng CI 인벤토리: [`docs/benchmarks/ARTIFACTS_INDEX.md`](../benchmarks/ARTIFACTS_INDEX.md)
- MCP 온보딩: [`MCP_ONBOARDING_KR.md`](MCP_ONBOARDING_KR.md)

VitalDB · CapnoBase · PulseDB · MIMIC · 병원 PHI 경로 **미포함**.
