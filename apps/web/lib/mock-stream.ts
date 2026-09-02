import {
  DEFAULT_PATIENT_CONTEXT,
  DISCLAIMER,
  type Evidence,
  type ResearchCase,
  type RiskLevel,
  type StreamFrame,
} from "@/lib/contracts";

export type ScenarioId =
  | "stable_case"
  | "progressive_instability"
  | "artifact_case"
  | "missing_signal_case"
  | "recovery_case"
  | "local_fixture_demo"
  | "vitaldb_public_demo";

export const MOCK_CASES: ResearchCase[] = [
  {
    id: "progressive_instability",
    name: "Progressive instability",
    kind: "SYNTHETIC",
    description: "Stable calibration followed by sustained HR, MAP, and PPG amplitude decline.",
    attribution: "T21 Safe deterministic synthetic generator",
    license: "Project test fixture — no patient data",
    verified_ds: false,
  },
  {
    id: "stable_case",
    name: "Stable physiology",
    kind: "SYNTHETIC",
    description: "Stable baseline, high signal quality, and a low research index.",
    attribution: "T21 Safe deterministic synthetic generator",
    license: "Project test fixture — no patient data",
    verified_ds: false,
  },
  {
    id: "artifact_case",
    name: "ECG motion artifact",
    kind: "SYNTHETIC",
    description: "ECG artifact lowers SQI and suppresses the research index.",
    attribution: "T21 Safe deterministic synthetic generator",
    license: "Project test fixture — no patient data",
    verified_ds: false,
  },
  {
    id: "missing_signal_case",
    name: "Missing PPG signal",
    kind: "SYNTHETIC",
    description: "PPG is absent; operation is degraded with an explicit limitation.",
    attribution: "T21 Safe deterministic synthetic generator",
    license: "Project test fixture — no patient data",
    verified_ds: false,
  },
  {
    id: "recovery_case",
    name: "Deterioration and recovery",
    kind: "SYNTHETIC",
    description: "Temporary deterioration returns toward the patient-specific baseline.",
    attribution: "T21 Safe deterministic synthetic generator",
    license: "Project test fixture — no patient data",
    verified_ds: false,
  },
  {
    id: "local_fixture_demo",
    name: "Local contract fixture",
    kind: "LOCAL_FIXTURE",
    description: "Prepackaged deterministic stream used for offline contract inspection.",
    attribution: "T21 Safe local exact-contract fixture",
    license: "Project test fixture — no patient data",
    verified_ds: false,
  },
  {
    id: "vitaldb_public_demo",
    name: "VitalDB public case demonstration",
    kind: "VITALDB_PUBLIC",
    description: "Public waveform replay placeholder used only to demonstrate signal processing.",
    attribution: "VitalDB public data — integration placeholder; see dataset information",
    license: "VitalDB data use terms apply",
    verified_ds: false,
  },
];

export const MOCK_EVIDENCE: Evidence = {
  model_version: "rii-demo-deterministic-v0.3.0",
  feature_schema: "t21-safe-feature-schema-v0.2",
  data_source: "Synthetic fixtures and non-DS public waveform integration placeholder",
  source_population: "Non-DS research data only; synthetic scenarios are not a population",
  ds_data_availability:
    "No DS-specific calibration or validation cohort is included in this build.",
  known_limitations: [
    "Research index thresholds are demonstration values and are not clinical action thresholds.",
    "Public waveform cases are not verified as Down syndrome cases.",
    "Missing or low-quality signals can invalidate the index.",
    "Medication metadata is displayed only as a time-aligned research annotation.",
  ],
  evidence_id: "EVD-T21S-UI-0003",
  dataset_license: "Per-source terms; synthetic fixtures contain no patient data",
  model_card_url: "/docs/model-card.html",
  protocol_url: "/docs/research-protocol.html",
};

