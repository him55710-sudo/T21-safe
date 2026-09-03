# Research engineering artifacts index

> **PUBLIC_DATA_REPORT_V1 freeze: `v1.0-pre-VitalDB` · `2026-09-02 UTC`**
>
> **PROXY / engineering only**  
> **clinical_validation=false**  
> **No DS clinical claims.**  
> **Fantasia Master Notion: `VERIFIED PROXY` (page `3d09631d743b81efae8fe2731113b4f6`).**
> The frozen `PUBLIC_DATA_REPORT_V1` retains its historical `PENDING` label.
>
> **VitalDB, CapnoBase, and PulseDB are NOT included in this freeze.**
>
> **Path B: observe-only / Research Use Only (RUO) / no dosing alerts as claims.**

This index points to reproducible engineering artifacts and their landing commits. It
does not report clinical performance or extend the claims made by the linked documents.
Run commands from the repository root after installing the engine development package:

```bash
python -m pip install -e "services/engine[dev]"
```

## DEMO runner

- Commit: `020dd79`
- Guide: [`docs/DEMO.md`](../DEMO.md)
- Module: `t21_engine.demo`
- Commands: `python -m t21_engine.demo` or, after installation,
  `t21-research-node-demo`

The demo is deterministic, synthetic-only, local, and has no patient-data input path.

## MIT-BIH beat table

- Commit: `0606d62`
- Module: `t21_engine.evaluation.mitbih_beat_bench`
- Report context: [`PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md), section
  “MIT-BIH-style beat detection table (CODEX-009)”
- Verification command: `python -m pytest tests/backend/unit/test_mitbih_beat_bench.py`

This is a PROXY engineering table; follow the source/provenance distinctions and
non-claims in the public-data report.

## BIDMC align / respiration

- Commit: `869b996`
- Module: `t21_engine.evaluation.bidmc_align_resp_bench`
- Report context: [`PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md), section
  “BIDMC alignment / respiration-rate table (CODEX-011)”
- Verification command: `python -m pytest tests/backend/unit/test_bidmc_align_resp_bench.py`

## Fantasia HRV / age-stability PROXY

- Commit: `f290223`
- Module: `t21_engine.evaluation.fantasia_hrv_age_bench`
- Report context: [`PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md), section
  “Fantasia HRV / age-stability PROXY (CODEX-016)”
- Verification command: `python -m pytest tests/backend/unit/test_fantasia_hrv_age_bench.py`

Authorization is `operational_proxy_ok`; the Notion Master is VERIFIED PROXY. The
fixture has no age metadata, so age-stability is unavailable / `PI_TO_DEFINE`.
`clinical_validation=false`; no DS, anesthesia, clinical age-effect, or PTT/PPG claim.

## Fantasia local-first MCP

- Guide: [`docs/mcp/FANTASIA_MCP.md`](../mcp/FANTASIA_MCP.md)
- Module / command: `t21_engine.fantasia_mcp` / `t21-fantasia-mcp`
- Tools: `list_records`, `load_sample`, `run_hrv_proxy_bench`
- Verification command: `python -m pytest tests/backend/unit/test_fantasia_mcp.py`

The tools are local-only, bounded, and gated to `PROXY_HRV_AGE_STABILITY` with
`clinical_validation=false`. VERIFIED PROXY references Notion page
`3d09631d743b81efae8fe2731113b4f6`; this does not create a clinical claim.

## Baseline 180 / 300

- Commit: `a7d8ebd`
- Module: `t21_engine.evaluation.baseline_window_sensitivity`
- Documentation: [`BASELINE_WINDOW_SENSITIVITY.md`](BASELINE_WINDOW_SENSITIVITY.md)
- Verification command:
  `python -m pytest tests/backend/unit/test_baseline_window_sensitivity.py`

The 180-second and 300-second comparison uses synthetic hospital cases and does not
select a clinical baseline window.

## SQI missingness

- Commit: `aec1d37`
- Module: `t21_engine.evaluation.sqi_missingness_impact`
- Documentation: [`SQI_MISSINGNESS_IMPACT.md`](SQI_MISSINGNESS_IMPACT.md)
- Verification command: `python -m pytest tests/backend/unit/test_sqi_missingness_impact.py`

## PUBLIC_DATA_REPORT_V1

- Frozen report: [`docs/benchmarks/PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md)
  (`v1.0-pre-VitalDB`, `2026-09-02 UTC`)
- Verification command: `python -m pytest tests/backend/unit/test_public_data_bench.py`
- Engineering trail documented in the report: `f4b36f5` → `44ed44c` → `b816efa` →
  `ba514e5`, with related follow-on documentation and benchmark commits in repository
  history.

The report itself is authoritative for dataset provenance, failure semantics, and
explicit non-claims.

## PI pack

The PI-facing documents are under `docs/business/`:

- [`research-node-one-pager.md`](../business/research-node-one-pager.md)
- [`research-overview-2p.md`](../business/research-overview-2p.md)
- [`hospital-aggregate-query-1p.md`](../business/hospital-aggregate-query-1p.md)
- [`safety-local-first-1p.md`](../business/safety-local-first-1p.md)
- [`HOSPITAL_POC_ONEPAGER.md`](../business/HOSPITAL_POC_ONEPAGER.md)
- [`GO_NO_GO_METRICS.md`](../business/GO_NO_GO_METRICS.md)

These materials retain Path B observe-only and RUO boundaries. They do not authorize
dosing alerts, clinical decisions, or DS-specific clinical claims.
