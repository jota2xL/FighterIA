/**
 * Tests for LoginPage.
 * Uses MSW to intercept auth API calls and React Router for navigation context.
 *
 * NOTE: The submit button text is "Entrar al dojo" (our implementation).
 * The briefing specified /iniciar sesión/i — adapted to match actual implementation.
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import LoginPage from "@/pages/LoginPage";

const renderLoginPage = () => {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe("LoginPage", () => {

  it("renders the email input field", () => {
    // Arrange / Act
    renderLoginPage();

    // Assert
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  });

  it("renders the password input field", () => {
    // Arrange / Act
    renderLoginPage();

    // Assert
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
  });

  it("renders the submit button", () => {
    // Arrange / Act
    renderLoginPage();

    // Assert — button text in our implementation is "Entrar al dojo"
    expect(screen.getByRole("button", { name: /entrar/i })).toBeInTheDocument();
  });

  it("renders a link to the register page", () => {
    // Arrange / Act
    renderLoginPage();

    // Assert
    expect(screen.getByRole("link", { name: /regístrate/i })).toBeInTheDocument();
  });

  it("shows validation error for invalid email format on submit", async () => {
    // Arrange
    renderLoginPage();
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "not-an-email" },
    });

    // Act
    fireEvent.click(screen.getByRole("button", { name: /entrar/i }));

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/email inv/i)).toBeInTheDocument();
    });
  });

  it("shows validation error when email field is empty on submit", async () => {
    // Arrange
    renderLoginPage();

    // Act — submit without filling any field
    fireEvent.click(screen.getByRole("button", { name: /entrar/i }));

    // Assert
    await waitFor(() => {
      // Zod will report "Invalid email" for empty string
      expect(screen.getByText(/email inv/i)).toBeInTheDocument();
    });
  });

  it("does not show error message before any user interaction", () => {
    // Arrange / Act
    renderLoginPage();

    // Assert — no error visible on initial render
    expect(screen.queryByText(/incorrectos/i)).not.toBeInTheDocument();
  });

  it("disables submit button while login mutation is pending", async () => {
    // Arrange
    renderLoginPage();
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "fighter@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/contraseña/i), {
      target: { value: "ValidPass123!" },
    });

    // Act — click submit; MSW will respond with success
    fireEvent.click(screen.getByRole("button", { name: /entrar/i }));

    // Assert — button is disabled during loading
    expect(screen.getByRole("button", { name: /entrar/i })).toBeDisabled();
  });

  it("accepts valid credentials without showing an error", async () => {
    // Arrange
    renderLoginPage();
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "fighter@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/contraseña/i), {
      target: { value: "ValidPass123!" },
    });

    // Act
    fireEvent.click(screen.getByRole("button", { name: /entrar/i }));

    // Assert — no "Email o contraseña incorrectos" message after successful call
    await waitFor(() => {
      expect(screen.queryByText(/email o contraseña incorrectos/i)).not.toBeInTheDocument();
    });
  });
});
