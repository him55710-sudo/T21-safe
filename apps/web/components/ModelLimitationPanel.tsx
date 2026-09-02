export function ModelLimitationPanel({ mode }: { mode: string }) {
  return (
    <section className="limitation-panel">
      <span aria-hidden="true">i</span>
      <div>
        <strong>Population limitation</strong>
        <p>
          Current model evidence is from non-DS research data only. The index must be interpreted
          with complete patient context.
        </p>
        {mode === "DS_HYPOTHESIS_MODE" ? (
          <p data-testid="ds-disclaimer">
            <strong>DS HYPOTHESIS MODE:</strong> Candidate physiological features selected for
            future validation in patients with Down syndrome. No DS-specific calibration has been
            completed.
          </p>
        ) : null}
      </div>
    </section>
  );
}
