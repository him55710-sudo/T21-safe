# Research Node demo

This is a synthetic-only, local demonstration of the Path B research workflow. It is
Research Use Only (RUO), runs in observe-only shadow mode, contains no patient data,
and always reports `clinical_validation=false`. It is not a clinical monitor.

## Run in under six minutes

From the repository root, use Python 3.11 or newer:

```bash
python -m pip install -e "services/engine[dev]"
python -m t21_engine.demo
```

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
