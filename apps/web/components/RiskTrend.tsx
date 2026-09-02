import type { StreamFrame } from "@/lib/contracts";

export function RiskTrend({ history }: { history: StreamFrame[] }) {
  const valid = history.filter((item) => item.risk.score !== null).slice(-24);
  const first = valid.at(0)?.risk.score;
  const last = valid.at(-1)?.risk.score;
  const delta = first == null || last == null ? 0 : last - first;
  const direction = delta > 4 ? "↑ INCREASING" : delta < -4 ? "↓ DECREASING" : "→ STABLE";
  const points = valid
    .map(
      (item, index) =>
        `${(index / Math.max(1, valid.length - 1)) * 100},${40 - (item.risk.score ?? 0) * 0.35}`,
    )
    .join(" ");
  return (
    <div className="risk-trend" role="group" aria-label={`Risk trend ${direction.toLowerCase()}`}>
      <div>
        <span>Trend</span>
        <strong>{direction}</strong>
        <small>Sustained window · not a single spike</small>
      </div>
      <svg viewBox="0 0 100 44" role="img" aria-label="Research index recent trend">
        <polyline points={points || "0,34 100,34"} />
      </svg>
    </div>
  );
}
