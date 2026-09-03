# Founder용 Research Node demo 체크리스트 (KR)

**Status:** DRAFT · Path B / RUO / Shadow  
**clinical_validation:** `false`  
**목적:** 로컬에서 synthetic Research Node 데모를 6분 안에 돌리는 최소 절차  
**임상·DS·투약/알림 claim 없음.**

상세 영문 가이드: [`docs/DEMO.md`](../DEMO.md)

---

## 체크리스트

1. 레포 루트에서 Python 3.11+ 확인
2. 엔진 editable 설치
   ```bash
   python -m pip install -e "services/engine[dev]"
   ```
3. 원커맨드 데모 실행 (권장: hospital runner)
   ```bash
   bash scripts/run_hospital_demo.sh /tmp/t21-hospital-demo
   ```
   또는 모듈 직접:
   ```bash
   python -m t21_engine.demo
   ```
   또는
   ```bash
   t21-research-node-demo
   ```
4. JSON 리포트에 `clinical_validation=false` · synthetic/local · 환자 데이터 경로 없음 확인
5. (선택) 로컬 shadow JSONL
   ```bash
   python -m t21_engine.demo --output-dir /tmp/t21-research-node-demo
   ```
   클라우드 URI/`s3://` 등은 fail-closed
6. (선택) clean venv 스모크는 [`docs/DEMO.md`](../DEMO.md) 의 clean-environment 절 참고

---

## MCP로 넘어갈 때

데모가 되면 Cursor dual-MCP는:

- [`MCP_ONBOARDING_KR.md`](MCP_ONBOARDING_KR.md)
- [`docs/mcp/FOUNDER_DUAL_MCP_SETUP.md`](../mcp/FOUNDER_DUAL_MCP_SETUP.md)

---

## 범위

- synthetic only · observe-only · no PHI cloud  
- freeze 참고: tip `v1.6-eng-ci` · onboarding [`HOSPITAL_DEMO_ONBOARDING_KR.md`](HOSPITAL_DEMO_ONBOARDING_KR.md) (`docs/benchmarks/PUBLIC_DATA_REPORT_V1.md`)  
- VitalDB/CapnoBase/PulseDB 미포함
