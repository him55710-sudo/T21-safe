import { z } from "zod";
import {
  caseSchema,
  evidenceSchema,
  streamFrameSchema,
  type Evidence,
  type ResearchCase,
  type StreamFrame,
} from "@/lib/contracts";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const backendCaseSchema = z.object({
  case_id: z.string(),
  title: z.string(),
  source: z.string(),
  data_type: z.string(),
  available_signals: z.array(z.string()),
  is_synthetic: z.boolean(),
  ds_status: z.string(),
  clinical_use_allowed: z.boolean(),
  attribution: z.string(),
});

const backendEvidenceSchema = z.object({
  model_version: z.string(),
  feature_schema_version: z.string(),
  clinical_validation: z.boolean(),
  items: z.array(
    z.object({
      evidence_id: z.string(),
      feature_or_model: z.string(),
      citation: z.string(),
      url: z.string(),
      applicability: z.string(),
      limitation: z.string(),
    }),
  ),
});

const nullableNumber = z.number().nullable();
const backendStreamFrameSchema = z.object({
  timestamp_ms: z.number().nonnegative(),
  mode: z.enum(["GENERIC_VALIDATION_MODE", "DS_HYPOTHESIS_MODE"]),
  source: z.object({
    dataset: z.string(),
    case_id: z.string(),
    is_synthetic: z.boolean(),
    attribution: z.string(),
    data_type: z.string(),
  }),
  patient_context: z.object({ ds_status: z.string(), age_group: z.string() }),
  signals: z.object({
    ecg_ii: z.array(nullableNumber),
    ppg: z.array(nullableNumber),
    abp: z.array(nullableNumber),
    hr_bpm: nullableNumber,
    sbp_mm_hg: nullableNumber,
    dbp_mm_hg: nullableNumber,
    map_mm_hg: nullableNumber,
    spo2_pct: nullableNumber,
    etco2_mm_hg: nullableNumber,
  }),
  quality: z.object({
    ecg_sqi: nullableNumber,
    ppg_sqi: nullableNumber,
    abp_sqi: nullableNumber,
    usable: z.boolean(),
    unavailable_signals: z.array(z.string()),
    reasons: z.array(z.string()),
    gap_fraction: z.number().min(0).max(1),
    timestamp_synchronized: z.boolean(),
  }),
  baseline: z.object({
    calibrated: z.boolean(),
    progress: z.number().min(0).max(1),
    confidence: z.number().min(0).max(1),
    reasons: z.array(z.string()),
    values: z.record(z.string(), nullableNumber),
  }),
  features: z.record(z.string(), nullableNumber),
  risk: z.object({
    name: z.literal("Research Instability Index"),
    score: nullableNumber,
    level: z.enum(["BASELINE", "STABLE", "WATCH", "ELEVATED", "HIGH", "INVALID"]),
    valid: z.boolean(),
    observation_context_seconds: z.number().positive(),
    confidence: z.number().min(0).max(1),
    reasons: z.array(z.string()),
    model_version: z.string(),
    population_validated_on: z.string(),
    limitations: z.array(z.string()),
  }),
  transport: z.record(z.string(), z.unknown()),
  provenance: z.record(z.string(), z.unknown()),
  disclaimer: z.literal(
    "Research prototype; not for diagnosis, treatment, dosing, or clinical monitoring.",
  ),
});

async function fetchJson<T>(
  path: string,
  schema: { parse: (value: unknown) => T },
  init?: RequestInit,
) {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return schema.parse(await response.json());
}

function caseKind(value: z.infer<typeof backendCaseSchema>): ResearchCase["kind"] {
  if (value.is_synthetic) return "SYNTHETIC";
  if (/vitaldb|physionet|wfdb/.test(value.source.toLowerCase())) return "VITALDB_PUBLIC";
  return "LOCAL_FIXTURE";
}

function caseLicense(value: z.infer<typeof backendCaseSchema>): string {
  if (value.is_synthetic) return "Locally generated synthetic data; no patient dataset license.";
  if (value.source.toLowerCase().includes("vitaldb")) {
    return "VitalDB Open Dataset: CC BY 4.0; source terms apply.";
  }
  if (value.source.toLowerCase().includes("physionet")) {
    return "Source-specific PhysioNet license; verify the dataset manifest.";
  }
  return "Repository development fixture; not clinical data.";
}

function normalizeCase(value: z.infer<typeof backendCaseSchema>): ResearchCase {
  return caseSchema.parse({
    id: value.case_id,
    name: value.title,
    kind: caseKind(value),
    description: `${value.data_type}; available signals: ${value.available_signals.join(", ")}. Research replay only.`,
    attribution: value.attribution,
    license: caseLicense(value),
    verified_ds: false,
  });
}

function normalizeEvidence(value: z.infer<typeof backendEvidenceSchema>): Evidence {
  return evidenceSchema.parse({
    model_version: value.model_version,
    feature_schema: value.feature_schema_version,
    data_source: "Versioned repository evidence registry",
    source_population: value.items.map((item) => item.applicability).join(" "),
    ds_data_availability: value.clinical_validation
      ? "Clinical validation is recorded; inspect the signed evidence package."
      : "No DS-specific calibration or clinical validation cohort is included.",
    known_limitations: value.items.map((item) => item.limitation),
    evidence_id: value.items.map((item) => item.evidence_id).join(", "),
    dataset_license: "Source-specific licenses apply; see research/dataset_registry.yaml.",
    model_card_url: "/docs/model-card.html",
    protocol_url: "/docs/research-protocol.html",
  });
}