function wave(length: number, phase: number, shape: "ecg" | "ppg" | "abp", noise = 0.02) {
  return Array.from({ length }, (_, index) => {
    const x = (index + phase) % 50;
    const jitter = Math.sin((index + phase) * 1.93) * noise;
    if (shape === "ecg") {
      const qrs = x === 3 ? -0.25 : x === 4 ? 1 : x === 5 ? -0.4 : 0;
      return qrs + Math.sin((index + phase) / 8) * 0.08 + jitter;
    }
    const pulse = Math.max(0, Math.sin((x / 50) * Math.PI * 2));
    if (shape === "ppg") return pulse ** 2 * 0.9 + jitter;
    return 65 + pulse ** 1.5 * 42 + jitter * 8;
  });
}

function resolveRisk(
  scenario: ScenarioId,
  timestampMs: number,
  calibrated: boolean,
): {
  score: number | null;
  level: RiskLevel;
  valid: boolean;
  confidence: number;
  reasons: string[];
} {
  if (!calibrated) {
    return {
      score: null,
      level: "BASELINE",
      valid: false,
      confidence: 0,
      reasons: ["Baseline calibration is still in progress."],
    };
  }
  if (scenario === "artifact_case" && timestampMs >= 220_000) {
    return {
      score: null,
      level: "INVALID",
      valid: false,
      confidence: 0.16,
      reasons: ["ECG motion artifact", "Signal quality is insufficient."],
    };
  }
  if (scenario === "missing_signal_case") {
    return {
      score: null,
      level: "INVALID",
      valid: false,
      confidence: 0.28,
      reasons: ["PPG signal is unavailable", "Composite input requirements are not met."],
    };
  }
  const elapsed = Math.max(0, timestampMs - 180_000);
  if (scenario === "progressive_instability") {
    const score = Math.min(82, 18 + elapsed / 3_200);
    return {
      score: Math.round(score),
      level: score >= 65 ? "ELEVATED" : score >= 38 ? "WATCH" : "STABLE",
      valid: true,
      confidence: 0.88,
      reasons:
        score >= 38
          ? [
              "Heart rate is declining from baseline.",
              "MAP trend is declining.",
              "PPG amplitude is reduced.",
            ]
          : ["Signals remain near the calibrated baseline."],
    };
  }
  if (scenario === "recovery_case") {
    const peak = elapsed < 120_000 ? 20 + elapsed / 2_000 : 80 - (elapsed - 120_000) / 2_300;
    const score = Math.max(22, Math.min(80, peak));
    return {
      score: Math.round(score),
      level: score >= 65 ? "ELEVATED" : score >= 38 ? "WATCH" : "STABLE",
      valid: true,
      confidence: 0.86,
      reasons:
        elapsed < 120_000
          ? ["Sustained hemodynamic trend moved away from baseline."]
          : ["Current values are returning toward the calibrated baseline."],
    };
  }
  return {
    score: 18 + Math.round(Math.sin(timestampMs / 35_000) * 3),
    level: "STABLE",
    valid: true,
    confidence: 0.92,
    reasons: ["Signals remain near the calibrated baseline."],
  };
}

