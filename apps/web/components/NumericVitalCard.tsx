export function NumericVitalCard({
  label,
  value,
  unit,
  tone,
}: {
  label: string;
  value: number | null | undefined;
  unit: string;
  tone: "green" | "blue" | "amber" | "violet";
}) {
  return (
    <div className={`vital-card vital-card--${tone}`}>
      <span>{label}</span>
      <strong>{value ?? "—"}</strong>
      <small>{unit}</small>
    </div>
  );
}
