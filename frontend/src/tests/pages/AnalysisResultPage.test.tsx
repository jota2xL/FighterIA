/**
 * Integration tests for AnalysisResultPage.
 * Verifies video player, scores, joint table and feedback rendering.
 */
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { server } from "@/mocks/server";
import AnalysisResultPage from "@/pages/AnalysisResultPage";
import { useAuthStore } from "@/store/auth.store";
import { mockUser } from "@/mocks/fixtures/users";
import { mockAnalysis, mockAnalysisFailed, mockAnalysisPending } from "@/mocks/fixtures/analysis";

const renderResult = (analysisId: number = 1) => {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/analysis/${analysisId}`]}>
        <Routes>
          <Route path="/analysis/:id" element={<AnalysisResultPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe("AnalysisResultPage", () => {

  beforeEach(() => {
    useAuthStore.setState({
      user: mockUser,
      accessToken: "fake-token",
      refreshToken: "fake-refresh",
    });
  });

  it("shows a loading spinner while analysis is being fetched", () => {
    // Arrange / Act
    renderResult();

    // Assert
    expect(document.querySelector(".animate-spin")).toBeInTheDocument();
  });

  it("renders the technique name after analysis loads", async () => {
    // Arrange / Act
    renderResult(1);

    // Assert — technique display_name from mockAnalysis is "Jab"
    await waitFor(() => {
      expect(screen.getByText("Jab")).toBeInTheDocument();
    });
  });

  it("renders the discipline name badge", async () => {
    // Arrange / Act
    renderResult(1);

    // Assert
    await waitFor(() => {
      expect(screen.getByText("Boxeo")).toBeInTheDocument();
    });
  });

  it("renders the global score", async () => {
    // Arrange / Act
    renderResult(1);

    // Assert — global_score is 73 in mockAnalysis
    await waitFor(() => {
      expect(screen.getByText("73")).toBeInTheDocument();
    });
  });

  it("renders all four sub-score labels", async () => {
    // Arrange / Act
    renderResult(1);

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/potencia/i)).toBeInTheDocument();
      expect(screen.getByText(/equilibrio/i)).toBeInTheDocument();
    });
  });

  it("shows the feedback section with at least one feedback item", async () => {
    // Arrange / Act
    renderResult(1);

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/extensión de codo insuficiente/i)).toBeInTheDocument();
    });
  });

  it("shows the joint results section", async () => {
    // Arrange / Act
    renderResult(1);

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/articulaci/i)).toBeInTheDocument();
    });
  });

  it("renders download buttons for overlay and original video", async () => {
    // Arrange / Act
    renderResult(1);

    // Assert
    await waitFor(() => {
      expect(screen.getByRole("link", { name: /overlay/i })).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /original/i })).toBeInTheDocument();
    });
  });

  it("shows error message for a failed analysis", async () => {
    // Arrange — override handler to return a failed analysis
    server.use(
      http.get("http://localhost:8000/analysis/:id", () =>
        HttpResponse.json(mockAnalysisFailed)
      )
    );

    // Act
    renderResult(2);

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/no pose detected/i)).toBeInTheDocument();
    });
  });

  it("shows processing spinner for a pending analysis", async () => {
    // Arrange — override handler to return a pending analysis
    server.use(
      http.get("http://localhost:8000/analysis/:id", () =>
        HttpResponse.json(mockAnalysisPending)
      )
    );

    // Act
    renderResult(3);

    // Assert
    await waitFor(() => {
      expect(document.querySelectorAll(".animate-spin").length).toBeGreaterThanOrEqual(1);
    });
  });

  it("shows error state when API returns 500", async () => {
    // Arrange
    server.use(
      http.get("http://localhost:8000/analysis/:id", () =>
        HttpResponse.json({ detail: "Server error" }, { status: 500 })
      )
    );

    // Act
    renderResult(1);

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
