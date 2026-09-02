# UX architecture

## Information model

The interface keeps four kinds of information distinct:

| Layer                   | Question                           | Examples                                                    |
| ----------------------- | ---------------------------------- | ----------------------------------------------------------- |
| Source validity         | Can this replay be interpreted?    | connection, attribution, license, public/synthetic label    |
| Signal validity         | Can features be calculated?        | availability, SQI, artifact, missing signal                 |
| Patient reference       | What is the individual comparison? | 180-second baseline, stability, confidence, deltas          |
| Research interpretation | What changed the index?            | score, level, trend, reasons, grouped features, limitations |

The score never substitutes for the first three layers.

## Navigation

The start → context → calibration sequence is linear because later steps are unsafe without prior data. After calibration, Monitor, Explanation, Case review, and Evidence are peer views in a persistent session header. Ending replay returns to the source screen and clears in-memory session history.

## Monitor layout

At 1920×1080, the live workspace uses roughly 63% width for waveforms/vitals and 37% for research interpretation. The bottom band is a shared event/replay timeline. This preserves waveform legibility while giving invalid-state explanations enough room to replace the score.

Waveforms are Canvas-based. Each panel has a stable label rail, sample rate, independent SQI, missing-state pattern, pause overlay, and artifact marker. Numeric cards retain units and signal color, but label and position remain the primary identifiers.

## State precedence

```text
connection status (independent)
  → baseline complete?
    no: BASELINE, score hidden
    yes → quality usable?
      no: INVALID, score hidden, reasons shown
      yes → backend risk valid and numeric?
        no: INVALID, score hidden
        yes: STABLE / WATCH / ELEVATED / HIGH with trend and reasons
```

## Data flow

```text
local deterministic generator OR FastAPI SSE
  → Zod stream-frame validation
  → session state + bounded history
  → Canvas signals / quality / baseline / risk / timeline
  → local anonymized export
```

The browser does not calculate a production risk result. Fixture calculations exist only for deterministic UI behavior and are visibly synthetic.

## Reconnect

API mode creates a replay, opens `/v1/stream/{session_id}`, and validates each message. A stream error closes the source, displays `RECONNECTING`, and retries with exponential backoff capped at five seconds. Invalid messages are ignored rather than partially rendered.
