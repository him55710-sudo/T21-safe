import type { StreamFrame } from "@/lib/contracts";

export function ResearchRiskGauge({
  risk,
  qualityUsable,
}: {
  risk: StreamFrame["risk"];
  qualityUsable: boolean;
}) {
  const invalid = !risk.valid || !qualityUsable || risk.score === null;
  const baselinePending = risk.level === "BASELINE";
  const displayedLevel = baselinePending ? "BASELINE" : invalid ? "INVALID" : risk.level;
  const score = risk.score ?? 0;
  const angle = Math.min(180, Math.max(0, score * 1.8));
  return (
    <section
      className={`risk-gauge risk-gauge--${displayedLevel.toLowerCase()} ${invalid ? "is-invalid" : ""}`}
      aria-label={`${risk.name}: ${baselinePending ? "baseline pending" : invalid ? "invalid" : score}`}
    >
      <div className="risk-heading">
        <span>RESEARCH INSTABILITY INDEX</span>
        <span className="level-pill">{displayedLevel}</span>
      </div>
      {invalid ? (
        <div className="invalid-score">
          <span aria-hidden="true">×</span>
          <strong>{baselinePending ? "AWAITING BASELINE" : "INDEX HIDDEN"}</strong>
          <p>
            {baselinePending
              ? "Baseline calibration is not complete."
              : "Signal or baseline requirements are not met."}
          </p>
        </div>
      ) : (
        <div className="gauge-visual">
          <div className="gauge-arc">
            <span style={{ transform: `rotate(${angle}deg)` }} />
          </div>
          <div className="gauge-value">
            <strong>{score}</strong>
            <span>/ 100</span>
          </div>
        </div>
      )}
      <div className="risk-confidence">
        <span>Confidence</span>
        <strong>{Math.round(risk.confidence * 100)}%</strong>
      </div>
    </section>
  );
}
