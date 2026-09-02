"use client";

import { useState, type FormEvent } from "react";
import { type PatientContext } from "@/lib/contracts";

const triState = ["yes", "no", "unknown"] as const;

function SelectField({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: readonly string[];
  onChange: (value: string) => void;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

export function PatientContextForm({
  initialValue,
  onSubmit,
}: {
  initialValue: PatientContext;
  onSubmit: (value: PatientContext) => void;
}) {
  const [value, setValue] = useState(initialValue);
  const update = <K extends keyof PatientContext>(key: K, next: PatientContext[K]) =>
    setValue((current) => ({ ...current, [key]: next }));

  const submit = (event: FormEvent) => {
    event.preventDefault();
    onSubmit(value);
  };

  return (
    <form className="context-form" onSubmit={submit}>
      <div className="form-grid">
        <label className="field">
          <span>Study subject ID</span>
          <input
            required
            value={value.studySubjectId}
            onChange={(event) => update("studySubjectId", event.target.value)}
          />
        </label>
        <SelectField
          label="Age group"
          value={value.ageGroup}
          options={[
            "Pediatric (2–11 years)",
            "Adolescent (12–17 years)",
            "Adult (18–64 years)",
            "Older adult (65+ years)",
          ]}
          onChange={(next) => update("ageGroup", next)}
        />
        <SelectField
          label="Weight range"
          value={value.weightRange}
          options={["20–39 kg", "40–59 kg", "60–79 kg", "80–99 kg", "100+ kg", "unknown"]}
          onChange={(next) => update("weightRange", next)}
        />
        <SelectField
          label="DS diagnosis status"
          value={value.dsStatus}
          options={["confirmed by clinical record", "not confirmed", "unknown"]}
          onChange={(next) => update("dsStatus", next as PatientContext["dsStatus"])}
        />
        <SelectField
          label="Congenital heart disease"
          value={value.congenitalHeartDisease}
          options={triState}
          onChange={(next) =>
            update("congenitalHeartDisease", next as PatientContext["congenitalHeartDisease"])
          }
        />
        <SelectField
          label="Obstructive sleep apnea"
          value={value.obstructiveSleepApnea}
          options={triState}
          onChange={(next) =>
            update("obstructiveSleepApnea", next as PatientContext["obstructiveSleepApnea"])
          }
        />
        <SelectField
          label="Previous anesthesia complication"
          value={value.previousAnesthesiaComplication}
          options={triState}
          onChange={(next) =>
            update(
              "previousAnesthesiaComplication",
              next as PatientContext["previousAnesthesiaComplication"],
            )
          }
        />
        <SelectField
          label="Anesthesia type"
          value={value.anesthesiaType}
          options={[
            "General anesthesia — metadata only",
            "Sedation — metadata only",
            "Regional anesthesia — metadata only",
            "unknown",
          ]}
          onChange={(next) => update("anesthesiaType", next)}
        />
      </div>
      <fieldset className="signal-checklist">
        <legend>Available signals</legend>
        {["ECG", "PPG", "ABP", "SpO₂", "EtCO₂", "Respiratory signal"].map((signal) => (
          <label key={signal}>
            <input
              type="checkbox"
              checked={value.availableSignals.includes(signal)}
              onChange={(event) =>
                update(
                  "availableSignals",
                  event.target.checked
                    ? [...value.availableSignals, signal]
                    : value.availableSignals.filter((item) => item !== signal),
                )
              }
            />
            {signal}
          </label>
        ))}
      </fieldset>
      <div className="safety-callout">
        <strong>Entered context is authoritative.</strong>
        <span>
          Missing values remain unknown. Waveforms are not used to infer Down syndrome or structural
          heart disease.
        </span>
      </div>
      <button className="button button--primary" type="submit">
        Begin 180-second baseline calibration
      </button>
    </form>
  );
}
