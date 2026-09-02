import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { Providers } from "@/app/providers";
import { CaseSelector } from "@/components/CaseSelector";
import { EventTimeline } from "@/components/EventTimeline";
import { ExportResearchSession } from "@/components/ExportResearchSession";
import { T21SafeApp } from "@/components/T21SafeApp";
import { getBackendHealth, openValidatedEventStream, startReplay } from "@/lib/api";
import { streamFrameSchema } from "@/lib/contracts";
import { createMockFrame, MOCK_CASES } from "@/lib/mock-stream";

describe("monitoring integration", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("plays a local mock stream through baseline to WATCH and ELEVATED", async () => {
    vi.useFakeTimers();
    render(
      <Providers>
        <T21SafeApp />
      </Providers>,
    );
    fireEvent.click(screen.getByRole("button", { name: /Start replay/ }));
    fireEvent.click(screen.getByRole("button", { name: /Begin 180-second baseline calibration/ }));
    expect(screen.getByText("Establishing a stable reference")).toBeInTheDocument();
    await act(async () => vi.advanceTimersByTime(4_500));
    expect(screen.getByText(/LIVE REPLAY/)).toBeInTheDocument();
    await act(async () => vi.advanceTimersByTime(4_000));
    expect(screen.getAllByText("ELEVATED").length).toBeGreaterThan(0);
  });

  it("checks backend health", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true }));
    await expect(getBackendHealth()).resolves.toBe(true);
  });

  it("selects a case", () => {
    const onSelect = vi.fn();
    render(<CaseSelector cases={MOCK_CASES} selectedId="stable_case" onSelect={onSelect} />);
    fireEvent.click(screen.getByRole("radio", { name: /ECG motion artifact/ }));
    expect(onSelect).toHaveBeenCalledWith("artifact_case");
  });

  it("starts an API replay with the exact endpoint", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({ session_id: "session-123" }) });
    vi.stubGlobal("fetch", fetchMock);
    await expect(startReplay("stable_case", { studySubjectId: "R-1" } as never)).resolves.toBe(
      "session-123",
    );
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/v1/replays"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("reconnects after an SSE interruption", () => {
    vi.useFakeTimers();
    const instances: MockEventSource[] = [];
    class MockEventSource {
      onopen: (() => void) | null = null;
      onmessage: ((event: MessageEvent) => void) | null = null;
      onerror: (() => void) | null = null;
      close = vi.fn();
      constructor(public url: string) {
        instances.push(this);
      }
    }
    vi.stubGlobal("EventSource", MockEventSource);
    const connection = vi.fn();
    const close = openValidatedEventStream("session-1", vi.fn(), connection);
    expect(instances).toHaveLength(1);
    instances[0]!.onerror?.();
    vi.advanceTimersByTime(1_000);
    expect(instances).toHaveLength(2);
    close();
  });

  it("updates the event timeline", () => {
    const { rerender } = render(
      <EventTimeline
        frame={createMockFrame("progressive_instability", 190_000)}
        annotations={[]}
      />,
    );
    expect(screen.queryByLabelText(/Sustained trend candidate/)).not.toBeInTheDocument();
    rerender(
      <EventTimeline
        frame={createMockFrame("progressive_instability", 300_000)}
        annotations={[]}
      />,
    );
    expect(screen.getByLabelText(/Sustained trend candidate/)).toBeInTheDocument();
  });

  it("exports an anonymized research session", () => {
    const createObjectURL = vi.fn(() => "blob:test");
    const revokeObjectURL = vi.fn();
    vi.stubGlobal("URL", { createObjectURL, revokeObjectURL });
    const click = vi
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => undefined);
    render(
      <ExportResearchSession payload={{ latest_frame: createMockFrame("stable_case", 200_000) }} />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Export anonymized JSON" }));
    expect(createObjectURL).toHaveBeenCalledOnce();
    expect(click).toHaveBeenCalledOnce();
  });

  it("validates every local scenario frame against the SSE schema", () => {
    for (const researchCase of MOCK_CASES.filter((item) => item.kind !== "VITALDB_PUBLIC")) {
      expect(
        streamFrameSchema.safeParse(createMockFrame(researchCase.id as never, 260_000)).success,
      ).toBe(true);
    }
  });
});
