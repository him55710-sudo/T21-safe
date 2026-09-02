import type { StreamFrame } from "@/lib/contracts";

interface FeatureRow {
  key: string;
  label: string;
  unit: string;
  baselineKey: string;
  explanation: string;
}

const GROUPS: Array<{ title: string; description: string; rows: FeatureRow[] }> = [
  {
    title: "Rhythm and Autonomic Trend",
    description: "Beat timing and autonomic features relative to the established baseline.",
    rows: [
      {
        key: "hr",
        label: "Heart rate",
        unit: "bpm",
        baselineKey: "hr",
        explanation: "Current beat rate compared with the subject-specific reference.",
      },
      {
        key: "hr_slope",
        label: "HR slope",
        unit: "bpm/min",
        baselineKey: "zero",
        explanation: "Direction and persistence of recent heart-rate movement.",
      },
      {
        key: "rmssd",
        label: "RMSSD",
        unit: "ms",
        baselineKey: "rmssd",
        explanation: "Short-term beat interval variability; shown only as a research feature.",
      },
      {
        key: "sdnn",
        label: "SDNN",
        unit: "ms",
        baselineKey: "sdnn",
        explanation: "Overall beat interval variation within the analysis window.",
      },
      {
        key: "beat_confidence",
        label: "Beat confidence",
        unit: "%",
        baselineKey: "confidence",
        explanation: "Confidence that detected beats support feature calculation.",
      },
    ],
  },
  {
    title: "Perfusion and Hemodynamics",
    description: "Pressure and peripheral pulse changes; no treatment action is inferred.",
    rows: [
      {
        key: "map",
        label: "MAP",
        unit: "mmHg",
        baselineKey: "map",
        explanation: "Current mean arterial pressure compared with baseline.",
      },
      {
        key: "map_slope",
        label: "MAP slope",
        unit: "mmHg/min",
        baselineKey: "zero",
        explanation: "Recent direction of pressure change.",
      },
      {
        key: "ppg_amplitude",
        label: "PPG amplitude",
        unit: "a.u.",
        baselineKey: "ppg_amplitude",
        explanation: "Relative peripheral pulse amplitude; sensor placement can affect this value.",
      },
      {
        key: "ptt",
        label: "Pulse transit time",
        unit: "ms",
        baselineKey: "ptt",
        explanation: "Displayed only when ECG and PPG timing are both valid.",
      },
    ],
  },
  {
    title: "Respiration and Oxygenation",
    description: "Available respiratory and gas-exchange context.",
    rows: [
      {
        key: "spo2",
        label: "SpO₂",
        unit: "%",
        baselineKey: "spo2",
        explanation: "Oxygen saturation input from the replay source.",
      },
      {
        key: "etco2",
        label: "EtCO₂",
        unit: "mmHg",
        baselineKey: "etco2",
        explanation: "End-tidal carbon dioxide input when available.",
      },
      {
        key: "respiratory_rate",
        label: "Respiratory rate",
        unit: "breaths/min",
        baselineKey: "respiratory_rate",
        explanation: "Respiratory signal-derived rate when a valid source is present.",
      },
    ],
  },
];

function displayValue(value: number | null | undefined, unit: string) {
  if (value === null || value === undefined) return "Missing";
  const shown = unit === "%" && value <= 1 ? Math.round(value * 100) : value;
  return `${shown} ${unit}`;
}

export function BaselineDeltaTable({ frame }: { frame: StreamFrame }) {
  const baselines = frame.baseline.values ?? {};
  return (
    <div className="feature-groups">
      {GROUPS.map((group) => (
        <section className="feature-group" key={group.title}>
          <div className="feature-group__heading">
            <div>
              <h2>{group.title}</h2>
              <p>{group.description}</p>
            </div>
            <span>{group.rows.length} FEATURES</span>
          </div>
          <div className="feature-table" role="table" aria-label={group.title}>
            <div className="feature-row feature-row--header" role="row">
              <span>Feature</span>
              <span>Current</span>
              <span>Baseline</span>
              <span>Delta</span>
              <span>Quality / direction</span>
              <span>Explanation</span>
            </div>
            {group.rows.map((row) => {
              const current = frame.features[row.key];
              const baseline =
                row.baselineKey === "zero"
                  ? 0
                  : row.baselineKey === "confidence"
                    ? 1
                    : baselines[row.baselineKey];
              const delta =
                current === null ||
                current === undefined ||
                baseline === null ||
                baseline === undefined
                  ? null
                  : current - baseline;
              const direction =
                delta === null
                  ? "—"
                  : delta > 0.5
                    ? "↑ positive"
                    : delta < -0.5
                      ? "↓ negative"
                      : "→ neutral";
              return (
                <div className="feature-row" role="row" key={row.key}>
                  <strong>{row.label}</strong>
                  <span>{displayValue(current, row.unit)}</span>
                  <span>{displayValue(baseline, row.unit)}</span>
                  <span>
                    {delta === null
                      ? "—"
                      : `${delta > 0 ? "+" : ""}${Number(delta.toFixed(2))} ${row.unit}`}
                  </span>
                  <span>
                    <em
                      className={`direction direction--${direction.includes("negative") ? "down" : direction.includes("positive") ? "up" : "neutral"}`}
                    >
                      {direction}
                    </em>
                    <small>{Math.round((frame.quality.overall ?? 0) * 100)}% quality</small>
                  </span>
                  <p>{row.explanation}</p>
                </div>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}
