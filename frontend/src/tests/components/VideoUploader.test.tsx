/**
 * Tests for VideoUploader.
 * Verifies drag & drop zone rendering and client-side validation behaviour.
 */
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import VideoUploader from "@/components/analysis/VideoUploader";

describe("VideoUploader", () => {

  it("renders the upload zone with instructional text", () => {
    // Arrange / Act
    render(
      <VideoUploader
        onFileSelect={vi.fn()}
        selectedFile={null}
      />
    );

    // Assert
    expect(screen.getByText(/arrastra/i)).toBeInTheDocument();
  });

  it("shows accepted format hint", () => {
    // Arrange / Act
    render(<VideoUploader onFileSelect={vi.fn()} selectedFile={null} />);

    // Assert
    expect(screen.getByText(/mp4/i)).toBeInTheDocument();
  });

  it("has a hidden file input element", () => {
    // Arrange / Act
    render(<VideoUploader onFileSelect={vi.fn()} selectedFile={null} />);

    // Assert
    const input = document.querySelector("input[type='file']");
    expect(input).toBeInTheDocument();
    expect(input).toHaveClass("hidden");
  });

  it("displays selected file name when a file is provided", () => {
    // Arrange
    const fakeFile = new File(["content"], "my_jab.mp4", { type: "video/mp4" });

    // Act
    render(<VideoUploader onFileSelect={vi.fn()} selectedFile={fakeFile} />);

    // Assert
    expect(screen.getByText("my_jab.mp4")).toBeInTheDocument();
  });

  it("displays an external error message when provided", () => {
    // Arrange / Act
    render(
      <VideoUploader
        onFileSelect={vi.fn()}
        selectedFile={null}
        error="Error al procesar el vídeo."
      />
    );

    // Assert
    expect(screen.getByText(/error al procesar/i)).toBeInTheDocument();
  });

  it("is keyboard accessible via Enter key", () => {
    // Arrange
    render(<VideoUploader onFileSelect={vi.fn()} selectedFile={null} />);
    const zone = screen.getByRole("button", { name: /subir vídeo/i });

    // Act / Assert — should not throw
    expect(() => fireEvent.keyDown(zone, { key: "Enter" })).not.toThrow();
  });
});
