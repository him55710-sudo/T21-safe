"use client";

import { useEffect, useState } from "react";
import { BackendStatus } from "@/components/BackendStatus";
import { BaselineCalibrationPanel } from "@/components/BaselineCalibrationPanel";
import { BaselineDeltaTable } from "@/components/BaselineDeltaTable";
import { CaseSelector } from "@/components/CaseSelector";
import { DatasetAttribution } from "@/components/DatasetAttribution";
import { EventTimeline } from "@/components/EventTimeline";
import { EvidenceDrawer } from "@/components/EvidenceDrawer";
import { ExplanationList } from "@/components/ExplanationList";
import { ExportResearchSession } from "@/components/ExportResearchSession";
import { ManualAnnotationDialog } from "@/components/ManualAnnotationDialog";
import { ModelLimitationPanel } from "@/components/ModelLimitationPanel";
import { NumericVitalCard } from "@/components/NumericVitalCard";
import { PatientContextForm } from "@/components/PatientContextForm";
import { ReplayControls } from "@/components/ReplayControls";
import { ResearchDisclaimerBanner } from "@/components/ResearchDisclaimerBanner";
import { ResearchRiskGauge } from "@/components/ResearchRiskGauge";
import { RiskTrend } from "@/components/RiskTrend";
import { SignalQualityBadge } from "@/components/SignalQualityBadge";
import { WaveformPanel } from "@/components/WaveformPanel";
import { useMonitoringSession, type AppScreen } from "@/hooks/useMonitoringSession";

