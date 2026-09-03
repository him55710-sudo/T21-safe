# Founder용 dual-MCP 트러블슈팅 (KR)

**Status:** DRAFT · Path B / RUO / Shadow  
**clinical_validation:** `false`  
**목적:** Cursor에서 `fantasia-proxy` / `research-node` 가 안 보일 때 로컬에서 먼저 고치기  
**임상 claim 없음.**

기준 가이드:

- [`MCP_ONBOARDING_KR.md`](MCP_ONBOARDING_KR.md)
- [`docs/mcp/FOUNDER_DUAL_MCP_SETUP.md`](../mcp/FOUNDER_DUAL_MCP_SETUP.md)
- [`docs/mcp/UNIFIED_MCP.md`](../mcp/UNIFIED_MCP.md)

---

## 빠른 진단

1. **데스크톱 없이 서버 스모크** (레포 루트)
   ```bash
   python -m pip install -e "services/engine[dev,wfdb]"
   PYTHONPATH=services/engine/src python scripts/smoke_dual_mcp.py
   ```
   `PASS fantasia-proxy` / `PASS research-node` 가 나와야 합니다. FAIL이면 Cursor 설정 전에 로컬 환경을 고칩니다.

2. **Python이 Cursor와 동일한지**  
   `UNIFIED_MCP.md` 의 `/absolute/path/to/python` · `PYTHONPATH` 를 Cursor MCP JSON에 그대로 맞춥니다. shell `PATH` 와 Cursor env가 다르면 콘솔 스크립트만 되고 MCP는 실패합니다.

3. **Cursor 완전 재시작**  
   MCP 설정만 저장하고 창만 닫으면 부족할 수 있습니다. 앱을 완전히 종료 후 다시 엽니다.

4. **툴은 보이는데 출력이 이상함**  
   모든 툴 응답에 `clinical_validation=false` · RUO/Shadow 가 있어야 합니다. 클라우드 URI/`s3://`/`gs://` 출력 경로는 fail-closed 가 정상입니다.

5. **BIDMC/MIT-BIH PROXY 툴**  
   Research Node에 `run_mitbih_beat_bench` / `run_bidmc_align_resp_bench` 가 없으면 엔진이 옛 설치일 수 있습니다. editable 재설치 후 smoke를 다시 돌립니다.

---

## 하지 말 것

- PHI/파형을 클라우드로 보내기  
- PATH_SCOPE 밖(엔진 코드·CI·벤치 로직)을 이 문서만으로 “임시 수정”하기 — 새 CODEX 슬라이스로 열기  
- VitalDB 등 freeze 밖 데이터셋 끌어오기 (`v1.2-mcp-dx`)
