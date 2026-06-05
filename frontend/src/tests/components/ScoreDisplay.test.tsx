/**
 * Tests for ScoreDisplay.
 * Uses an `analysis` object prop (our actual implementation).
 * The briefing used individual score props — adapted to match actual component API.
 *
 * NOTE: Our ScoreDisplay uses score.toFixed(0), so 73.5 is displayed as "74".
 * Tests use integer scores to avoid rounding ambiguity. See DEF-005 in QA report.
 */
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import ScoreDisplay from "@/components/analysis/ScoreDisplay";
import type { Analysis } from "@/types/analysis.types";
import { mockAnalysis } from "@/mocks/fixtures/analysis";

const makeAnalysis = (overrides: Partial<Analysis> = {}): Analysis => ({
  ...mockAnalysis,
  ...overrides,
});

describe("ScoreDisplay", () => {

  it("renders the global score value", () => {
    // Arrange
    const analysis = makeAnalysis({ global_score: 73 });

    // Act
    render(<ScoreDisplay analysis={analysis} />);

    // Assert
    expect(screen.getByText("73")).toBeInTheDocument();
  });

  it("renders all four sub-score labels", () => {
    // Arrange / Act
    render(<ScoreDisplay analysis={makeAnalysis()} />);

    // Assert
    expect(screen.getByText(/potencia/i)).toBeInTheDocument();
    expect(screen.getByText(/equilibrio/i)).toBeInTheDocument();
    expect(screen.getByText(/alineaci/i)).toBeInTheDocument();
    expect(screen.getByText(/velocidad/i)).toBeInTheDocument();
  });

  it("displays a dash when global score is null", () => {
    // Arrange
    const analysis = makeAnalysis({ global_score: null });

    // Act
    render(<ScoreDisplay analysis={analysis} />);

    // Assert
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("applies the excellent color class for score >= 80", () => {
    // Arrange
    const analysis = makeAnalysis({ global_score: 85 });

    // Act
    render(<ScoreDisplay analysis={analysis} />);

    // Assert — Tailwind class includes "excellent"
    const scoreEl = screen.getByText("85");
    expect(scoreEl.className).toMatch(/excellent/i);
  });

  it("applies the good color class for score between 60 and 79", () => {
    // Arrange
    const analysis = makeAnalysis({ global_score: 70 });

    // Act
    render(<ScoreDisplay analysis={analysis} />);

    // Assert
    const scoreEl = screen.getByText("70");
    expect(scoreEl.className).toMatch(/good/i);
  });

  it("applies the poor color class for score below 60", () => {
    // Arrange
    const analysis = makeAnalysis({ global_score: 45 });

    // Act
    render(<ScoreDisplay analysis={analysis} />);

    // Assert
    const scoreEl = screen.getByText("45");
    expect(scoreEl.className).toMatch(/poor/i);
  });

  it("renders the boundary score 80 as excellent", () => {
    // Arrange
    const analysis = makeAnalysis({ global_score: 80 });

    // Act
    render(<ScoreDisplay analysis={analysis} />);

    // Assert
    const scoreEl = screen.getByText("80");
    expect(scoreEl.className).toMatch(/excellent/i);
  });

  it("renders the /100 label next to the global score", () => {
    // Arrange / Act
    render(<ScoreDisplay analysis={makeAnalysis({ global_score: 73 })} />);

    // Assert
    expect(screen.getByText("/100")).toBeInTheDocument();
  });

  it("renders the Puntuación Global label", () => {
    // Arrange / Act
    render(<ScoreDisplay analysis={makeAnalysis()} />);

    // Assert
    expect(screen.getByText(/puntuaci/i)).toBeInTheDocument();
  });
});
