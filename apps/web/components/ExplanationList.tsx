export function ExplanationList({ reasons }: { reasons: string[] }) {
  return (
    <section className="explanation-list">
      <span className="eyebrow">TOP REASONS FOR INDEX MOVEMENT</span>
      {reasons.length > 0 ? (
        <ol>
          {reasons.map((reason, index) => (
            <li key={reason}>
              <span>{index + 1}</span>
              {reason}
            </li>
          ))}
        </ol>
      ) : (
        <p>No reason is available for this frame.</p>
      )}
    </section>
  );
}
