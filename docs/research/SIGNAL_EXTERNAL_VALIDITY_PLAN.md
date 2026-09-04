# Signal External Validity Plan — M0-A

**Status:** Protocol plan; evidence collection not yet complete

**Mode:** Path B / Research Use Only / Shadow / `clinical_validation=false`
**M0 freeze:** No clinical-definition, model, weight, or threshold change is authorized by this document.

## Purpose

Define how the team will determine whether the version-pinned deterministic signal pipeline behaves consistently outside the development fixtures. External validity here means transportability of signal acquisition, quality assessment, feature computation, missingness handling, and output availability. It does **not** mean that the Research Instability Index (RII) is clinically validated, diagnostic, or predictive of an outcome.

## Questions and evidence boundaries

| Question | Evidence required | M0 interpretation |
| --- | --- | --- |
| Can supported waveforms be ingested reproducibly across sites/devices? | Interface conformance, units, sampling metadata, timestamp and lead/channel mapping | Engineering compatibility only |
| Are signal-quality and missingness behaviors stable across cohorts? | Prespecified availability, invalidity, dropout, and reason-code summaries | Descriptive; no patient-care claim |
| Are deterministic features reproducible under the pinned pipeline? | Container/code/data/preprocessing versions plus repeat-run checksums | Technical reproducibility only |
| Does performance transport to the intended population and setting? | PI-approved, representative external cohort and locked analysis plan | `PI_REQUIRED`; cannot be answered by public non-DS proxy data |
| Can the display be interpreted safely? | Human-factors protocol and comprehension evidence | Separate from model validity |

## Study sequence

### EV-0 — Contract and provenance readiness

Before any external record is processed, record:

- dataset custodian, approval basis, license/DUA, site, device, software export version, signal names, units, sample rates, and time basis;
- cohort inclusion/exclusion criteria approved by the PI, without inventing missing context;
- immutable dataset manifest and record-level pseudonymous study identifiers;
- commit SHA, model identifier, preprocessing version, configuration digest, runtime/container digest, and analysis-script version;
- a data dictionary and mapping log for every transformation.

**Gate:** data governance, no-PHI review, and mapping review are complete. Failure blocks processing.

### EV-1 — Interface and signal-quality transport

Run the frozen pipeline without tuning. Report by site/device and prespecified subgroup:

- records and analyzable duration presented, accepted, and rejected;
- channel presence, sample-rate and unit conformity;
- missingness, discontinuity, clipping/artifact indicators, and invalid-output duration;
- baseline eligibility and failure reasons;
- processing failures and unmapped fields.

Do not suppress rejected records. Denominators and reasons must remain visible.

### EV-2 — Feature reproducibility and distribution shift

Using only PI-approved variables and a locked analysis script:

- confirm deterministic repeatability on identical inputs;
- compare feature availability and distributions with the development reference;
- characterize shift by site/device and prespecified groups with uncertainty intervals;
- investigate likely acquisition, mapping, or preprocessing causes without changing values in the frozen pipeline.

Observed shift creates an evidence gap or future change proposal. It does not authorize retuning.

### EV-3 — Clinical external validation (future gate)

This stage requires a PI-approved endpoint, population, sample-size rationale, ground-truth process, statistical analysis plan, missing-data strategy, multiplicity handling, and acceptance criteria defined **before** unblinding outcomes. Calibration and discrimination measures must match the locked estimand and include uncertainty intervals. Site-held-out or independent-site analysis is preferred where feasible.

**Gate:** EV-3 cannot begin or be claimed complete until the Clinical Research Lock is approved and the Founder records an explicit unfreeze scope.

## Dataset roles

| Dataset class | Allowed use | Prohibited interpretation |
| --- | --- | --- |
| Synthetic fixtures | Contract, deterministic regression, failure-path testing | Biological or clinical performance |
| Public non-DS proxy data | Pipeline/SQI feasibility and engineering stress tests, with attribution | DS-specific or intended-use validation |
| Retrospective site data | Approved observational validation under governance | Prospective workflow safety or clinical utility |
| Prospective shadow data | Workflow, acquisition, and prespecified validation evidence | Patient-care intervention or alarm performance unless separately authorized |

## Bias, subgroup, and missingness controls

The PI and statistician must prespecify scientifically justified groups based on variables actually collected. Report availability and performance with denominators and uncertainty; do not infer diagnoses or histories from waveforms. Analyze whether exclusions, unusable signal, device mix, and missing context differ across groups. Small cells are suppressed or aggregated under the approved privacy plan, not silently omitted.

## Change control and outputs

Each execution produces a read-only evidence packet: protocol/SAP version, approvals, dataset manifest, lineage map, environment and code identifiers, frozen configuration digest, analysis logs, exclusions, results, deviations, and reviewer decisions. Any proposed pipeline or display change becomes a separately reviewed change request and is evaluated on a new version; it never rewrites the frozen run.

## Exit decisions

- **Proceed:** evidence packet complete and prespecified technical criteria met; only the approved next stage opens.
- **Hold:** remediable mapping, quality, representativeness, or governance gap; document owner and due date.
- **Stop:** unauthorized data, provenance failure, material protocol deviation, or unsafe/unsupported interpretation.

Related: [Clinical Research Lock](CLINICAL_RESEARCH_LOCK_V0.md), [Statistical Analysis Plan](STATISTICAL_ANALYSIS_PLAN.md), [Data Lineage](../data/DATA_LINEAGE.md), [RII display options](../model/RII_DISPLAY_HF_OPTIONS.md).
