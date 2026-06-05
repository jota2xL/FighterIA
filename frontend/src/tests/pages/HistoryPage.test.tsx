/**
 * Integration tests for HistoryPage.
 * Verifies history list rendering, empty state and discipline filter display.
 */
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { server } from "@/mocks/server";
import HistoryPage from "@/pages/HistoryPage";
import { useAuthStore } from "@/store/auth.store";
import { mockUser } from "@/mocks/fixtures/users";

const renderHistory = () => {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <HistoryPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe("HistoryPage", () => {

  beforeEach(() => {
    useAuthStore.setState({
      user: mockUser,
      accessToken: "fake-token",
      refreshToken: "fake-refresh",
    });
  });

  it("renders the page title", () => {
    // Arrange / Act
    renderHistory();

    // Assert
    expect(screen.getByText(/historial de análisis/i)).toBeInTheDocument();
  });

  it("renders a link to start a new analysis", () => {
    // Arrange / Act
    renderHistory();

    // Assert
    expect(screen.getByRole("link", { name: /nuevo análisis/i })).toBeInTheDocument();
  });

  it("shows a loading spinner while history is being fetched", () => {
    // Arrange / Act
    renderHistory();

    // Assert
    expect(document.querySelector(".animate-spin")).toBeInTheDocument();
  });

  it("renders analysis cards after successful fetch", async () => {
    // Arrange / Act
    renderHistory();

    // Assert — MSW returns one item with technique "Jab"
    await waitFor(() => {
      expect(screen.getByText("Jab")).toBeInTheDocument();
    });
  });

  it("shows empty state when user has no analyses", async () => {
    // Arrange — override handler to return empty list
    server.use(
      http.get("http://localhost:8000/analysis/me", () =>
        HttpResponse.json({ items: [], total: 0, page: 1, limit: 20, pages: 0 })
      )
    );

    // Act
    renderHistory();

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/sin análisis/i)).toBeInTheDocument();
    });
  });

  it("shows error message when API call fails", async () => {
    // Arrange
    server.use(
      http.get("http://localhost:8000/analysis/me", () =>
        HttpResponse.json({ detail: "Server error" }, { status: 500 })
      )
    );

    // Act
    renderHistory();

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("renders discipline filter buttons after disciplines load", async () => {
    // Arrange / Act
    renderHistory();

    // Assert — "Todas" filter button is always present
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /todas/i })).toBeInTheDocument();
    });
  });
});
