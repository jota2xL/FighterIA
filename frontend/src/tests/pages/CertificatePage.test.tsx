/**
 * Integration tests for CertificatePage.
 * Uses MSW to mock the blockchain verification endpoint.
 * Route params are injected via MemoryRouter initialEntries.
 */
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { server } from "@/mocks/server";
import CertificatePage from "@/pages/CertificatePage";
import { useAuthStore } from "@/store/auth.store";
import { mockUser } from "@/mocks/fixtures/users";

const BASE = "http://localhost:8000";

const VALID_HASH = "a".repeat(64);   // 64-char placeholder representing a real certificate

const mockValidResponse = {
  valid: true,
  certificate: {
    id: 1,
    analysis_id: 42,
    hash: VALID_HASH,
    issued_at: "2026-06-05T12:00:00",
    verified_count: 3,
  },
  message: "Certificado válido y verificado correctamente.",
};

const mockInvalidResponse = {
  valid: false,
  certificate: null,
  message: "Certificado no encontrado.",
};

const renderPage = (hash: string) => {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/certificates/${hash}`]}>
        <Routes>
          <Route path="/certificates/:hash" element={<CertificatePage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe("CertificatePage", () => {

  beforeEach(() => {
    useAuthStore.setState({
      user: mockUser,
      accessToken: "fake-token",
      refreshToken: "fake-refresh",
    });
  });

  it("muestra spinner mientras verifica el certificado", () => {
    // Arrange — set up handler but don't wait for resolution
    server.use(
      http.get(`${BASE}/blockchain/certificates/${VALID_HASH}`, () =>
        HttpResponse.json(mockValidResponse)
      )
    );

    // Act
    renderPage(VALID_HASH);

    // Assert — Spinner renders during pending query
    expect(document.querySelector(".animate-spin")).toBeInTheDocument();
  });

  it("muestra datos del certificado cuando valid=true", async () => {
    // Arrange
    server.use(
      http.get(`${BASE}/blockchain/certificates/${VALID_HASH}`, () =>
        HttpResponse.json(mockValidResponse)
      )
    );

    // Act
    renderPage(VALID_HASH);

    // Assert — certificate details section is shown
    await waitFor(() => {
      expect(screen.getByText(/certificado válido/i)).toBeInTheDocument();
    });
    // Hash value is displayed in the details card
    expect(screen.getByText(VALID_HASH)).toBeInTheDocument();
    // Analysis ID is shown
    expect(screen.getByText("#42")).toBeInTheDocument();
  });

  it("muestra el conteo de verificaciones cuando el certificado es válido", async () => {
    // Arrange
    server.use(
      http.get(`${BASE}/blockchain/certificates/${VALID_HASH}`, () =>
        HttpResponse.json(mockValidResponse)
      )
    );

    // Act
    renderPage(VALID_HASH);

    // Assert — verified_count = 3 is displayed
    await waitFor(() => {
      expect(screen.getByText("3")).toBeInTheDocument();
    });
  });

  it("muestra mensaje de error cuando valid=false", async () => {
    // Arrange
    const invalidHash = "b".repeat(64);
    server.use(
      http.get(`${BASE}/blockchain/certificates/${invalidHash}`, () =>
        HttpResponse.json(mockInvalidResponse)
      )
    );

    // Act
    renderPage(invalidHash);

    // Assert — invalid certificate state is shown
    await waitFor(() => {
      expect(screen.getByText(/certificado no válido/i)).toBeInTheDocument();
    });
    // The message from the API is also displayed
    expect(screen.getByText(/no encontrado/i)).toBeInTheDocument();
  });

  it("muestra imagen QR cuando el certificado es válido", async () => {
    // Arrange
    server.use(
      http.get(`${BASE}/blockchain/certificates/${VALID_HASH}`, () =>
        HttpResponse.json(mockValidResponse)
      )
    );

    // Act
    renderPage(VALID_HASH);

    // Assert — the QR image element is present
    await waitFor(() => {
      const qrImg = screen.getByAltText(new RegExp(`QR del certificado ${VALID_HASH}`, "i"));
      expect(qrImg).toBeInTheDocument();
    });
  });

  it("la imagen QR apunta a la URL del servicio QR externo", async () => {
    // Arrange
    server.use(
      http.get(`${BASE}/blockchain/certificates/${VALID_HASH}`, () =>
        HttpResponse.json(mockValidResponse)
      )
    );

    // Act
    renderPage(VALID_HASH);

    // Assert — src must contain the qrserver.com URL with the hash
    await waitFor(() => {
      const qrImg = screen.getByAltText(new RegExp(`QR del certificado`, "i")) as HTMLImageElement;
      expect(qrImg.src).toContain("qrserver.com");
      expect(qrImg.src).toContain(encodeURIComponent(VALID_HASH));
    });
  });

  it("muestra enlace al análisis cuando el certificado es válido", async () => {
    // Arrange
    server.use(
      http.get(`${BASE}/blockchain/certificates/${VALID_HASH}`, () =>
        HttpResponse.json(mockValidResponse)
      )
    );

    // Act
    renderPage(VALID_HASH);

    // Assert — link to the analysis page is present
    await waitFor(() => {
      expect(screen.getByRole("link", { name: /ver análisis #42/i })).toBeInTheDocument();
    });
  });

  it("muestra mensaje genérico cuando el API falla completamente", async () => {
    // Arrange — simulate a network error / 500
    server.use(
      http.get(`${BASE}/blockchain/certificates/${VALID_HASH}`, () =>
        HttpResponse.json({ detail: "Server error" }, { status: 500 })
      )
    );

    // Act
    renderPage(VALID_HASH);

    // Assert — ErrorMessage component is rendered
    await waitFor(() => {
      expect(screen.getByText(/error al verificar/i)).toBeInTheDocument();
    });
  });
});
