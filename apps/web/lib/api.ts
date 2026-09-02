import {
  caseSchema,
  evidenceSchema,
  streamFrameSchema,
  type Evidence,
  type PatientContext,
  type ResearchCase,
  type StreamFrame,
} from "@/lib/contracts";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function fetchJson<T>(
  path: string,
  schema: { parse: (value: unknown) => T },
  init?: RequestInit,
) {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return schema.parse(await response.json());
}

export async function getBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(2_500) });
    return response.ok;
  } catch {
    return false;
  }
}

export function getCases(): Promise<ResearchCase[]> {
  return fetchJson("/v1/cases", caseSchema.array());
}

export function getEvidence(): Promise<Evidence> {
  return fetchJson("/v1/evidence", evidenceSchema);
}

export async function startReplay(caseId: string, context: PatientContext): Promise<string> {
  const response = await fetch(`${API_URL}/v1/replays`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ case_id: caseId, patient_context: context }),
  });
  if (!response.ok) throw new Error(`Replay start failed: ${response.status}`);
  const body = (await response.json()) as { session_id?: unknown };
  if (typeof body.session_id !== "string") throw new Error("Replay response has no session_id");
  return body.session_id;
}

export function analyzeWindow(frame: StreamFrame): Promise<StreamFrame> {
  return fetchJson("/v1/analyze-window", streamFrameSchema, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(frame),
  });
}

export function openValidatedEventStream(
  sessionId: string,
  onFrame: (frame: StreamFrame) => void,
  onConnection: (connected: boolean) => void,
) {
  let source: EventSource | null = null;
  let closed = false;
  let retryTimer: ReturnType<typeof setTimeout> | undefined;
  let retryCount = 0;

  const connect = () => {
    if (closed) return;
    source = new EventSource(`${API_URL}/v1/stream/${encodeURIComponent(sessionId)}`);
    source.onopen = () => {
      retryCount = 0;
      onConnection(true);
    };
    source.onmessage = (event) => {
      try {
        const result = streamFrameSchema.safeParse(JSON.parse(event.data) as unknown);
        if (result.success) onFrame(result.data);
      } catch {
        // Ignore malformed SSE messages. A partial frame is never rendered.
      }
    };
    source.onerror = () => {
      onConnection(false);
      source?.close();
      if (!closed) {
        retryCount += 1;
        retryTimer = setTimeout(connect, Math.min(5_000, 500 * 2 ** retryCount));
      }
    };
  };

  connect();
  return () => {
    closed = true;
    if (retryTimer) clearTimeout(retryTimer);
    source?.close();
  };
}
