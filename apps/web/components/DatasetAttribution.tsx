import type { ResearchCase } from "@/lib/contracts";

export function DatasetAttribution({ researchCase }: { researchCase: ResearchCase }) {
  return (
    <section className="attribution-card" aria-labelledby="attribution-title">
      <div>
        <span className="eyebrow">DATA PROVENANCE</span>
        <h3 id="attribution-title">{researchCase.attribution}</h3>
        <p>{researchCase.license}</p>
      </div>
      {researchCase.kind === "VITALDB_PUBLIC" ? (
        <div className="safety-callout" data-testid="public-case-disclaimer">
          <strong>This case is not a verified Down syndrome case.</strong>
          <span>Used only to demonstrate signal processing.</span>
        </div>
      ) : (
        <div className="safety-callout safety-callout--synthetic">
          <strong>SYNTHETIC SCENARIO</strong>
          <span>No patient data. No claim of population validity.</span>
        </div>
      )}
    </section>
  );
}