export function createMockFrame(
  scenario: ScenarioId,
  timestampMs: number,
  mode: StreamFrame["mode"] = "GENERIC_VALIDATION_MODE",
): StreamFrame {
  const progress = Math.min(1, timestampMs / 180_000);
  const calibrated = progress >= 1;
  const risk = resolveRisk(scenario, timestampMs, calibrated);
  const elapsed = Math.max(0, timestampMs - 180_000);
  const deterioration = scenario === "progressive_instability" ? Math.min(1, elapsed / 220_000) : 0;
  const recovering =
    scenario === "recovery_case" ? Math.max(0, 1 - Math.abs(elapsed - 120_000) / 150_000) : 0;
  const effect = Math.max(deterioration, recovering);
  const artifact = scenario === "artifact_case" && timestampMs >= 220_000;
  const ppgMissing = scenario === "missing_signal_case";
  const overallQuality = artifact ? 0.18 : ppgMissing ? 0.58 : 0.94;
  const hr = Math.round(76 - effect * 18 + Math.sin(timestampMs / 15_000));
  const map = Math.round(82 - effect * 25 + Math.sin(timestampMs / 19_000) * 2);
  const ppgAmplitude = Number((0.92 - effect * 0.42).toFixed(2));
  const events: NonNullable<StreamFrame["events"]> = [
    { id: "baseline", timestamp_ms: 0, type: "BASELINE", label: "Baseline calibration" },
  ];
  if (timestampMs >= 180_000) {
    events.push({
      id: "baseline-complete",
      timestamp_ms: 180_000,
      type: "BASELINE",
      label: "Baseline established",
    });
  }
  if (scenario === "progressive_instability" && timestampMs >= 260_000) {
    events.push({
      id: "candidate-1",
      timestamp_ms: 260_000,
      type: "CANDIDATE",
      label: "Sustained trend candidate",
    });
  }
  if (scenario === "progressive_instability" && timestampMs >= 300_000) {
    events.push({
      id: "medication-metadata",
      timestamp_ms: 300_000,
      type: "MEDICATION",
      label: "Medication event metadata (source record only)",
    });
  }
  if (artifact) {
    events.push({
      id: "signal-loss",
      timestamp_ms: 220_000,
      type: "SIGNAL_LOSS",
      label: "ECG artifact / index suppressed",
    });
  }

  return {
    timestamp_ms: timestampMs,
    mode,
    source: {
      scenario_id: scenario,
      synthetic: scenario !== "vitaldb_public_demo",
      replay_speed: 20,
    },
    patient_context: { ...DEFAULT_PATIENT_CONTEXT },
    signals: {
      ecg: {
        value: hr,
        unit: "bpm",
        samples: wave(420, Math.round(timestampMs / 20), "ecg", artifact ? 0.38 : 0.02),
        sample_rate_hz: 250,
        available: true,
      },
      ppg: {
        value: ppgMissing ? null : ppgAmplitude,
        unit: "a.u.",
        samples: ppgMissing ? [] : wave(420, Math.round(timestampMs / 25), "ppg"),
        sample_rate_hz: 100,
        available: !ppgMissing,
      },
      abp: {
        value: map,
        unit: "mmHg",
        samples: wave(420, Math.round(timestampMs / 20), "abp"),
        sample_rate_hz: 125,
        available: true,
      },
      spo2: { value: 97 - Math.round(effect * 2), unit: "%", samples: [], available: true },
      etco2: { value: 36, unit: "mmHg", samples: [], available: true },
    },
    quality: {
      usable: !artifact && !ppgMissing,
      reasons: artifact ? ["ECG motion artifact"] : ppgMissing ? ["PPG absent"] : [],
      overall: overallQuality,
      by_signal: { ECG: artifact ? 0.18 : 0.96, PPG: ppgMissing ? 0 : 0.92, ABP: 0.95 },
    },
    baseline: {
      calibrated,
      progress,
      stable: true,
      values: { hr: 76, map: 82, ppg_amplitude: 0.92, rmssd: 31, sdnn: 42 },
      confidence: calibrated ? 0.91 : progress * 0.91,
      failure_reasons: [],
    },
    features: {
      hr,
      hr_slope: Number((-effect * 1.8).toFixed(1)),
      map,
      map_slope: Number((-effect * 2.4).toFixed(1)),
      ppg_amplitude: ppgMissing ? null : ppgAmplitude,
      rmssd: Math.round(31 - effect * 9),
      sdnn: Math.round(42 - effect * 11),
      spo2: 97 - Math.round(effect * 2),
      etco2: 36,
      respiratory_rate: 14,
      beat_confidence: artifact ? 0.18 : 0.96,
      ptt: ppgMissing ? null : 228 + Math.round(effect * 16),
    },
    risk: {
      name: "Research Instability Index",
      ...risk,
      population_validated_on: "non-DS research data only",
    },
    events,
    disclaimer: DISCLAIMER,
  };
}

export function isScenarioId(value: string): value is ScenarioId {
  return MOCK_CASES.some((item) => item.id === value);
}
