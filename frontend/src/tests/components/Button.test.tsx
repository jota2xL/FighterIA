import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Button from "@/components/ui/Button";

describe("Button", () => {

  it("renders the button with its label text", () => {
    // Arrange / Act
    render(<Button onClick={vi.fn()}>Enviar</Button>);

    // Assert
    expect(screen.getByRole("button", { name: /enviar/i })).toBeInTheDocument();
  });

  it("calls onClick handler when clicked", () => {
    // Arrange
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Clic aquí</Button>);

    // Act
    fireEvent.click(screen.getByRole("button"));

    // Assert
    expect(handleClick).toHaveBeenCalledOnce();
  });

  it("is disabled when disabled prop is true", () => {
    // Arrange / Act
    render(<Button disabled>Desactivado</Button>);

    // Assert
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("is disabled when isLoading prop is true", () => {
    // Arrange / Act
    render(<Button isLoading>Cargando</Button>);

    // Assert
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("shows a spinner when isLoading is true", () => {
    // Arrange / Act
    render(<Button isLoading>Procesando...</Button>);

    // Assert — spinner is a decorative span with animate-spin class
    const spinner = document.querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
  });

  it("does not call onClick when the button is disabled", () => {
    // Arrange
    const handleClick = vi.fn();
    render(<Button disabled onClick={handleClick}>No clicar</Button>);

    // Act
    fireEvent.click(screen.getByRole("button"));

    // Assert
    expect(handleClick).not.toHaveBeenCalled();
  });

  it("applies the danger variant class when variant is danger", () => {
    // Arrange / Act
    render(<Button variant="danger">Eliminar</Button>);

    // Assert
    const btn = screen.getByRole("button");
    expect(btn.className).toMatch(/danger|red-900/i);
  });

  it("applies a custom className alongside default classes", () => {
    // Arrange / Act
    render(<Button className="mt-8">Test</Button>);

    // Assert
    expect(screen.getByRole("button").className).toContain("mt-8");
  });
});
