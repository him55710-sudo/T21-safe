# Data flow

## Sources and boundaries

| Source | Default availability | Flow | Permitted use |
|---|---|---|---|
| Deterministic synthetic scenarios | Yes | Generator → memory → pipeline → SSE → browser | Unit/integration testing and UI demonstration |
| Bundled local fixture | Yes | Repository CSV → memory → pipeline → SSE → browser | Software plumbing only; not clinical evidence |
| VitalDB public API | No; requires `OFFLINE_MODE=false` | Public HTTPS GET → memory → pipeline | Generic perioperative adapter/signal research only |
| PhysioNet/WFDB records | No; requires online mode and optional dependency | Public or approved local record → memory → pipeline | Dataset-specific technical validation only |
| Hospital data | Not implemented | Future hospital adapter inside approved LAN | Only after IRB/DUA, de-identification, and data-governance approval |

The API never receives the dashboard's detailed study-subject context. The browser sends only a case identifier, replay mode, speed, and baseline duration. API analysis-window bodies are ephemeral and are not persisted. Browser exports are initiated locally and must use pseudonymous study IDs.

## Runtime flow

1. An adapter returns aligned timestamps, available signals, source metadata, and raw provenance.
2. The ring buffer sorts timestamps, retains the newest duplicate, counts reversals, measures gaps, and bounds memory.
3. ECG/PPG are filtered for feature calculation. Signal-quality metrics operate on raw windows so filtering cannot hide motion or clipping.
4. The gate evaluates per-signal SQI, missingness, source dropout, packet latency, synchronization, valid beats, and pressure availability.
5. A stable 180-second baseline is calculated. If calibration fails, risk output is withheld.
6. Features and the deterministic index are calculated locally. Invalid input yields `INVALID` and no score.
7. FastAPI validates every frame and emits SSE `signal` events followed by an explicit `end` event.
8. The dashboard validates and normalizes the API frame before rendering it. Malformed frames are ignored.

## Persistence and egress

- API replay sessions exist only in process memory and are deleted after consumption, cancellation, or TTL expiry.
- The ring buffer is cleared in a `finally` block.
- No raw waveform, PHI, or feature data are sent to cloud services by repository code.
- `OFFLINE_MODE=true` prevents network-backed adapters from being listed or loaded.
- Source downloads performed by research tools must target a directory outside the Git checkout and produce a manifest/checksum.
