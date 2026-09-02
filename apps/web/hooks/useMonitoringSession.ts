"use client";

import { useQuery } from "@tanstack/react-query";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  getBackendHealth,
  getCases,
  getEvidence,
  openValidatedEventStream,
  startReplay as startApiReplay,
} from "@/lib/api";
import { DEFAULT_PATIENT_CONTEXT, type PatientContext, type StreamFrame } from "@/lib/contracts";
import {
  createMockFrame,
  isScenarioId,
  MOCK_CASES,
  MOCK_EVIDENCE,
  type ScenarioId,
} from "@/lib/mock-stream";

export type AppScreen =
  | "start"
  | "context"
  | "calibration"
  | "live"
  | "explanation"
  | "review"
  | "evidence";

export interface ResearchAnnotation {
  id: string;
  timestampMs: number;
  text: string;
}

const demoMode = process.env.NEXT_PUBLIC_DEMO_MODE !== "false";
const configuredDefault = process.env.NEXT_PUBLIC_DEFAULT_CASE ?? "progressive_instability";
const defaultCase: ScenarioId = isScenarioId(configuredDefault)
  ? configuredDefault
  : "progressive_instability";

export function useMonitoringSession() {
  const [screen, setScreen] = useState<AppScreen>("start");
  const [selectedCaseId, setSelectedCaseId] = useState<string>(defaultCase);
  const [patientContext, setPatientContext] = useState(DEFAULT_PATIENT_CONTEXT);
  const [mode, setMode] = useState<StreamFrame["mode"]>("GENERIC_VALIDATION_MODE");
  const [frame, setFrame] = useState(() => createMockFrame(defaultCase, 0));
  const frameRef = useRef(frame);
  const [history, setHistory] = useState<StreamFrame[]>([]);
  const [annotations, setAnnotations] = useState<ResearchAnnotation[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [replaySpeed, setReplaySpeed] = useState(40);
  const [connected, setConnected] = useState(demoMode);
  const [replayComplete, setReplayComplete] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);
  const streamCleanup = useRef<(() => void) | null>(null);

  const healthQuery = useQuery({
    queryKey: ["backend-health"],
    queryFn: getBackendHealth,
    enabled: !demoMode,
    refetchInterval: 15_000,
  });
  const casesQuery = useQuery({
    queryKey: ["cases"],
    queryFn: getCases,
    enabled: !demoMode,
  });
  const evidenceQuery = useQuery({
    queryKey: ["evidence"],
    queryFn: getEvidence,
    enabled: !demoMode,
  });

  const cases = casesQuery.data ?? MOCK_CASES;
  const evidence = evidenceQuery.data ?? MOCK_EVIDENCE;
  const effectiveSelectedCaseId = cases.some((item) => item.id === selectedCaseId)
    ? selectedCaseId
    : (cases[0]?.id ?? selectedCaseId);
  const selectedCase = cases.find((item) => item.id === effectiveSelectedCaseId) ?? MOCK_CASES[0]!;

  const acceptFrame = useCallback((nextFrame: StreamFrame) => {
    frameRef.current = nextFrame;
    setFrame(nextFrame);
    setHistory((current) => [...current.slice(-239), nextFrame]);
    if (nextFrame.baseline.calibrated) {
      setScreen((current) => (current === "calibration" ? "live" : current));
    }
  }, []);

  useEffect(() => {
    if (!demoMode || !isPlaying || (screen !== "calibration" && screen !== "live")) return;
    const timer = window.setInterval(() => {
      const scenario = isScenarioId(selectedCaseId) ? selectedCaseId : "progressive_instability";
      const next = createMockFrame(
        scenario,
        frameRef.current.timestamp_ms + 500 * replaySpeed,
        mode,
      );
      frameRef.current = next;
      setFrame(next);
      setHistory((items) => [...items.slice(-239), next]);
      if (next.baseline.calibrated) {
        setScreen((currentScreen) => (currentScreen === "calibration" ? "live" : currentScreen));
      }
    }, 500);
    return () => window.clearInterval(timer);
  }, [isPlaying, mode, replaySpeed, screen, selectedCaseId]);

  useEffect(() => () => streamCleanup.current?.(), []);

  const beginSession = useCallback(
    async (context: PatientContext) => {
      setPatientContext(context);
      const nextMode =
        context.dsStatus === "confirmed by clinical record"
          ? "DS_HYPOTHESIS_MODE"
          : "GENERIC_VALIDATION_MODE";
      setMode(nextMode);
      setHistory([]);
      setAnnotations([]);
      setStreamError(null);
      setReplayComplete(false);
      setScreen("calibration");
      setIsPlaying(true);

      if (demoMode) {
        const scenario = isScenarioId(selectedCaseId) ? selectedCaseId : "progressive_instability";
        const initialFrame = createMockFrame(scenario, 0, nextMode);
        frameRef.current = initialFrame;
        setFrame(initialFrame);
        setConnected(true);
        return;
      }

      try {
        const sessionId = await startApiReplay(effectiveSelectedCaseId, nextMode, replaySpeed);
        streamCleanup.current?.();
        streamCleanup.current = openValidatedEventStream(
          sessionId,
          acceptFrame,
          setConnected,
          () => {
            setIsPlaying(false);
            setReplayComplete(true);
          },
        );
      } catch (error) {
        setConnected(false);
        setIsPlaying(false);
        setStreamError(error instanceof Error ? error.message : "Unable to start replay.");
      }
    },
    [acceptFrame, effectiveSelectedCaseId, replaySpeed, selectedCaseId],
  );

  const seek = useCallback(
    (timestampMs: number) => {
      if (!demoMode) return;
      const scenario = isScenarioId(selectedCaseId) ? selectedCaseId : "progressive_instability";
      const next = createMockFrame(scenario, Math.max(0, timestampMs), mode);
      frameRef.current = next;
      setFrame(next);
      setHistory((items) => [...items, next]);
    },
    [mode, selectedCaseId],
  );

  const addAnnotation = useCallback(
    (text: string) => {
      setAnnotations((current) => [
        ...current,
        { id: `annotation-${current.length + 1}`, timestampMs: frame.timestamp_ms, text },
      ]);
    },
    [frame.timestamp_ms],
  );

  const reset = useCallback(() => {
    streamCleanup.current?.();
    streamCleanup.current = null;
    setScreen("start");
    setIsPlaying(false);
    setReplayComplete(false);
    setHistory([]);
    setAnnotations([]);
    const scenario = isScenarioId(selectedCaseId) ? selectedCaseId : "progressive_instability";
    const initialFrame = createMockFrame(scenario, 0);
    frameRef.current = initialFrame;
    setFrame(initialFrame);
  }, [selectedCaseId]);

  const exportPayload = useMemo(
    () => ({
      export_type: "research_session_summary",
      generated_at: new Date().toISOString(),
      source: selectedCase,
      mode,
      patient_context: patientContext,
      latest_frame: frame,
      annotations,
      frame_count: history.length,
    }),
    [annotations, frame, history.length, mode, patientContext, selectedCase],
  );

  return {
    annotations,
    addAnnotation,
    backendHealthy: healthQuery.data === true,
    beginSession,
    cases,
    connected,
    demoMode,
    evidence,
    exportPayload,
    frame,
    history,
    isPlaying,
    mode,
    patientContext,
    replaySpeed,
    replayComplete,
    reset,
    screen,
    seek,
    selectedCase,
    selectedCaseId: effectiveSelectedCaseId,
    setIsPlaying,
    setPatientContext,
    setReplaySpeed,
    setScreen,
    setSelectedCaseId,
    streamError,
  };
}
