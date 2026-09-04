# Research Node demo

This is a synthetic-only, local demonstration of the Path B research workflow. It is
Research Use Only (RUO), runs in observe-only shadow mode, contains no patient data,
and always reports `clinical_validation=false`. It is not a clinical monitor.

Korean PROXY v0.1 meeting talk track (ECG HR-event/SQI only; no FACT):
[`docs/founder/MEETING_ONEPAGER_PROXY_v0.1_KR.md`](founder/MEETING_ONEPAGER_PROXY_v0.1_KR.md).
Freeze tip: `v2.7-meeting-pack-mcp-followup` (`a0aa6dd`).

## Cursor dual-MCP (Founder)

After the demo entrypoints work, optional Path B MCP tooling can be enabled in Cursor:

- Korean onboarding one-pager: [`docs/founder/MCP_ONBOARDING_KR.md`](founder/MCP_ONBOARDING_KR.md)
- English dual-MCP checklist: [`docs/mcp/FOUNDER_DUAL_MCP_SETUP.md`](mcp/FOUNDER_DUAL_MCP_SETUP.md)
- Unified `mcpServers` JSON: [`docs/mcp/UNIFIED_MCP.md`](mcp/UNIFIED_MCP.md)

These MCP servers remain Research Use Only with `clinical_validation=false`. They are not
a clinical monitor and do not add dosing, alerts, or DS clinical claims.

## One-command hospital demo (CODEX-079)

Showable Path B synthetic hospital run with local shadow JSONL + `ExportManifest` gate checks (`clinical_validation=false`, `includes_phi=false`):

```bash
bash scripts/run_hospital_demo.sh /tmp/t21-hospital-demo
```

Korean Founder onboarding: [`docs/founder/HOSPITAL_DEMO_ONBOARDING_KR.md`](founder/HOSPITAL_DEMO_ONBOARDING_KR.md).

## Run in under six minutes

From the repository root, use Python 3.11 or newer:

```bash
python -m pip install -e "services/engine[dev]"
python -m t21_engine.demo
```

For a clean-environment install and entrypoint smoke test on Linux or macOS:

```bash
python3 -m venv /tmp/t21-research-node-venv
source /tmp/t21-research-node-venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "services/engine[dev]"
python -c "import t21_engine.demo"
python -m t21_engine.demo --help
t21-research-node-demo --help
python -m pytest tests/backend/integration/test_research_node_demo.py -q
```

Remove an existing `/tmp/t21-research-node-venv` first, or choose a new path, when
you need to prove the install does not depend on previously installed packages. The
two help commands validate both supported entrypoints without running a replay.

The second command is the one-command demo runner. It creates the deterministic
synthetic hospital case, checks channel time alignment, runs the existing replay/QC
pipeline without real-time delays, and prints one JSON report. The default run does
not write any files.

To append metadata-only shadow captures and an `ExportManifest` to local JSONL:

```bash
python -m t21_engine.demo --output-dir /tmp/t21-research-node-demo
```

The output is `shadow-capture.jsonl` in that directory. Capture records exclude raw
waveforms and PHI; the final line is the manifest. Output paths with a URI scheme,
including cloud storage URIs, fail closed. Choose a new or empty local directory when
you want a standalone export because repeated runs append to the JSONL file.

After editable installation, the equivalent console command is:

```bash
t21-research-node-demo --output-dir /tmp/t21-research-node-demo
```

Optional reproducibility controls are `--duration-seconds`, `--baseline-seconds`, and
`--seed`. The runner accepts only its built-in synthetic factory; it has no public-data
or patient-data input path and provides no alerts, treatment, or dosing behavior.
