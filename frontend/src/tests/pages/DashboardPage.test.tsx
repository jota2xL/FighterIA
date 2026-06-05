/**
 * Integration tests for DashboardPage.
 * Uses MSW to mock all API calls and verifies page content renders correctly.
 */
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { server } from "@/mocks/server";
import DashboardPage from "@/pages/DashboardPage";
import { useAuthStore } from "@/store/auth.store";
import { mockUser } from "@/mocks/fixtures/users";

const renderDashboard = () => {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe("DashboardPage", () => {

  beforeEach(() => {
    // Seed the Zustand store with a logged-in user for each test
    useAuthStore.setState({
      user: mockUser,
      accessToken: "fake-token",
      refreshToken: "fake-refresh",
    });
  });

  it("shows the user greeting with username", async () => {
    // Arrange / Act
    renderDashboard();

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/hola/i)).toBeInTheDocument();
    });
  });

  it("renders the Nuevo análisis button", () => {
    // Arrange / Act
    renderDashboard();

    // Assert
    expect(screen.getByRole("link", { name: /nuevo análisis/i })).toBeInTheDocument();
  });

  it("shows loading state while stats are being fetched", () => {
    // Arrange / Act
    renderDashboard();

    // Assert — at least one spinner should appear during initial load
    expect(document.querySelector(".animate-spin")).toBeInTheDocument();
  });

  it("renders stat cards after stats load successfully", async () => {
    // Arrange / Act
    renderDashboard();

    // Assert — wait for the stats to appear
    await waitFor(() => {
      expect(screen.getByText(/análisis realizados/i)).toBeInTheDocument();
    });
  });

  it("displays total analyses count from the API", async () => {
    // Arrange / Act
    renderDashboard();

    // Assert — MSW returns total_analyses: 5
    await waitFor(() => {
      expect(screen.getByText("5")).toBeInTheDocument();
    });
  });

  it("shows error state when stats API fails", async () => {
    // Arrange — override MSW handler to simulate server error
    server.use(
      http.get("http://localhost:8000/dashboard/me", () =>
        HttpResponse.json({ detail: "Server error" }, { status: 500 })
      )
    );

    // Act
    renderDashboard();

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("renders a link to the history page", () => {
    // Arrange / Act
    renderDashboard();

    // Assert
    expect(screen.getByRole("link", { name: /ver todos/i })).toBeInTheDocument();
  });
});
