import type { StreamFrame } from "@/lib/contracts";
import type { ResearchAnnotation } from "@/hooks/useMonitoringSession";

const MAX_TIMELINE_MS = 600_000;

function formatTime(ms: number) {
  const seconds = Math.floor(ms / 1000);
  return `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
}

export function EventTimeline({
  frame,
  annotations,
  compact = false,
}: {
  frame: StreamFrame;
  annotations: ResearchAnnotation[];
  compact?: boolean;
}) {
  const events = [
    ...(frame.events ?? []),
    ...annotations.map((item) => ({
      id: item.id,
      timestamp_ms: item.timestampMs,
      type: "ANNOTATION" as const,
      label: item.text,
    })),
  ];
  return (
    <section
      className={`event-timeline ${compact ? "event-timeline--compact" : ""}`}
      aria-label="Research event timeline"
    >
      <div className="timeline-heading">
        <div>
          <span className="eyebrow">EVENT TIMELINE</span>
          <strong>{formatTime(frame.timestamp_ms)} elapsed</strong>
        </div>
        <div className="timeline-legend">
          <span className="baseline">Baseline</span>
          <span className="candidate">Candidate event</span>
          <span className="loss">Signal loss</span>
          <span className="annotation">Annotation</span>
        </div>
      </div>
      <div className="timeline-track">
        <span
          className="baseline-region"
          style={{ width: `${(180_000 / MAX_TIMELINE_MS) * 100}%` }}
        >
          BASELINE · 180 s
        </span>
        {events.map((event) => (
          <button
            type="button"
            key={event.id}
            className={`timeline-event timeline-event--${event.type.toLowerCase()}`}
            style={{ left: `${Math.min(98, (event.timestamp_ms / MAX_TIMELINE_MS) * 100)}%` }}
            title={`${formatTime(event.timestamp_ms)} — ${event.label}`}
            aria-label={`${formatTime(event.timestamp_ms)} ${event.label}`}
          />
        ))}
        <span
          className="timeline-cursor"
          style={{ left: `${Math.min(100, (frame.timestamp_ms / MAX_TIMELINE_MS) * 100)}%` }}
        />
      </div>
      {!compact ? (
        <div className="timeline-list">
          {events.slice(-5).map((event) => (
            <div key={event.id}>
              <time>{formatTime(event.timestamp_ms)}</time>
              <span>{event.type.replace("_", " ")}</span>
              <p>{event.label}</p>
            </div>
          ))}
        </div>
      ) : null}
    </section>
  );
}
