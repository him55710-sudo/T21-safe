# Founder용 Cursor dual-MCP 온보딩 (1페이지)

**Status:** DRAFT · Path B / RUO / Shadow  
**clinical_validation:** `false`  
**Freeze note:** 공개 데이터·MCP 엔지니어링 기준선은 `v1.1-mcp-pre-VitalDB` (VitalDB/CapnoBase/PulseDB 미포함)  
**목적:** Cursor에서 Fantasia PROXY + Research Node MCP를 켜는 최소 절차만 안내합니다.  
**임상·DS·투약/알림 claim 없음.**

---

## 한 줄 요약

로컬에서 엔진을 editable 설치한 뒤, Cursor MCP에 **두 서버**(`fantasia-proxy`, `research-node`)를 등록하고 재시작하면 됩니다. 자세한 JSON·툴 목록·스모크는 기존 영문 가이드를 보세요.

---

## 5분 체크리스트

1. **엔진 설치** (레포 루트)
   ```bash
   python -m pip install -e "services/engine[dev,wfdb]"
   ```
2. **Cursor MCP 설정**에 dual `mcpServers` 블록을 붙여넣기  
   → 원문·절대경로 안내: [`docs/mcp/UNIFIED_MCP.md`](../mcp/UNIFIED_MCP.md)
3. **Cursor 완전 재시작** (MCP 리로드)
4. MCP 툴 목록에 두 서버가 보이는지 확인  
   → Founder 영문 단계형: [`docs/mcp/FOUNDER_DUAL_MCP_SETUP.md`](../mcp/FOUNDER_DUAL_MCP_SETUP.md)
5. (선택) 데스크톱 없이 프로세스 스모크
   ```bash
   python scripts/smoke_dual_mcp.py
   ```

---

## 서버가 하는 일 / 안 하는 일

| 서버 | 하는 일 (엔지니어링) | 안 하는 일 |
| --- | --- | --- |
| `fantasia-proxy` | 로컬 Fantasia PROXY HRV/age-stability 워크플로 | DS·마취 임상 검증, PTT/PPG claim, 환자 결정 |
| `research-node` | synthetic demo/QC/shadow JSONL, SQI·baseline, BIDMC/MIT-BIH **PROXY** 벤치 읽기 | PHI 클라우드 전송, 투약/알림, 임상 cutoff claim |

세부 툴·게이트·URI fail-closed:

- Fantasia: [`docs/mcp/FANTASIA_MCP.md`](../mcp/FANTASIA_MCP.md)
- Research Node: [`docs/mcp/RESEARCH_NODE_MCP.md`](../mcp/RESEARCH_NODE_MCP.md)

---

## Freeze / 범위

- 문서·벤치 기준선: **`v1.1-mcp-pre-VitalDB`** (`docs/benchmarks/PUBLIC_DATA_REPORT_V1.md`에 기록된 freeze)
- **포함 안 함:** VitalDB, CapnoBase, PulseDB, MIMIC 벤치 확장
- 모든 MCP/벤치 출력은 **`clinical_validation=false`** 를 유지해야 합니다.

---

## 막히면

1. Python·`PYTHONPATH`가 Cursor가 쓰는 환경과 같은지 확인 (`UNIFIED_MCP.md`의 절대경로 예시).
2. `scripts/smoke_dual_mcp.py`가 FAIL이면 Cursor 설정 전에 로컬 서버부터 고칩니다.
3. PATH_SCOPE 밖(엔진 코드·CI·벤치 구현) 수정이 필요하면 **슬라이스를 새로 열고** 이 문서만으로는 범위를 넓히지 마세요.
