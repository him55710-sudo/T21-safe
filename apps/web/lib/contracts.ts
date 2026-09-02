import { z } from "zod";

export const DISCLAIMER =
  "Research prototype; not for diagnosis, treatment, dosing, or clinical monitoring.";

export const riskLevelSchema = z.enum([
  "BASELINE",
  "STABLE",
  "WATCH",
  "ELEVATED",
  "HIGH",
  "INVALID",
]);

export type RiskLevel = z.infer<typeof riskLevelSchema>;

const signalSchema = z.object({
  value: z.number().nullable(),
  unit: z.string(),
  samples: z.array(z.number()).default([]),
  sample_rate_hz: z.number().positive().optional(),
  available: z.boolean().default(true),
});

export const streamFrameSchema = z.object({
  timestamp_ms: z.number().nonnegative(),
  mode: z.enum(["GENERIC_VALIDATION_MODE", "DS_HYPOTHESIS_MODE"]),
  source: z.record(z.string(), z.unknown()),
  patient_context: z.record(z.string(), z.unknown()),
  signals: z.record(z.string(), signalSchema),
  quality: z.object({
    usable: z.boolean(),
    reasons: z.array(z.string()),
    overall: z.number().min(0).max(1).optional(),
    by_signal: z.record(z.string(), z.number().min(0).max(1)).optional(),
  }),
  baseline: z.object({
    calibrated: z.boolean(),
    progress: z.number().min(0).max(1),
    stable: z.boolean().optional(),
    values: z.record(z.string(), z.number().nullable()).optional(),
    confidence: z.number().min(0).max(1).optional(),
    failure_reasons: z.array(z.string()).optional(),
  }),
  features: z.record(z.string(), z.number().nullable()),
  risk: z.object({
    name: z.literal("Research Instability Index"),
    score: z.number().min(0).max(100).nullable(),
    level: riskLevelSchema,
    valid: z.boolean(),
    confidence: z.number().min(0).max(1),
    reasons: z.array(z.string()),
    population_validated_on: z.string(),
  }),
  events: z
    .array(
      z.object({
        id: z.string(),
        timestamp_ms: z.number(),
        type: z.enum(["BASELINE", "CANDIDATE", "SIGNAL_LOSS", "ANNOTATION", "MEDICATION"]),
        label: z.string(),
      }),
    )
    .optional(),
  disclaimer: z.literal(DISCLAIMER),
});

export type StreamFrame = z.infer<typeof streamFrameSchema>;
export type SignalDatum = z.infer<typeof signalSchema>;

export const caseSchema = z.object({
  id: z.string(),
  name: z.string(),
  kind: z.enum(["VITALDB_PUBLIC", "SYNTHETIC", "LOCAL_FIXTURE"]),
  description: z.string(),
  attribution: z.string(),
  license: z.string(),
  verified_ds: z.boolean(),
});

export type ResearchCase = z.infer<typeof caseSchema>;

export const evidenceSchema = z.object({
  model_version: z.string(),
  feature_schema: z.string(),
  data_source: z.string(),
  source_population: z.string(),
  ds_data_availability: z.string(),
  known_limitations: z.array(z.string()),
  evidence_id: z.string(),
  dataset_license: z.string(),
  model_card_url: z.string(),
  protocol_url: z.string(),
});

export type Evidence = z.infer<typeof evidenceSchema>;

export interface PatientContext {
  studySubjectId: string;
  ageGroup: string;
  weightRange: string;
  dsStatus: "confirmed by clinical record" | "not confirmed" | "unknown";
  congenitalHeartDisease: "yes" | "no" | "unknown";
  obstructiveSleepApnea: "yes" | "no" | "unknown";
  previousAnesthesiaComplication: "yes" | "no" | "unknown";
  anesthesiaType: string;
  availableSignals: string[];
}

export const DEFAULT_PATIENT_CONTEXT: PatientContext = {
  studySubjectId: "RSP-0241",
  ageGroup: "Adult (18–64 years)",
  weightRange: "60–79 kg",
  dsStatus: "unknown",
  congenitalHeartDisease: "unknown",
  obstructiveSleepApnea: "unknown",
  previousAnesthesiaComplication: "unknown",
  anesthesiaType: "General anesthesia — metadata only",
  availableSignals: ["ECG", "PPG", "ABP", "SpO₂", "EtCO₂"],
};
