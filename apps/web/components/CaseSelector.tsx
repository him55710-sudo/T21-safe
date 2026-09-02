import type { ResearchCase } from "@/lib/contracts";

export function CaseSelector({
  cases,
  selectedId,
  onSelect,
}: {
  cases: ResearchCase[];
  selectedId: string;
  onSelect: (id: string) => void;
}) {
  return (
    <fieldset className="case-selector">
      <legend>Data source</legend>
      {cases.map((item) => (
        <label
          key={item.id}
          className={`case-option ${item.id === selectedId ? "is-selected" : ""}`}
        >
          <input
            type="radio"
            name="research-case"
            value={item.id}
            checked={item.id === selectedId}
            onChange={() => onSelect(item.id)}
          />
          <span className={`source-chip source-chip--${item.kind.toLowerCase()}`}>
            {item.kind.replaceAll("_", " ")}
          </span>
          <strong>{item.name}</strong>
          <small>{item.description}</small>
        </label>
      ))}
    </fieldset>
  );
}
