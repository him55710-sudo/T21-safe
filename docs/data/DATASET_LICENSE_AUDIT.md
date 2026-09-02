# Dataset license audit

Audit date: 2026-09-02. This is an engineering provenance review, not legal advice. Re-check source terms before every acquisition or redistribution.

| Dataset | Recorded license/access | Audit result | Required action |
|---|---|---|---|
| VitalDB Open | CC BY 4.0; open | Verified against official API/source description | Preserve attribution and source terms |
| INSPIRE 1.4.2 | Korea Credentialed Health Data License 1.0.0; CITI/DUA | Verified | Credentialing and DUA; no DS construction from excluded codes |
| MIMIC-IV 3.1 | PhysioNet Credentialed Health Data License 1.5.0; CITI/DUA | Verified | Approved environment; derived data/models may remain sensitive |
| MIMIC-IV Waveform 0.1.0 | ODbL 1.0; open technical preview | Verified | ODbL attribution/share-alike analysis before derivative distribution |
| MIMIC-III Waveform | ODbL 1.0; waveform open, clinical linkage restricted | Consistent with registry | Separate waveform and clinical-table permissions |
| MIMIC-III-Ext-PPG | PhysioNet Credentialed Health Data License 1.5.0 | Consistent with registry | Do not redistribute; preserve patient grouping |
| Propofol autonomic dynamics 1.0 | PhysioNet Contributor Review Health Data License and DUA 1.5.0 | **Corrected:** registry previously said ODC Attribution 1.0 | Apply current DUA, no re-identification, review derivative-sharing terms |
| BIDMC PPG/Respiration 1.0.0 | ODC Attribution 1.0; open | Verified | Preserve citation and attribution |
| PTT-PPG 1.1.0 | ODbL 1.0; open | Verified | Attribution/share-alike review |
| MIT-BIH Arrhythmia 1.0.0 | ODC Attribution 1.0; open | Consistent with registry | Preserve attribution |
| Fantasia 1.0.0 | ODC Attribution 1.0; open | Consistent with registry | Preserve attribution |
| Multimodal Surgery/Anesthesia 1.0 | PhysioNet Restricted Health Data License 1.5.0; DUA | Consistent with registry | Credentialing/DUA; no redistribution |
| VitalDB Arrhythmia 1.0.0 | ODC Attribution 1.0; open | Consistent with registry | Preserve PhysioNet and VitalDB citations |

## Repository controls

- `download_open_sample.py` allows only registry rows marked open, HTTPS, allowlisted official hosts, explicit sample URL/size limits, and destinations outside the checkout.
- `generate_data_manifest.py` records source, version, license, size, and SHA-256.
- Restricted datasets are never downloaded by repository tooling.
- Raw data directories are ignored and must not be committed.

## Remaining gap

The web case API does not yet source license strings directly from the registry; the frontend applies a conservative source-based label. Before hospital or multi-dataset PoC use, expose a manifest ID and exact dataset license/attribution in every replay case and export.
