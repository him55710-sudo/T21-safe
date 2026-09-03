# Research engineering artifacts index

> **PUBLIC_DATA_REPORT_V1 freeze: `v2.1-proxy-hyp-benches` · `2026-09-04 UTC`**
>
> **PROXY / engineering only**  
> **clinical_validation=false**  
> **No DS clinical claims.**  
> **Fantasia Master Notion: `VERIFIED PROXY` (page `3d09631d743b81efae8fe2731113b4f6`).**
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

## Unified local MCP setup

- Commit: `66c792a` (CODEX-022)
- Two-server client configuration and shared stdio smoke matrix:
  [`docs/mcp/UNIFIED_MCP.md`](../mcp/UNIFIED_MCP.md)
- Founder Cursor checklist:
  [`docs/mcp/FOUNDER_DUAL_MCP_SETUP.md`](../mcp/FOUNDER_DUAL_MCP_SETUP.md)
- Desktop-independent dual-server check: `python scripts/smoke_dual_mcp.py`

## Fantasia local-first MCP

- Commits: `38e749d` (CODEX-018), `41211ce` (CODEX-019), `7c69ff8` (CODEX-020)
- Guide: [`docs/mcp/FANTASIA_MCP.md`](../mcp/FANTASIA_MCP.md)
- Module / command: `t21_engine.fantasia_mcp` / `t21-fantasia-mcp`
- Tools: `list_records`, `load_sample`, `run_hrv_proxy_bench`
- Verification command:
  `python -m pytest tests/backend/unit/test_fantasia_mcp.py tests/backend/unit/test_fantasia_mcp_stdio.py`

The tools are local-only, bounded, and gated to `PROXY_HRV_AGE_STABILITY` with
`clinical_validation=false`. VERIFIED PROXY references Notion page
`3d09631d743b81efae8fe2731113b4f6`; this does not create a clinical claim.
The stdio smoke test starts the real server process and checks MCP initialization and
tool discovery using the repository's synthetic-fixture setup; no desktop client or
Fantasia download is required.

## Synthetic Research Node MCP

- Commits: `9c5d4d9` (CODEX-021), `66c792a` (CODEX-022), `3cd2dab` (CODEX-023)
- Guide: [`docs/mcp/RESEARCH_NODE_MCP.md`](../mcp/RESEARCH_NODE_MCP.md)
- Module / command: `t21_engine.research_node_mcp` / `t21-research-node-mcp`
- Tools: `run_synthetic_demo`, `run_time_align_qc`, `run_sqi_missingness_impact`,
  `run_baseline_window_sensitivity`, `run_mitbih_beat_bench`,
  `run_bidmc_align_resp_bench`, `list_local_shadow_exports`, `export_shadow_summary`
- Verification command:
  `python -m pytest tests/backend/unit/test_research_node_mcp.py tests/backend/unit/test_research_node_mcp_stdio.py tests/backend/integration/test_research_node_demo.py`

This local-only MCP reuses the deterministic synthetic Path B demo, alignment QC,
replay, shadow JSONL writer, and `ExportManifest`. It requires neither Fantasia nor a
public clinical dataset and provides no VitalDB, CapnoBase, PulseDB, MIMIC, PHI,
dosing, alerting, or actuation path. Every tool payload preserves
`clinical_validation=false`, `synthetic_only=true`, and observe-only gates.
Shadow JSONL records expose `shadow-capture/1.0` and `export-manifest/1.0`; the
read-only MCP tools list local files or return validated aggregate counts only.
The two sensitivity tools reuse the indexed evaluation modules as read-only MCP
operations and return a `PI_TO_DEFINE` banner on both success and failure.
The MIT-BIH and BIDMC tools reuse their indexed evaluation modules and local fixture
fallbacks as pinned-record, read-only PROXY operations. Every result, including a
failure, carries `clinical_validation=false`, a PROXY banner, and no DS or clinical
claim; the underlying dataset block retains `master_verified_proxy` where applicable.
Neither tool adds a network, arbitrary-path, artifact-write, or VitalDB path.

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
  (`v1.1-mcp-pre-VitalDB`, `2026-09-03 UTC`)
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

