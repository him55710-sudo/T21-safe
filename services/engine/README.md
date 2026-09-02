# T21 Safe signal engine

Deterministic biomedical signal processing for a **Research Use Only / Shadow Mode**
prototype. The engine replays public, local-fixture, or deterministic synthetic signals
and emits an explainable **Research Instability Index**. The index is not a calibrated
clinical probability and must not be used for diagnosis, treatment, dosing, alarms, or
patient monitoring.

## Modes

- `GENERIC_VALIDATION_MODE` checks signal processing and generic adult research labels
  on public perioperative/ICU data.
- `DS_HYPOTHESIS_MODE` visualizes change from a patient-specific baseline. It has no
  validated Down syndrome or pediatric performance and reduces confidence accordingly.

Neither mode puts an LLM in the inference path. No PHI is stored.

## Install and verify

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e "services/engine[dev]" -e "services/api[dev]"
.venv\Scripts\python -m pytest tests/backend -q
.venv\Scripts\python -m ruff check services/engine/src services/api/src tests/backend
.venv\Scripts\python -m mypy --config-file services/engine/pyproject.toml services/engine/src/t21_engine
```

Start the API with:

```powershell
.venv\Scripts\python -m uvicorn t21_api.main:app --host 127.0.0.1 --port 8000
```

## Data sources

- VitalDB public virtual real-time FHIR API (read-only, no key), with source and CC BY
  4.0 attribution preserved.
- Optional WFDB catalog entries for BIDMC, Pulse Transit Time PPG, and the MIMIC-IV
  waveform preview through the `wfdb` extra. Custom WFDB records can also be supplied.
- Bundled small local fixture for offline transport testing.
- Pinned deterministic synthetic scenarios for stable, deteriorating, artifact, signal
  loss, desaturation, and recovery paths.

Unavailable tracks do not crash the pipeline. A public-source failure can explicitly
fall back to the local fixture, and the output then identifies the source as Local
fixture rather than VitalDB.

See [SIGNAL_PIPELINE.md](SIGNAL_PIPELINE.md),
[FEATURE_DICTIONARY.md](FEATURE_DICTIONARY.md), and
[VALIDATION_LIMITATIONS.md](VALIDATION_LIMITATIONS.md).

An optional, non-runtime generic logistic training demo is available with
`pip install -e "services/engine[training]"`. It requires caller-supplied versioned
features, labels, case IDs, and a dataset checksum; it performs case-level splitting and
validation-only threshold selection. It never labels the result as a DS model.