function formatElapsed(timestampMs: number) {
  const seconds = Math.floor(timestampMs / 1000);
  return `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
}

function ProductMark() {
  return (
    <div className="product-mark">
      <span className="product-symbol" aria-hidden="true">
        <i />
        <i />
        <i />
      </span>
      <div>
        <strong>T21 SAFE</strong>
        <span>PERIOPERATIVE RESEARCH SYSTEM</span>
      </div>
    </div>
  );
}

function ScreenHeader({
  screen,
  subjectId,
  source,
  mode,
  elapsed,
  connected,
  replayComplete,
  sessionReady,
  onNavigate,
  onExit,
}: {
  screen: AppScreen;
  subjectId: string;
  source: string;
  mode: string;
  elapsed: string;
  connected: boolean;
  replayComplete: boolean;
  sessionReady: boolean;
  onNavigate: (screen: AppScreen) => void;
  onExit: () => void;
}) {
  const sessionActive = !["start", "context"].includes(screen);
  return (
    <header className="app-header">
      <ProductMark />
      {sessionActive && sessionReady ? (
        <div className="session-strip">
          <div>
            <span>SUBJECT</span>
            <strong>{subjectId}</strong>
          </div>
          <div>
            <span>SOURCE</span>
            <strong>{source}</strong>
          </div>
          <div>
            <span>MODE</span>
            <strong>{mode.replaceAll("_", " ")}</strong>
          </div>
          <div>
            <span>ELAPSED</span>
            <strong className="mono">{elapsed}</strong>
          </div>
          <div className={`connection-state ${connected ? "is-connected" : "is-offline"}`}>
            <span className="status-dot" />
            <strong>
              {connected ? "DATA CONNECTED" : replayComplete ? "REPLAY COMPLETE" : "RECONNECTING"}
            </strong>
          </div>
        </div>
      ) : (
        <p className="tagline">
          Local-first perioperative physiological signal research
          <br />
          for physiologically vulnerable patients, starting with Down syndrome.
        </p>
      )}
      {sessionActive ? (
        <nav className="screen-nav" aria-label="Session views">
          <button
            type="button"
            className={screen === "live" ? "is-active" : ""}
            onClick={() => onNavigate("live")}
          >
            Monitor
          </button>
          <button
            type="button"
            className={screen === "explanation" ? "is-active" : ""}
            onClick={() => onNavigate("explanation")}
          >
            Explanation
          </button>
          <button
            type="button"
            className={screen === "review" ? "is-active" : ""}
            onClick={() => onNavigate("review")}
          >
            Case review
          </button>
          <button
            type="button"
            className={screen === "evidence" ? "is-active" : ""}
            onClick={() => onNavigate("evidence")}
          >
            Evidence
          </button>
          <button type="button" className="exit-button" onClick={onExit}>
            End replay
          </button>
        </nav>
      ) : sessionActive ? (
        <button type="button" className="button button--ghost" onClick={onExit}>
          End replay
        </button>
      ) : null}
    </header>
  );
}

function StartScreen({ session }: { session: ReturnType<typeof useMonitoringSession> }) {
  const [info, setInfo] = useState<"dataset" | "limitations" | null>(null);
  return (
    <main className="start-screen">
      <section className="hero-panel">
        <div className="hero-copy">
          <span className="eyebrow">SHADOW MODE · RESEARCH USE ONLY</span>
          <h1>
            See the signal.
            <br />
            <em>Understand the change.</em>
          </h1>
          <p>
            T21 Safe organizes waveform quality, patient-specific baseline change, and a
            deterministic research index into one inspectable perioperative timeline.
          </p>
          <div className="guardrail-row">
            <span>◇ No patient-care commands</span>
            <span>◇ No LLM risk generation</span>
            <span>◇ Index hidden when invalid</span>
          </div>
        </div>
        <div className="hero-visual" aria-hidden="true">
          <div className="visual-orbit">
            <span>RII</span>
            <strong>—</strong>
            <small>AWAITING BASELINE</small>
          </div>
          <svg viewBox="0 0 500 140">
            <polyline points="0,83 30,82 42,84 48,22 54,112 62,80 105,82 140,79 146,28 152,110 160,80 205,81 240,81 246,20 252,113 260,81 305,80 340,79 346,30 352,107 360,80 405,82 440,80 446,22 452,111 460,80 500,82" />
          </svg>
        </div>
      </section>
      <section className="start-workspace">
        <div className="start-main">
          <CaseSelector
            cases={session.cases}
            selectedId={session.selectedCaseId}
            onSelect={session.setSelectedCaseId}
          />
          <DatasetAttribution researchCase={session.selectedCase} />
        </div>
        <aside className="start-sidebar">
          <BackendStatus healthy={session.backendHealthy} demoMode={session.demoMode} />
          <div className="readiness-card">
            <span className="eyebrow">REPLAY READINESS</span>
            <ul>
              <li>
                <span>✓</span> Schema validation active
              </li>
              <li>
                <span>✓</span> Deterministic pipeline
              </li>
              <li>
                <span>✓</span> Audio alerts disabled
              </li>
              <li>
                <span>✓</span> Anonymous research ID
              </li>
            </ul>
          </div>
          <button
            className="button button--primary button--large"
            type="button"
            onClick={() => session.setScreen("context")}
          >
            Start replay <span>→</span>
          </button>
          <button
            className="button button--ghost"
            type="button"
            onClick={() => setInfo(info === "dataset" ? null : "dataset")}
          >
            Open dataset information
          </button>
          <button
            className="button button--ghost"
            type="button"
            onClick={() => setInfo(info === "limitations" ? null : "limitations")}
          >
            Review limitations
          </button>
        </aside>
      </section>
      {info ? (
        <section className="info-panel" aria-live="polite">
          <button
            className="icon-button"
            type="button"
            aria-label="Close information"
            onClick={() => setInfo(null)}
          >
            ×
          </button>
          {info === "dataset" ? (
            <>
              <span className="eyebrow">DATASET INFORMATION</span>
              <h2>{session.selectedCase.name}</h2>
              <p>{session.selectedCase.description}</p>
              <dl>
                <div>
                  <dt>Attribution</dt>
                  <dd>{session.selectedCase.attribution}</dd>
                </div>
                <div>
                  <dt>Terms</dt>
                  <dd>{session.selectedCase.license}</dd>
                </div>
                <div>
                  <dt>DS verification</dt>
                  <dd>Not verified as a Down syndrome case</dd>
                </div>
              </dl>
            </>
          ) : (
            <>
              <span className="eyebrow">CURRENT LIMITATIONS</span>
              <h2>Interpret as a research replay only</h2>
              <ul>
                <li>The index and thresholds have no patient-care indication.</li>
                <li>No DS-specific calibration or validation is present.</li>
                <li>Public data are not presented as DS patient data.</li>
                <li>Signal loss and low SQI suppress index display.</li>
              </ul>
            </>
          )}
        </section>
      ) : null}
    </main>
  );
}

function ContextScreen({ session }: { session: ReturnType<typeof useMonitoringSession> }) {
  return (
    <main className="content-screen content-screen--narrow">
      <div className="screen-intro">
        <button className="back-link" type="button" onClick={() => session.setScreen("start")}>
          ← Data source
        </button>
        <span className="step-label">STEP 2 OF 3</span>
        <h1>Confirm research subject context</h1>
        <p>Use structured record-derived context only. Unknown values must remain unknown.</p>
      </div>
      <DatasetAttribution researchCase={session.selectedCase} />
      <PatientContextForm
        initialValue={session.patientContext}
        onSubmit={(value) => void session.beginSession(value)}
      />
      {session.streamError ? (
        <div className="error-message" role="alert">
          {session.streamError}
        </div>
      ) : null}
    </main>
  );
}

function CalibrationScreen({ session }: { session: ReturnType<typeof useMonitoringSession> }) {
  return (
    <main className="content-screen calibration-screen">
      <div className="calibration-header">
        <span className="step-label">STEP 3 OF 3</span>
        <SignalQualityBadge value={session.frame.quality.overall ?? 0} />
      </div>
      <BaselineCalibrationPanel frame={session.frame} />
      <ModelLimitationPanel mode={session.mode} />
      <ReplayControls
        isPlaying={session.isPlaying}
        speed={session.replaySpeed}
        timestampMs={session.frame.timestamp_ms}
        onPlayChange={session.setIsPlaying}
        onSpeedChange={session.setReplaySpeed}
        onSeek={session.seek}
        interactive={session.demoMode}
        complete={session.replayComplete}
      />
    </main>
  );
}

function LiveScreen({ session }: { session: ReturnType<typeof useMonitoringSession> }) {
  const [annotationOpen, setAnnotationOpen] = useState(false);
  const [waveformsPaused, setWaveformsPaused] = useState(false);
  const [zoomed, setZoomed] = useState(false);
  const frame = session.frame;
  const quality = frame.quality.by_signal ?? {};
  const artifact = frame.quality.reasons.some((item) => item.toLowerCase().includes("artifact"));
  return (
    <main className="monitor-screen">
      <section className={`monitor-left ${zoomed ? "is-zoomed" : ""}`}>
        <div className="monitor-toolbar">
          <div>
            <span className="eyebrow">
              LIVE REPLAY ·{" "}
              {session.selectedCase.kind === "SYNTHETIC"
                ? "SYNTHETIC"
                : session.selectedCase.kind === "LOCAL_FIXTURE"
                  ? "LOCAL FIXTURE"
                  : "PUBLIC DATA"}
            </span>
            <strong>{session.selectedCase.name}</strong>
          </div>
          <div>
            <button
              className="tool-button"
              type="button"
              onClick={() => setWaveformsPaused((value) => !value)}
            >
              {waveformsPaused ? "▶ Resume waveforms" : "Ⅱ Pause waveforms"}
            </button>
            <button
              className="tool-button"
              type="button"
              onClick={() => setZoomed((value) => !value)}
            >
              {zoomed ? "− Standard view" : "+ Waveform zoom"}
            </button>
            <button className="tool-button" type="button" onClick={() => setAnnotationOpen(true)}>
              ＋ Annotation
            </button>
          </div>
        </div>
        <div className="vitals-row">
          <NumericVitalCard label="HR" value={frame.signals.ecg?.value} unit="bpm" tone="green" />
          <NumericVitalCard label="MAP" value={frame.signals.abp?.value} unit="mmHg" tone="amber" />
          <NumericVitalCard label="SpO₂" value={frame.signals.spo2?.value} unit="%" tone="blue" />
          <NumericVitalCard
            label="EtCO₂"
            value={frame.signals.etco2?.value}
            unit="mmHg"
            tone="violet"
          />
        </div>
        <div className="waveform-stack">
          <WaveformPanel
            label="ECG"
            signal={frame.signals.ecg!}
            quality={quality.ECG ?? 0}
            paused={waveformsPaused}
            zoomed={zoomed}
            artifact={artifact}
          />
          <WaveformPanel
            label="PPG"
            signal={frame.signals.ppg!}
            quality={quality.PPG ?? 0}
            paused={waveformsPaused}
            zoomed={zoomed}
          />
          <WaveformPanel
            label="ABP"
            signal={frame.signals.abp!}
            quality={quality.ABP ?? 0}
            paused={waveformsPaused}
            zoomed={zoomed}
          />
        </div>
      </section>
      <aside className="monitor-right">
        <ResearchRiskGauge risk={frame.risk} qualityUsable={frame.quality.usable} />
        <RiskTrend history={session.history} />
        <div className="baseline-comparison">
          <span className="eyebrow">BASELINE COMPARISON</span>
          <div>
            <span>HR</span>
            <strong>
              {Number(frame.features.hr ?? 0) - Number(frame.baseline.values?.hr ?? 0)} bpm
            </strong>
          </div>
          <div>
            <span>MAP</span>
            <strong>
              {Number(frame.features.map ?? 0) - Number(frame.baseline.values?.map ?? 0)} mmHg
            </strong>
          </div>
          <div>
            <span>PPG amplitude</span>
            <strong>
              {frame.features.ppg_amplitude === null
                ? "Missing"
                : `${(Number(frame.features.ppg_amplitude) - Number(frame.baseline.values?.ppg_amplitude ?? 0)).toFixed(2)} a.u.`}
            </strong>
          </div>
        </div>
        <div className="quality-summary">
          <span className="eyebrow">SIGNAL QUALITY</span>
          <SignalQualityBadge value={frame.quality.overall ?? 0} />
          <p>
            {frame.quality.reasons.join(" · ") ||
              "All required inputs meet the current research quality gate."}
          </p>
        </div>
        <ExplanationList reasons={frame.risk.reasons} />
        <ModelLimitationPanel mode={session.mode} />
        <button
          className="button button--primary"
          type="button"
          onClick={() => session.setScreen("explanation")}
        >
          Open structured explanation →
        </button>
      </aside>
      <section className="monitor-footer">
        <EventTimeline frame={frame} annotations={session.annotations} compact />
        <ReplayControls
          isPlaying={session.isPlaying}
          speed={session.replaySpeed}
          timestampMs={frame.timestamp_ms}
          onPlayChange={session.setIsPlaying}
          onSpeedChange={session.setReplaySpeed}
          onSeek={session.seek}
          interactive={session.demoMode}
          complete={session.replayComplete}
        />
      </section>
      <ManualAnnotationDialog
        open={annotationOpen}
        onClose={() => setAnnotationOpen(false)}
        onSave={session.addAnnotation}
      />
    </main>
  );
}

function ExplanationScreen({ session }: { session: ReturnType<typeof useMonitoringSession> }) {
  return (
    <main className="content-screen explanation-screen">
      <div className="screen-intro screen-intro--row">
        <div>
          <span className="eyebrow">STRUCTURED EXPLANATION</span>
          <h1>What changed the research index?</h1>
          <p>
            This view describes feature movement. It does not determine why a patient is at risk or
            prescribe a response.
          </p>
        </div>
        <div className="current-index">
          <span>CURRENT INDEX</span>
          <strong>{session.frame.risk.valid ? session.frame.risk.score : "INVALID"}</strong>
          <em>{session.frame.risk.level}</em>
        </div>
      </div>
      <div className="explanation-summary">
        <ExplanationList reasons={session.frame.risk.reasons} />
        <ModelLimitationPanel mode={session.mode} />
      </div>
      <BaselineDeltaTable frame={session.frame} />
    </main>
  );
}

function CaseReviewScreen({ session }: { session: ReturnType<typeof useMonitoringSession> }) {
  const scores = session.history.filter((item) => item.risk.score !== null).slice(-80);
  const points = scores
    .map(
      (item, index) =>
        `${(index / Math.max(1, scores.length - 1)) * 100},${48 - (item.risk.score ?? 0) * 0.42}`,
    )
    .join(" ");
  const recentFrames = session.history.slice(-80);
  const vitalPoints = recentFrames
    .map(
      (item, index) =>
        `${(index / Math.max(1, recentFrames.length - 1)) * 100},${50 - Number(item.features.map ?? 0) * 0.42}`,
    )
    .join(" ");
  const qualityPoints = recentFrames
    .map(
      (item, index) =>
        `${(index / Math.max(1, recentFrames.length - 1)) * 100},${50 - Number(item.quality.overall ?? 0) * 45}`,
    )
    .join(" ");
  return (
    <main className="content-screen review-screen">
      <div className="screen-intro screen-intro--row">
        <div>
          <span className="eyebrow">RESEARCH SESSION SUMMARY</span>
          <h1>Case review</h1>
          <p>
            Retrospective research replay with synchronized index, vitals, quality, and annotations.
          </p>
        </div>
        <ExportResearchSession payload={session.exportPayload} />
      </div>
      <section className="review-overview">
        <div className="review-stat">
          <span>Duration</span>
          <strong>{formatElapsed(session.frame.timestamp_ms)}</strong>
          <small>replay elapsed</small>
        </div>
        <div className="review-stat">
          <span>Current level</span>
          <strong>{session.frame.risk.level}</strong>
          <small>
            {session.frame.risk.valid ? `${session.frame.risk.score} / 100` : "index hidden"}
          </small>
        </div>
        <div className="review-stat">
          <span>Signal quality</span>
          <strong>{Math.round((session.frame.quality.overall ?? 0) * 100)}%</strong>
          <small>{session.frame.quality.usable ? "usable" : "not usable"}</small>
        </div>
        <div className="review-stat">
          <span>Annotations</span>
          <strong>{session.annotations.length}</strong>
          <small>research notes</small>
        </div>
      </section>
      <section className="review-trends">
        <article className="review-chart">
          <div>
            <span className="eyebrow">INDEX TREND</span>
            <strong>Research Instability Index</strong>
          </div>
          <svg
            viewBox="0 0 100 52"
            preserveAspectRatio="none"
            role="img"
            aria-label="Full research index trend"
          >
            <line x1="0" x2="100" y1="20.7" y2="20.7" />
            <line x1="0" x2="100" y1="32" y2="32" />
            <polyline points={points || "0,42 100,42"} />
          </svg>
          <div className="chart-labels">
            <span>0</span>
            <span>WATCH</span>
            <span>ELEVATED</span>
            <span>100</span>
          </div>
        </article>
        <article className="review-chart">
          <div>
            <span className="eyebrow">VITALS TREND</span>
            <strong>MAP · mmHg</strong>
          </div>
          <svg
            viewBox="0 0 100 52"
            preserveAspectRatio="none"
            role="img"
            aria-label="Mean arterial pressure trend"
          >
            <polyline points={vitalPoints || "0,20 100,20"} />
          </svg>
          <div className="chart-labels">
            <span>Earlier</span>
            <span>Patient-specific trend</span>
            <span>Current</span>
          </div>
        </article>
        <article className="review-chart">
          <div>
            <span className="eyebrow">SIGNAL QUALITY TREND</span>
            <strong>Composite SQI · %</strong>
          </div>
          <svg
            viewBox="0 0 100 52"
            preserveAspectRatio="none"
            role="img"
            aria-label="Signal quality trend"
          >
            <polyline points={qualityPoints || "0,8 100,8"} />
          </svg>
          <div className="chart-labels">
            <span>Earlier</span>
            <span>Usability context</span>
            <span>Current</span>
          </div>
        </article>
      </section>
      <EventTimeline frame={session.frame} annotations={session.annotations} />
      <section className="review-note">
        <strong>Research summary — not a patient-care report</strong>
        <p>
          Exports are anonymized replay artifacts and contain no name, medical-record number,
          contact information, or treatment advice.
        </p>
      </section>
    </main>
  );
}

function EvidenceScreen({ session }: { session: ReturnType<typeof useMonitoringSession> }) {
  return (
    <main className="content-screen evidence-screen">
      <div className="screen-intro">
        <span className="eyebrow">MODEL & DATA TRANSPARENCY</span>
        <h1>Evidence and data</h1>
        <p>
          Inspect the versioned evidence record and population limitations before interpreting
          research output.
        </p>
      </div>
      <EvidenceDrawer evidence={session.evidence} embedded />
      <ModelLimitationPanel mode={session.mode} />
    </main>
  );
}

export function T21SafeApp() {
  const session = useMonitoringSession();
  const activeScreen =
    session.screen === "calibration" && session.frame.baseline.calibrated ? "live" : session.screen;

  useEffect(() => {
    window.scrollTo({ top: 0, left: 0 });
  }, [activeScreen]);

  return (
    <div className="app-shell">
      <ResearchDisclaimerBanner />
      <ScreenHeader
        screen={activeScreen}
        subjectId={session.patientContext.studySubjectId}
        source={session.selectedCase.name}
        mode={session.mode}
        elapsed={formatElapsed(session.frame.timestamp_ms)}
        connected={session.connected}
        replayComplete={session.replayComplete}
        sessionReady={session.frame.baseline.calibrated}
        onNavigate={session.setScreen}
        onExit={session.reset}
      />
      {activeScreen === "start" ? <StartScreen session={session} /> : null}
      {activeScreen === "context" ? <ContextScreen session={session} /> : null}
      {activeScreen === "calibration" ? <CalibrationScreen session={session} /> : null}
      {activeScreen === "live" ? <LiveScreen session={session} /> : null}
      {activeScreen === "explanation" ? <ExplanationScreen session={session} /> : null}
      {activeScreen === "review" ? <CaseReviewScreen session={session} /> : null}
      {activeScreen === "evidence" ? <EvidenceScreen session={session} /> : null}
    </div>
  );
}