## Founder / DX packaging (025–028)

Freeze companion: [`PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md) (`v1.2-mcp-dx` history; tip `v1.3-mcp-dx2`).

| Item | Commit | Pointer |
| --- | --- | --- |
| Dual-MCP smoke + EN setup checklist | `e6514fc` | `docs/mcp/FOUNDER_DUAL_MCP_SETUP.md`, `scripts/smoke_dual_mcp.py` |
| Shadow JSONL schema + MCP list/export | `ed13e47` | Research Node MCP tools `list_local_shadow_exports` / `export_shadow_summary` |
| BIDMC/MIT-BIH PROXY MCP tools | `03468f1` | `run_mitbih_beat_bench` / `run_bidmc_align_resp_bench` |
| Founder KR MCP onboarding | `fa9b152` | `docs/founder/MCP_ONBOARDING_KR.md` |

`clinical_validation=false` · PROXY/RUO only · no DS clinical claims · VitalDB not included.

## MCP DX2 packaging (039–044)

Freeze companion: [`PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md) (`v1.3-mcp-dx2`).

| Item | Commit | Pointer |
| --- | --- | --- |
| MCP tool catalog auto-gen | `2b890ac` | `scripts/generate_mcp_tool_catalog.py`, `docs/mcp/TOOL_CATALOG.md` |
| mcp-stdio-smoke path filters + matrix | `da75ff1` | `.github/workflows/mcp-stdio-smoke.yml` |
| `list_demo_presets` MCP tool | `0fbaf5d` | Research Node MCP |
| Shadow JSONL schema pin tests | `79e977b` | `tests/backend/unit/test_shadow_jsonl_schema.py` |
| Fantasia age `PI_TO_DEFINE` asserts | `43f1859` | `tests/backend/unit/test_fantasia_mcp*.py` |
| TOOL_CATALOG regen (`list_demo_presets`) | `1acb911` | `docs/mcp/TOOL_CATALOG.md` |

`clinical_validation=false` · PROXY/RUO only · no DS clinical claims · VitalDB not included.

## Path B verify packaging (051–055)

Freeze companion: [`PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md) (`v1.4-path-b-verify`).

| Item | Commit | Pointer |
| --- | --- | --- |
| Schema/unit pins CI | `d599f68` | `.github/workflows/mcp-schema-unit-pins.yml` |
| Founder DX verify script | `3701b2e` | `scripts/verify_path_b_mcp.sh` |
| Verify script CI | `87680a1` | `.github/workflows/path-b-mcp-verify.yml` |
| Verify script thin unit | `e498967` | `tests/backend/unit/test_verify_path_b_mcp.py` |
| UNIFIED_MCP verify pointer | `9dd49cd` | `docs/mcp/UNIFIED_MCP.md` |

`clinical_validation=false` · PROXY/RUO only · no DS clinical claims · VitalDB not included.

## MCP verify hardening (059–067)

Freeze companion: [`PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md) (`v1.5-mcp-verify`).

| Item | Commit | Pointer |
| --- | --- | --- |
| Schema pins + roundtrip CI | `af5e869` | `.github/workflows/mcp-schema-unit-pins.yml` |
| `export_shadow_summary` roundtrip | `8c99037` | `tests/backend/unit/test_research_node_mcp.py` |
| Catalog drift fail-closed | `9d788c1` | `tests/backend/unit/test_mcp_tool_catalog.py` |
| Verify unit in Path B / schema CI | `4cdb61c` | `.github/workflows/path-b-mcp-verify.yml`, `mcp-schema-unit-pins.yml` |
| Shadow exports list tmp roundtrip | `048336b` | `tests/backend/unit/test_research_node_mcp.py` |
| Fantasia list_records sha256 | `09fa324` | `tests/backend/unit/test_fantasia_mcp.py` |
| Public PROXY bench CI | `f0d661d` | `.github/workflows/proxy-bench-smoke.yml` |
| Synthetic hospital QC CI | `904cc9e` | `.github/workflows/synthetic-hospital-qc-smoke.yml` |

