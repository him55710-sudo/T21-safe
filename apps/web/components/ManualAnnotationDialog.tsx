"use client";

import { useState, type FormEvent } from "react";

export function ManualAnnotationDialog({
  open,
  onClose,
  onSave,
}: {
  open: boolean;
  onClose: () => void;
  onSave: (text: string) => void;
}) {
  const [text, setText] = useState("");
  if (!open) return null;
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!text.trim()) return;
    onSave(text.trim());
    setText("");
    onClose();
  };
  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={onClose}>
      <div
        className="dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="annotation-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <span className="eyebrow">RESEARCH ANNOTATION</span>
        <h2 id="annotation-title">Add a timeline note</h2>
        <p>
          This records an observation only. It does not represent completion of any patient-care
          action.
        </p>
        <form onSubmit={submit}>
          <label className="field">
            <span>Annotation</span>
            <textarea
              autoFocus
              required
              maxLength={240}
              value={text}
              onChange={(event) => setText(event.target.value)}
              placeholder="Observed change or contextual event"
            />
          </label>
          <div className="dialog-actions">
            <button className="button button--ghost" type="button" onClick={onClose}>
              Cancel
            </button>
            <button className="button button--primary" type="submit">
              Add annotation
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
