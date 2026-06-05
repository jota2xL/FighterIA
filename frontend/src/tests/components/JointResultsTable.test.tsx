/**
 * Tests for JointResultsTable.
 * Verifies correct rendering of joint measurement data with status indicators.
 */
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import JointResultsTable from "@/components/analysis/JointResultsTable";
import type { JointResult } from "@/types/analysis.types";

const correctJoint: JointResult = {
  joint_name: "right_shoulder",
  measured_angle: 88.0,
  reference_min: 80,
  reference_max: 100,
  optimal_angle: 90,
  is_correct: true,
  deviation: -2.0,
};

const incorrectJoint: JointResult = {
  joint_name: "right_elbow",
  measured_angle: 145.2,
  reference_min: 165,
  reference_max: 180,
  optimal_angle: 175,
  is_correct: false,
  deviation: -29.8,
};

describe("JointResultsTable", () => {

  it("renders nothing when joint results list is empty", () => {
    // Arrange / Act
    const { container } = render(<JointResultsTable joints={[]} />);

    // Assert
    expect(container.firstChild).toBeNull();
  });

  it("renders the joint name for each row", () => {
    // Arrange / Act
    render(<JointResultsTable joints={[correctJoint]} />);

    // Assert — joint name with underscores replaced by spaces
    expect(screen.getByText(/right shoulder/i)).toBeInTheDocument();
  });

  it("renders the measured angle value", () => {
    // Arrange / Act
    render(<JointResultsTable joints={[correctJoint]} />);

    // Assert
    expect(screen.getByText(/88\.0°/)).toBeInTheDocument();
  });

  it("shows a checkmark indicator for correct joints", () => {
    // Arrange / Act
    render(<JointResultsTable joints={[correctJoint]} />);

    // Assert — aria-label Correcto is present
    expect(screen.getByLabelText(/correcto/i)).toBeInTheDocument();
  });

  it("shows an error indicator for incorrect joints", () => {
    // Arrange / Act
    render(<JointResultsTable joints={[incorrectJoint]} />);

    // Assert
    expect(screen.getByLabelText(/incorrecto/i)).toBeInTheDocument();
  });

  it("renders column headers", () => {
    // Arrange / Act
    render(<JointResultsTable joints={[correctJoint]} />);

    // Assert — look for the Articulación header
    expect(screen.getByText(/articulaci/i)).toBeInTheDocument();
  });

  it("renders multiple joint rows", () => {
    // Arrange / Act
    render(<JointResultsTable joints={[correctJoint, incorrectJoint]} />);

    // Assert — both joints are displayed
    expect(screen.getByText(/right shoulder/i)).toBeInTheDocument();
    expect(screen.getByText(/right elbow/i)).toBeInTheDocument();
  });
});
