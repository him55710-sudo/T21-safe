export function BackendStatus({ healthy, demoMode }: { healthy: boolean; demoMode: boolean }) {
  const label = healthy
    ? "Backend connected"
    : demoMode
      ? "Local mock active"
      : "Backend unavailable";
  return (
    <div
      className={`backend-status ${healthy ? "is-connected" : demoMode ? "is-mock" : "is-offline"}`}
    >
      <span className="status-dot" aria-hidden="true" />
      <div>
        <strong>{label}</strong>
        <span>
          {healthy
            ? "FastAPI contract reachable"
            : demoMode
              ? "No backend required"
              : "Check API URL"}
        </span>
      </div>
    </div>
  );
}
