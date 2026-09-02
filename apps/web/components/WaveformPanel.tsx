"use client";

import { useEffect, useRef } from "react";
import type { SignalDatum } from "@/lib/contracts";
import { SignalQualityBadge } from "@/components/SignalQualityBadge";

const COLORS = { ECG: "#43e5b0", PPG: "#58c7ff", ABP: "#ffbb55" } as const;

export function WaveformPanel({
  label,
  signal,
  quality,
  paused,
  zoomed = false,
  artifact = false,
}: {
  label: keyof typeof COLORS;
  signal: SignalDatum;
  quality: number;
  paused: boolean;
  zoomed?: boolean;
  artifact?: boolean;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    if (paused) return;
    const ratio = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.floor(rect.width * ratio));
    canvas.height = Math.max(1, Math.floor(rect.height * ratio));
    context.scale(ratio, ratio);
    context.clearRect(0, 0, rect.width, rect.height);
    context.strokeStyle = "rgba(126, 154, 178, .12)";
    context.lineWidth = 1;
    for (let x = 0; x < rect.width; x += 32) {
      context.beginPath();
      context.moveTo(x, 0);
      context.lineTo(x, rect.height);
      context.stroke();
    }
    for (let y = 0; y < rect.height; y += 32) {
      context.beginPath();
      context.moveTo(0, y);
      context.lineTo(rect.width, y);
      context.stroke();
    }
    if (signal.samples.length < 2) return;
    let min = Infinity;
    let max = -Infinity;
    for (const sample of signal.samples) {
      if (sample < min) min = sample;
      if (sample > max) max = sample;
    }
    const range = Math.max(0.01, max - min);
    context.strokeStyle = COLORS[label];
    context.lineWidth = 1.7;
    context.shadowColor = COLORS[label];
    context.shadowBlur = 4;
    context.beginPath();
    signal.samples.forEach((sample, index) => {
      const x = (index / (signal.samples.length - 1)) * rect.width;
      const y = rect.height - ((sample - min) / range) * (rect.height * 0.72) - rect.height * 0.14;
      if (index === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    });
    context.stroke();
  }, [label, paused, signal.samples, zoomed]);

  return (
    <section
      className={`waveform-panel ${!signal.available ? "is-missing" : ""}`}
      aria-label={`${label} waveform`}
    >
      <div className="waveform-label">
        <div>
          <strong style={{ color: COLORS[label] }}>{label}</strong>
          <span>{signal.sample_rate_hz ?? "—"} Hz</span>
        </div>
        <SignalQualityBadge value={quality} label={`${label} signal quality`} />
      </div>
      {signal.available ? (
        <canvas ref={canvasRef} />
      ) : (
        <div className="waveform-missing">
          <strong>NO SIGNAL</strong>
          <span>{label} is unavailable</span>
        </div>
      )}
      {paused ? <span className="waveform-state">PAUSED</span> : null}
      {artifact ? <span className="artifact-marker">△ ARTIFACT</span> : null}
    </section>
  );
}
