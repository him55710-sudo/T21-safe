import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BaselineCalibrationPanel } from "@/components/BaselineCalibrationPanel";
import { DatasetAttribution } from "@/components/DatasetAttribution";
import { EvidenceDrawer } from "@/components/EvidenceDrawer";
import { ModelLimitationPanel } from "@/components/ModelLimitationPanel";
import { ResearchRiskGauge } from "@/components/ResearchRiskGauge";
import { SignalQualityBadge } from "@/components/SignalQualityBadge";
import { WaveformPanel } from "@/components/WaveformPanel";
import { createMockFrame, MOCK_CASES, MOCK_EVIDENCE } from "@/lib/mock-stream";

describe("safety-critical component states", () => {
  it("keeps primary monitor color pairs above WCAG AA contrast", () => {
    const luminance = (hex: string) => {
      const channels = [1, 3, 5].map(
        (index) => Number.parseInt(hex.slice(index, index + 2), 16) / 255,
      );
      const [red = 0, green = 0, blue = 0] = channels.map((channel) =>
        channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4,
      );
      return 0.2126 * red + 0.7152 * green + 0.0722 * blue;
    };
    const contrast = (foreground: string, background: string) => {
      const values = [luminance(foreground), luminance(background)];
      return (Math.max(...values) + 0.05) / (Math.min(...values) + 0.05);
    };
    const pairs = [
      ["#edf6f6", "#071018"],
      ["#8ca5b3", "#071018"],
      ["#43e5b0", "#071018"],
      ["#ffbb55", "#071018"],
      ["#ff6f70", "#071018"],
      ["#ffe4ab", "#261f12"],
      ["#041813", "#43e5b0"],
    ];
    for (const [foreground, background] of pairs) {
      expect(contrast(foreground!, background!)).toBeGreaterThanOrEqual(4.5);
    }
  });

  it("shows a valid risk score with level and confidence", () => {
    const frame = createMockFrame("progressive_instability", 360_000);
    render(<ResearchRiskGauge risk={frame.risk} qualityUsable />);
    expect(screen.getByText(frame.risk.score!)).toBeInTheDocument();
    expect(screen.getByText("ELEVATED")).toBeInTheDocument();
    expect(screen.getByText("88%")).toBeInTheDocument();
  });

  it("hides the score when risk is invalid", () => {
    const frame = createMockFrame("artifact_case", 260_000);
    render(<ResearchRiskGauge risk={frame.risk} qualityUsable={false} />);
    expect(screen.getByText("INDEX HIDDEN")).toBeInTheDocument();
    expect(screen.getByText("INVALID")).toBeInTheDocument();
  });

  it("reports baseline progress and never offers a bypass", () => {
    render(<BaselineCalibrationPanel frame={createMockFrame("stable_case", 90_000)} />);
    expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "50");
    expect(screen.getByText("90")).toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("marks low SQI with icon, text, and percentage", () => {
    render(<SignalQualityBadge value={0.18} />);
    expect(screen.getByLabelText(/INSUFFICIENT, 18 percent/)).toBeInTheDocument();
    expect(screen.getByText("×")).toBeInTheDocument();
  });

  it("renders an explicit missing-signal state", () => {
    const frame = createMockFrame("missing_signal_case", 220_000);
    render(<WaveformPanel label="PPG" signal={frame.signals.ppg!} quality={0} paused={false} />);
    expect(screen.getByText("NO SIGNAL")).toBeInTheDocument();
    expect(screen.getByText("PPG is unavailable")).toBeInTheDocument();
  });

  it("shows the DS hypothesis limitation", () => {
    render(<ModelLimitationPanel mode="DS_HYPOTHESIS_MODE" />);
    expect(screen.getByTestId("ds-disclaimer")).toHaveTextContent(
      "No DS-specific calibration has been completed",
    );
  });

  it("does not present a public case as verified DS data", () => {
    const publicCase = MOCK_CASES.find((item) => item.kind === "VITALDB_PUBLIC")!;
    render(<DatasetAttribution researchCase={publicCase} />);
    expect(screen.getByTestId("public-case-disclaimer")).toHaveTextContent(
      "not a verified Down syndrome case",
    );
  });

  it("shows model evidence and known limitations", () => {
    render(<EvidenceDrawer evidence={MOCK_EVIDENCE} embedded />);
    expect(screen.getByText(MOCK_EVIDENCE.evidence_id)).toBeInTheDocument();
    expect(screen.getByText("Known limitations")).toBeInTheDocument();
    expect(screen.getByText(MOCK_EVIDENCE.model_version)).toBeInTheDocument();
  });

  it("does not render patient-care recommendations", () => {
    const { container } = render(<ModelLimitationPanel mode="GENERIC_VALIDATION_MODE" />);
    const text = container.textContent?.toLowerCase() ?? "";
    expect(text).not.toMatch(
      /reduce\s+propofol|administer\s+atropine|safe\s+to\s+proceed|dosing\s+recommendation/,
    );
  });
});
