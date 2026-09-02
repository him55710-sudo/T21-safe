export function SignalQualityBadge({
  value,
  label = "Signal quality",
}: {
  value: number;
  label?: string;
}) {
  const state = value >= 0.8 ? "GOOD" : value >= 0.5 ? "DEGRADED" : "INSUFFICIENT";
  const icon = state === "GOOD" ? "✓" : state === "DEGRADED" ? "△" : "×";
  return (
    <span
      className={`quality-badge quality-badge--${state.toLowerCase()}`}
      role="img"
      aria-label={`${label}: ${state}, ${Math.round(value * 100)} percent`}
    >
      <span aria-hidden="true">{icon}</span>
      <span>{state}</span>
      <strong>{Math.round(value * 100)}%</strong>
    </span>
  );
}