function finiteRange(values: Array<number | null>): number | null {
  const finite = values.filter((value): value is number => value !== null);
  if (!finite.length) return null;
  return Math.max(...finite) - Math.min(...finite);
}

function normalizeStreamFrame(value: unknown): StreamFrame {
  const frame = backendStreamFrameSchema.parse(value);
  const qualityValues = [
    frame.quality.ecg_sqi,
    frame.quality.ppg_sqi,
    frame.quality.abp_sqi,
  ].filter((item): item is number => item !== null);
  const overall = qualityValues.length
    ? qualityValues.reduce((sum, item) => sum + item, 0) / qualityValues.length
    : 0;
  const ppgAmplitude = finiteRange(frame.signals.ppg);

  return streamFrameSchema.parse({
    timestamp_ms: frame.timestamp_ms,
    mode: frame.mode,
    source: frame.source,
    patient_context: frame.patient_context,
    signals: {
      ecg: {
        value: frame.signals.hr_bpm,
        unit: "mV",
        samples: frame.signals.ecg_ii.filter((item): item is number => item !== null),
        available: frame.signals.ecg_ii.length > 0,
      },
      ppg: {
        value: ppgAmplitude,
        unit: "a.u.",
        samples: frame.signals.ppg.filter((item): item is number => item !== null),
        available: frame.signals.ppg.length > 0,
      },
      abp: {
        value: frame.signals.map_mm_hg,
        unit: "mmHg",
        samples: frame.signals.abp.filter((item): item is number => item !== null),
        available: frame.signals.abp.length > 0,
      },
      spo2: { value: frame.signals.spo2_pct, unit: "%", samples: [], available: true },
      etco2: { value: frame.signals.etco2_mm_hg, unit: "mmHg", samples: [], available: true },
    },
    quality: {
      usable: frame.quality.usable,
      reasons: frame.quality.reasons,
      overall,
      by_signal: {
        ECG: frame.quality.ecg_sqi ?? 0,
        PPG: frame.quality.ppg_sqi ?? 0,
        ABP: frame.quality.abp_sqi ?? 0,
      },
    },
    baseline: {
      calibrated: frame.baseline.calibrated,
      progress: frame.baseline.progress,
      stable: frame.baseline.calibrated && frame.quality.usable,
      values: frame.baseline.values,
      confidence: frame.baseline.confidence,
      failure_reasons: frame.baseline.reasons,
    },
    features: {
      ...frame.features,
      hr: frame.signals.hr_bpm,
      map: frame.signals.map_mm_hg,
      ppg_amplitude: ppgAmplitude,
    },
    risk: frame.risk,
    disclaimer: frame.disclaimer,
  });
}

export async function getBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(2_500) });
    return response.ok;
  } catch {
    return false;
  }
}

export async function getCases(): Promise<ResearchCase[]> {
  const cases = await fetchJson("/v1/cases", backendCaseSchema.array());
  return cases.map(normalizeCase);
}

export async function getEvidence(): Promise<Evidence> {
  return normalizeEvidence(await fetchJson("/v1/evidence", backendEvidenceSchema));
}

export async function startReplay(
  caseId: string,
  mode: StreamFrame["mode"],
  speed = 40,
): Promise<string> {
  const response = await fetch(`${API_URL}/v1/replays`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      case_id: caseId,
      mode,
      speed,
      baseline_seconds: 180,
    }),
  });
  if (!response.ok) throw new Error(`Replay start failed: ${response.status}`);
  const body = (await response.json()) as { session_id?: unknown };
  if (typeof body.session_id !== "string") throw new Error("Replay response has no session_id");
  return body.session_id;
}

export function openValidatedEventStream(
  sessionId: string,
  onFrame: (frame: StreamFrame) => void,
  onConnection: (connected: boolean) => void,
  onComplete: () => void = () => undefined,
) {
  let source: EventSource | null = null;
  let closed = false;
  let retryTimer: ReturnType<typeof setTimeout> | undefined;
  let retryCount = 0;

  const connect = () => {
    if (closed) return;
    source = new EventSource(`${API_URL}/v1/stream/${encodeURIComponent(sessionId)}`);
    source.onopen = () => {
      retryCount = 0;
      onConnection(true);
    };
    const handleFrame = (event: MessageEvent<string>) => {
      try {
        onFrame(normalizeStreamFrame(JSON.parse(event.data) as unknown));
      } catch {
        // Ignore malformed SSE messages. A partial frame is never rendered.
      }
    };
    source.onmessage = handleFrame;
    source.addEventListener?.("signal", handleFrame as EventListener);
    source.addEventListener?.("end", () => {
      closed = true;
      source?.close();
      onConnection(false);
      onComplete();
    });
    source.onerror = () => {
      onConnection(false);
      source?.close();
      if (!closed) {
        retryCount += 1;
        retryTimer = setTimeout(connect, Math.min(5_000, 500 * 2 ** retryCount));
      }
    };
  };

  connect();
  return () => {
    closed = true;
    if (retryTimer) clearTimeout(retryTimer);
    source?.close();
  };
}