`clinical_validation=false` · PROXY/RUO only · no DS clinical claims · VitalDB not included.

## Eng CI packaging (069–074)

Freeze companion: [`PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md) (`v1.6-eng-ci`).

| Item | Commit | Pointer |
| --- | --- | --- |
| Fantasia HRV/age PROXY CI | `ae1a59b` | `.github/workflows/proxy-bench-smoke.yml` |
| Replay pipeline CI | `48feac4` | `.github/workflows/replay-pipeline-smoke.yml` |
| Research node demo CI | `85ed55f` | `.github/workflows/research-node-demo-smoke.yml` |
| Baseline + SQI sensitivity CI | `6e0d4c2` | `.github/workflows/sensitivity-bench-smoke.yml` |
| public_data_bench CI | `f7dd376` | `.github/workflows/proxy-bench-smoke.yml` |
| Empty signal batch fail-closed | `8b1ba66` | `services/engine/src/t21_engine/streaming/replay.py` |

`clinical_validation=false` · PROXY/RUO only · no DS clinical claims · VitalDB not included.

## Eng CI workflow inventory (066–076)

CODEX-078 checklist of Path B eng smoke workflows landed after MCP verify packaging.
`CODEX-077` SKIP — RingBuffer zero-capacity already raises in `__init__`; empty `append` is intentional no-op (ReplayPipeline empty-batch fail-closed is CODEX-074).

| CODEX | Workflow / note | Commit | Path |
| --- | --- | --- | --- |
| 066 | Public PROXY bench smoke (BIDMC + MIT-BIH) | `f0d661d` | `.github/workflows/proxy-bench-smoke.yml` |
| 067 | Synthetic hospital QC smoke | `904cc9e` | `.github/workflows/synthetic-hospital-qc-smoke.yml` |
| 068 | Freeze `v1.5-mcp-verify` (docs) | `6b52604` | `docs/benchmarks/**` |
| 069 | Fantasia HRV/age added to proxy-bench | `ae1a59b` | `.github/workflows/proxy-bench-smoke.yml` |
| 070 | Replay pipeline smoke | `48feac4` | `.github/workflows/replay-pipeline-smoke.yml` |
| 071 | Research node demo smoke | `85ed55f` | `.github/workflows/research-node-demo-smoke.yml` |
| 072 | Sensitivity bench smoke | `6e0d4c2` | `.github/workflows/sensitivity-bench-smoke.yml` |
| 073 | `public_data_bench` on proxy-bench | `f7dd376` | `.github/workflows/proxy-bench-smoke.yml` |
| 074 | Empty signal batch fail-closed (engine) | `8b1ba66` | `services/engine/src/t21_engine/streaming/replay.py` |
| 075 | Freeze `v1.6-eng-ci` (docs) | `a153e74` | `docs/benchmarks/**` |
| 076 | Baseline features risk smoke | `7a35713` | `.github/workflows/baseline-features-risk-smoke.yml` |
| 077 | SKIP (RingBuffer already fail-closed / empty append no-op) | — | `services/engine/src/t21_engine/streaming/ring_buffer.py` |

`clinical_validation=false` · PROXY/RUO only · no DS clinical claims · VitalDB not included.

## Hospital demo packaging (079–100)

Founder/partner showable Path B demo track after eng CI packaging (`v1.6-eng-ci` tip moves to `v1.7-hospital-demo` in CODEX-088).

| Item | Commit | Pointer |
| --- | --- | --- |
| One-command hospital demo runner | `75fbf65` | `scripts/run_hospital_demo.sh` |
| Hospital demo KR onboarding | `8ace65f` | `docs/founder/HOSPITAL_DEMO_ONBOARDING_KR.md` |
| ExportManifest PHI-false partner pack | `366811c` | `docs/business/export-manifest-phi-false-1p.md`, `docs/founder/EXPORT_MANIFEST_PHI_FALSE_KR.md` |
| Hospital demo CI smoke | `d3d995d` | `.github/workflows/hospital-demo-smoke.yml` |
| PHI-false Markdown show-card | `835706d` | `scripts/generate_hospital_demo_showcard.py` |
| Multi-seed demo matrix (`--seeds`) | `99f9bac` | `scripts/run_hospital_demo.sh` |
| Partner pack zip (no shadow JSONL) | `3a92306` | `scripts/pack_hospital_demo_partner.sh` |
| CI extends showcard + partner pack | `73a5cf1` | `.github/workflows/hospital-demo-smoke.yml` |
| HTML browser show-card | `b1a5597` | `scripts/generate_hospital_demo_showcard_html.py` |
| Demo → HTML → partner zip chain | `001a008` | `scripts/run_hospital_demo_chain.sh` |
| Hospital demo runbook (KR) | `abbac57` | `docs/founder/HOSPITAL_DEMO_RUNBOOK_KR.md` |
| CI HTML showcard + chain units | `12f01c7` | `.github/workflows/hospital-demo-smoke.yml` |
| Partner pack HTML showcard default | `abca64c` | `scripts/pack_hospital_demo_partner.sh` |
| Partner pack business 1-pagers | `d5aa785` | `scripts/pack_hospital_demo_partner.sh` |
| Print-friendly HTML show-card | `b9862e3` | `scripts/generate_hospital_demo_showcard_html.py` |
| Pack freeze / runbook refresh | `5f3dac1` | `docs/founder/HOSPITAL_DEMO_RUNBOOK_KR.md`, `docs/benchmarks/**` |
| Partner zip fail-closed CI/unit | `a46aa74` | `.github/workflows/hospital-demo-smoke.yml`, `tests/backend/unit/test_partner_pack_zip_contents.py` |
| Makefile hospital-demo targets | `5f68050` | `Makefile` |
| Ready freeze tip | `3659fc3` | `docs/benchmarks/**` |

`clinical_validation=false` · synthetic/local · `includes_phi=false` · no DS clinical claims · VitalDB not included.

## Hospital demo freeze (079–087)

Freeze companion: [`PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md) (`v1.7-hospital-demo`).

See **Hospital demo packaging (079–086)** above for paths/commits. CODEX-087 refreshes this index; tip freeze is `v1.7-hospital-demo`.

`clinical_validation=false` · synthetic/local · PHI-false · no DS clinical claims · VitalDB not included.

## Hospital demo HTML freeze (089–093)

Freeze companion: [`PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md) (`v1.8-hospital-demo-html`).

See **Hospital demo packaging (079–093)** above. Tip freeze is `v1.8-hospital-demo-html`.

`clinical_validation=false` · synthetic/local · PHI-false · no DS clinical claims · VitalDB not included.

## Hospital demo pack freeze (095–097)

Freeze companion: [`PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md) (`v1.9-hospital-demo-pack`).

Tip freeze after business 1-pagers + print-friendly HTML show-card.

`clinical_validation=false` · synthetic/local · PHI-false · no DS clinical claims · VitalDB not included.

## Hospital demo ready freeze (098–100)

Freeze companion: [`PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md) (`v2.0-hospital-demo-ready`).

Tip freeze after fail-closed partner zip CI and Makefile wrappers.

`clinical_validation=false` · synthetic/local · PHI-false · no DS clinical claims · VitalDB not included.

## PROXY Analysis Plan v0.1 (HYP-01/03/07)

### METHODS_CRITIQUE + Auditor DSCS (read first)

- **Auditor DSCS (HANDOFF):** HYP-01 **PARTIALLY_SUPPORTED** (HR-event/SQI only); HYP-03/07 **STRETCH if positive PROXY** / **OK as neg-control-QA**; **no clinical FACT**.
- **v0.1 claim collapse:** ECG HR-event / SQI only — do not expand to positive autonomic/age/HRV PROXY story.
- **Airway + BIDMC: do-not-run** on this track.
- **PROXY ≠ DS** · Path B RUO · **`clinical_validation=false`** on all outputs.
- Thresholds remain **`PI_TO_DEFINE`** (no clinical cutoffs hardcoded).
- **RQ-004** resting HRV → peri-op stays **HYPOTHESIS/gap** (never FACT).
- **LF/HF is not primary**; **&lt;180s withheld** (Task Force gate).
- **Age metadata UNAVAILABLE** / `PI_TO_DEFINE` on synthetic fixtures.
- **Selection / confounding / leakage:** PhysioNet ambulatory/resting (or synthetic fixture-equivalent) only — not OR/ICU/DS; does not resolve peri-op confounding; local fixture observe-only; no PHI/waveform cloud; Dataset rows are PROXY fixtures, not experiment-approved; do not recycle engineering numbers into clinical lockbox claims.
- No pooled instability score · no BIDMC / Airway / Driver-map / dosing / closed-loop.
- HYP Claims with `HUMAN_REVIEW_REQUIRED` are **labels**, not clinical facts.
- Founder-facing pack: [`docs/founder/PROXY_HYP_RESULTS_KR.md`](../founder/PROXY_HYP_RESULTS_KR.md) (Auditor DSCS + METHODS_CRITIQUE at top).

Founder-approved PROXY Analysis Plan benches + one-command runner (CODEX-101–106).
Method Master: Notion `P2E-METHOD-PROXY-PLAN-V01` (CODEX_READY).

| Item | Commit | Pointer |
| --- | --- | --- |
| HYP-01 MIT-BIH abs/rel brady-def sensitivity | `af98247` | `t21_engine.evaluation.mitbih_brady_def_sensitivity` |
| HYP-03 Fantasia short-window HRV/LF-HF negative-control | `6318771` | `t21_engine.evaluation.fantasia_short_window_hrv_lfhf` |
| HYP-07 Fantasia age-band HRV stability engine QA | `f0f7692` | `t21_engine.evaluation.fantasia_age_band_hrv_stability` |
| One-command PROXY HYP runner (JSON/MD tables) | `d0b3988` | `scripts/run_proxy_hyp_benches.sh`, `t21_engine.evaluation.proxy_hyp_bench_runner` |
| CI smoke for PROXY HYP runner | `385b812` | `.github/workflows/proxy-hyp-bench-smoke.yml` |
| Founder PROXY results pack (KR) | `b710db6` | [`docs/founder/PROXY_HYP_RESULTS_KR.md`](../founder/PROXY_HYP_RESULTS_KR.md) |
| METHODS_CRITIQUE prominence | `628911e` | `docs/founder/PROXY_HYP_RESULTS_KR.md`, `ARTIFACTS_INDEX.md` |
| Auditor DSCS founder-pack wording | `9e7dce8` | `docs/founder/PROXY_HYP_RESULTS_KR.md`, pack README |
| PROXY HYP partner zip | `3025cca` | `scripts/pack_proxy_hyp_partner.sh` |
| PROXY HYP MCP list/run | `e2c3d6d` | `t21_engine.proxy_hyp_mcp`, `t21-proxy-hyp-mcp` |

Commands:

```bash
make proxy-hyp-benches
# or: bash scripts/run_proxy_hyp_benches.sh /tmp/t21-proxy-hyp-benches
```

Artifacts emitted: `proxy-hyp-bench-report.json`, `proxy-hyp-bench-results.md`.

`clinical_validation=false` · MIT-BIH+Fantasia local fixtures only · role tags `PROXY_ECG_BENCHMARK` / `PROXY_HRV_AGE_STABILITY` · FACT/INTERPRETATION/HYPOTHESIS layers · thresholds `PI_TO_DEFINE` · no pooled instability score · no BIDMC / Airway / Driver-map / PHI · no dosing/closed-loop · HYP Claims `HUMAN_REVIEW_REQUIRED` remain labels not clinical facts.

## PROXY Analysis Plan freeze tip

Freeze companion: [`PUBLIC_DATA_REPORT_V1.md`](PUBLIC_DATA_REPORT_V1.md) (`v2.1-proxy-hyp-benches`).

Covers CODEX-101–109 (benches, runner, CI, METHODS_CRITIQUE docs, partner zip, MCP).
Hospital demo tip `v2.0-hospital-demo-ready` remains valid for packaging track.

`clinical_validation=false` · PROXY≠DS · MIT-BIH+Fantasia local only · no BIDMC/Airway/PHI · no dosing/closed-loop.
