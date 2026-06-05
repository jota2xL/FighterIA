/**
 * Tests for FeedbackList.
 * Verifies that feedback items render correctly and expand on click.
 */
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import FeedbackList from "@/components/analysis/FeedbackList";
import type { FeedbackItem } from "@/types/analysis.types";

const makeFeedback = (overrides: Partial<FeedbackItem> = {}): FeedbackItem => ({
  priority_order: 1,
  correction_title: "Extensión de codo insuficiente",
  correction_text: "Tu codo derecho alcanza 145°...",
  biomechanical_explanation: "La extensión completa del codo maximiza el alcance.",
  exercise_suggestion: "Practica shadow boxing con espejo.",
  impact_score: 0.85,
  ...overrides,
});

describe("FeedbackList", () => {

  it("renders nothing when feedback array is empty", () => {
    // Arrange / Act
    const { container } = render(<FeedbackList feedback={[]} />);

    // Assert
    expect(container.firstChild).toBeNull();
  });

  it("renders a button with the correction title", () => {
    // Arrange / Act
    render(<FeedbackList feedback={[makeFeedback()]} />);

    // Assert
    expect(screen.getByRole("button", { name: /extensi/i })).toBeInTheDocument();
  });

  it("shows the priority number badge", () => {
    // Arrange / Act
    render(<FeedbackList feedback={[makeFeedback({ priority_order: 1 })]} />);

    // Assert — priority badge with "1"
    expect(screen.getByText("1")).toBeInTheDocument();
  });

  it("renders all feedback items when multiple are provided", () => {
    // Arrange
    const items = [
      makeFeedback({ priority_order: 1, correction_title: "Error de codo" }),
      makeFeedback({ priority_order: 2, correction_title: "Error de cadera" }),
    ];

    // Act
    render(<FeedbackList feedback={items} />);

    // Assert
    expect(screen.getByRole("button", { name: /codo/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /cadera/i })).toBeInTheDocument();
  });

  it("shows the correction text when first item is expanded by default", () => {
    // Arrange — first item (idx=0) is open by default
    const feedback = [makeFeedback()];

    // Act
    render(<FeedbackList feedback={feedback} />);

    // Assert — correction text is visible without clicking
    expect(screen.getByText(/145°/i)).toBeInTheDocument();
  });

  it("expands a collapsed item when its button is clicked", () => {
    // Arrange — two items; first is open by default, click second to open it
    const items = [
      makeFeedback({ priority_order: 1, correction_title: "Error codo", correction_text: "Texto codo" }),
      makeFeedback({ priority_order: 2, correction_title: "Error cadera", correction_text: "Texto cadera" }),
    ];
    render(<FeedbackList feedback={items} />);

    // Act — click the second item button
    fireEvent.click(screen.getByRole("button", { name: /cadera/i }));

    // Assert — second item's correction text is now visible
    expect(screen.getByText(/texto cadera/i)).toBeInTheDocument();
  });

  it("shows the biomechanical explanation section when expanded", () => {
    // Arrange
    render(<FeedbackList feedback={[makeFeedback()]} />);

    // Assert — visible by default (first item open)
    expect(screen.getByText(/extensión completa del codo/i)).toBeInTheDocument();
  });

  it("shows the exercise suggestion section when expanded", () => {
    // Arrange
    render(<FeedbackList feedback={[makeFeedback()]} />);

    // Assert
    expect(screen.getByText(/shadow boxing/i)).toBeInTheDocument();
  });
});
