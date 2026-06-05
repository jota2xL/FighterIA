/**
 * Integration tests for GymManagementPage.
 * Uses MSW to mock CRM API calls and verifies page content and modal behaviour.
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { server } from "@/mocks/server";
import GymManagementPage from "@/pages/GymManagementPage";
import { useAuthStore } from "@/store/auth.store";
import { mockUser } from "@/mocks/fixtures/users";

const BASE = "http://localhost:8000";

const mockGyms = [
  {
    id: 1,
    name: "Dragon Gym Madrid",
    city: "Madrid",
    country: "España",
    plan: "pro",
    created_at: "2026-05-01T10:00:00",
  },
  {
    id: 2,
    name: "Tiger Dojo Barcelona",
    city: "Barcelona",
    country: "España",
    plan: "free",
    created_at: "2026-05-10T08:00:00",
  },
];

const renderPage = () => {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <GymManagementPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe("GymManagementPage", () => {

  beforeEach(() => {
    // Seed Zustand with a logged-in user
    useAuthStore.setState({
      user: mockUser,
      accessToken: "fake-token",
      refreshToken: "fake-refresh",
    });

    // Default MSW handler: return the two mock gyms
    server.use(
      http.get(`${BASE}/crm/gyms`, () => HttpResponse.json(mockGyms))
    );
  });

  it("muestra spinner mientras se cargan los datos", () => {
    // Arrange / Act — render before the query resolves
    renderPage();

    // Assert — Spinner component renders .animate-spin during loading
    expect(document.querySelector(".animate-spin")).toBeInTheDocument();
  });

  it("renderiza la lista de gimnasios cuando los datos están disponibles", async () => {
    // Arrange / Act
    renderPage();

    // Assert — wait for gym names to appear after the fetch resolves
    await waitFor(() => {
      expect(screen.getByText("Dragon Gym Madrid")).toBeInTheDocument();
    });
    expect(screen.getByText("Tiger Dojo Barcelona")).toBeInTheDocument();
  });

  it("renderiza el plan de cada gimnasio", async () => {
    // Arrange / Act
    renderPage();

    // Assert — plan badges must appear
    await waitFor(() => {
      expect(screen.getByText("pro")).toBeInTheDocument();
    });
    expect(screen.getByText("free")).toBeInTheDocument();
  });

  it("muestra botón 'Nuevo Gimnasio' en el header", () => {
    // Arrange / Act
    renderPage();

    // Assert
    expect(screen.getByRole("button", { name: /nuevo gimnasio/i })).toBeInTheDocument();
  });

  it("muestra modal al hacer click en 'Nuevo Gimnasio'", async () => {
    // Arrange
    renderPage();

    // Act
    fireEvent.click(screen.getByRole("button", { name: /nuevo gimnasio/i }));

    // Assert — modal title appears
    await waitFor(() => {
      expect(screen.getByText(/nuevo gimnasio/i)).toBeInTheDocument();
    });
    // The modal form field for gym name should be present
    expect(screen.getByPlaceholderText(/crossfit madrid centro/i)).toBeInTheDocument();
  });

  it("cierra modal al hacer click en cancelar", async () => {
    // Arrange
    renderPage();
    fireEvent.click(screen.getByRole("button", { name: /nuevo gimnasio/i }));
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/crossfit madrid centro/i)).toBeInTheDocument();
    });

    // Act — click the cancel button inside the modal
    fireEvent.click(screen.getByRole("button", { name: /cancelar/i }));

    // Assert — the name input (inside modal) should no longer be visible
    await waitFor(() => {
      expect(screen.queryByPlaceholderText(/crossfit madrid centro/i)).not.toBeInTheDocument();
    });
  });

  it("muestra estado vacío cuando no hay gimnasios", async () => {
    // Arrange — override handler to return empty list
    server.use(
      http.get(`${BASE}/crm/gyms`, () => HttpResponse.json([]))
    );

    // Act
    renderPage();

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/no hay gimnasios registrados/i)).toBeInTheDocument();
    });
  });

  it("muestra error cuando la API falla", async () => {
    // Arrange — simulate server error
    server.use(
      http.get(`${BASE}/crm/gyms`, () =>
        HttpResponse.json({ detail: "Server error" }, { status: 500 })
      )
    );

    // Act
    renderPage();

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/error cargando gimnasios/i)).toBeInTheDocument();
    });
  });

  it("renderiza el encabezado de la página", () => {
    // Arrange / Act
    renderPage();

    // Assert
    expect(screen.getByText("Gimnasios")).toBeInTheDocument();
  });
});
