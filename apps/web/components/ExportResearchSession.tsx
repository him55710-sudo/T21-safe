"use client";

function download(name: string, content: string, type: string) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function ExportResearchSession({ payload }: { payload: Record<string, unknown> }) {
  const exportJson = () =>
    download(
      "t21-safe-research-session.json",
      JSON.stringify(payload, null, 2),
      "application/json",
    );
  const exportCsv = () => {
    const latest = payload.latest_frame as
      | {
          timestamp_ms?: number;
          risk?: { score?: number | null; level?: string; valid?: boolean };
          features?: Record<string, number | null>;
        }
      | undefined;
    const rows = [
      ["timestamp_ms", "index_score", "level", "valid", "hr", "map", "ppg_amplitude"],
      [
        latest?.timestamp_ms ?? "",
        latest?.risk?.score ?? "",
        latest?.risk?.level ?? "",
        latest?.risk?.valid ?? "",
        latest?.features?.hr ?? "",
        latest?.features?.map ?? "",
        latest?.features?.ppg_amplitude ?? "",
      ],
    ];
    download(
      "t21-safe-research-session.csv",
      rows.map((row) => row.join(",")).join("\n"),
      "text/csv",
    );
  };
  const exportReport = () => {
    const html = `<!doctype html><meta charset="utf-8"><title>T21 Safe research session summary</title><h1>T21 Safe — research session summary</h1><p>Research prototype. Not for diagnosis, treatment, dosing, or clinical monitoring.</p><pre>${JSON.stringify(payload, null, 2).replaceAll("&", "&amp;").replaceAll("<", "&lt;")}</pre>`;
    download("t21-safe-research-summary.html", html, "text/html");
  };
  return (
    <div className="export-actions" aria-label="Export anonymized research session">
      <button className="button button--primary" type="button" onClick={exportJson}>
        Export anonymized JSON
      </button>
      <button className="button button--ghost" type="button" onClick={exportCsv}>
        Export CSV
      </button>
      <button className="button button--ghost" type="button" onClick={exportReport}>
        Export research summary
      </button>
    </div>
  );
}
