import type { StreamFrame } from "@/lib/contracts";
import { SignalQualityBadge } from "@/components/SignalQualityBadge";

export function BaselineCalibrationPanel({ frame }: { frame: StreamFrame }) {
  const percent = Math.round(frame.baseline.progress * 100);
  const seconds = Math.round(frame.baseline.progress * 180);
  const baseline = frame.baseline.values ?? {};
  const failed = (frame.baseline.failure_reasons?.length ?? 0) > 0;
  return (
    <section className="calibration-panel" aria-labelledby="calibration-title">
      <div
        className="calibration-orbit"
        style={{ "--progress": `${percent * 3.6}deg` } as React.CSSProperties}
      >
        <div>
          <strong>{seconds}</strong>
          <span>/ 180 s</span>
        </div>
      </div>
      <div className="calibration-content">
        <span className="eyebrow">PATIENT-SPECIFIC BASELINE</span>
        <h2 id="calibration-title">
          {failed ? "Calibration could not be established" : "Establishing a stable reference"}
        </h2>
        <p>
          Risk output remains hidden until signal availability, quality, and baseline stability
          requirements are met.
        </p>
        <div
          className="progress-track"
          aria-label={`Calibration progress ${percent} percent`}
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={percent}
        >
          <span style={{ width: `${percent}%` }} />
        </div>
        <div className="calibration-metrics">
          <div>
            <span>Available</span>
            <strong>
              {Object.values(frame.signals).filter((signal) => signal.available).length} signals
            </strong>
          </div>
          <div>
            <span>Baseline state</span>
            <strong>{frame.baseline.stable === false ? "UNSTABLE" : "STABLE SO FAR"}</strong>
          </div>
          <div>
            <span>Confidence</span>
            <strong>{Math.round((frame.baseline.confidence ?? 0) * 100)}%</strong>
          </div>
          <SignalQualityBadge value={frame.quality.overall ?? 0} />
        </div>
        <div className="baseline-preview">
          <div>
            <span>HR</span>
            <strong>
              {baseline.hr ?? "—"} <small>bpm</small>
            </strong>
          </div>
          <div>
            <span>MAP</span>
            <strong>
              {baseline.map ?? "—"} <small>mmHg</small>
            </strong>
          </div>
          <div>
            <span>PPG amplitude</span>
            <strong>
              {baseline.ppg_amplitude ?? "—"} <small>a.u.</small>
            </strong>
          </div>
          <div>
            <span>RMSSD</span>
            <strong>
              {baseline.rmssd ?? "—"} <small>ms</small>
            </strong>
          </div>
        </div>
        {failed ? (
          <div className="invalid-panel">
            <strong>Index unavailable</strong>
            {frame.baseline.failure_reasons?.join(" · ")}
          </div>
        ) : null}
      </div>
    </section>
  );
}
