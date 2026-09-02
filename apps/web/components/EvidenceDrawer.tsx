import type { Evidence } from "@/lib/contracts";

export function EvidenceDrawer({
  evidence,
  onClose,
  embedded = false,
}: {
  evidence: Evidence;
  onClose?: () => void;
  embedded?: boolean;
}) {
  return (
    <aside
      className={`evidence-drawer ${embedded ? "evidence-drawer--embedded" : ""}`}
      aria-labelledby="evidence-title"
    >
      <div className="drawer-heading">
        <div>
          <span className="eyebrow">TRACEABILITY</span>
          <h2 id="evidence-title">Evidence & data</h2>
        </div>
        {onClose ? (
          <button
            className="icon-button"
            type="button"
            aria-label="Close evidence"
            onClick={onClose}
          >
            ×
          </button>
        ) : null}
      </div>
      <div className="evidence-id">
        <span>Evidence ID</span>
        <strong>{evidence.evidence_id}</strong>
      </div>
      <dl className="evidence-list">
        <div>
          <dt>Model version</dt>
          <dd>{evidence.model_version}</dd>
        </div>
        <div>
          <dt>Feature schema</dt>
          <dd>{evidence.feature_schema}</dd>
        </div>
        <div>
          <dt>Data source</dt>
          <dd>{evidence.data_source}</dd>
        </div>
        <div>
          <dt>Source population</dt>
          <dd>{evidence.source_population}</dd>
        </div>
        <div>
          <dt>DS data availability</dt>
          <dd>{evidence.ds_data_availability}</dd>
        </div>
        <div>
          <dt>Dataset license</dt>
          <dd>{evidence.dataset_license}</dd>
        </div>
      </dl>
      <section className="known-limitations">
        <h3>Known limitations</h3>
        <ul>
          {evidence.known_limitations.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
      <div className="drawer-actions">
        <a className="button button--ghost" href={evidence.model_card_url}>
          Model card
        </a>
        <a className="button button--ghost" href={evidence.protocol_url}>
          Research protocol
        </a>
      </div>
    </aside>
  );
}
