/**
 * Unit tests for nlp.service.ts
 * Uses MSW to intercept HTTP calls so we verify the exact URL and payload
 * that getNlpFeedback sends to the backend.
 */
import { describe, it, expect } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/mocks/server";
import { nlpService } from "@/services/nlp.service";

const BASE = "http://localhost:8000";

describe("nlpService", () => {

  describe("getNlpFeedback", () => {

    it("llama a POST /nlp/feedback con los scores correctos", async () => {
      // Arrange — capture the request body to verify the payload
      let capturedBody: unknown = null;

      server.use(
        http.post(`${BASE}/nlp/feedback`, async ({ request }) => {
          capturedBody = await request.json();
          return HttpResponse.json({ feedback: "Texto de feedback de prueba." });
        })
      );

      const scores = {
        potencia:   75.0,
        equilibrio: 80.0,
        alineacion: 65.0,
        velocidad:  70.0,
      };

      // Act
      await nlpService.getNlpFeedback(scores);

      // Assert — the exact payload was sent
      expect(capturedBody).toEqual(scores);
    });

    it("retorna el campo feedback del response", async () => {
      // Arrange
      const expectedFeedback = "Excelente sesión — tu rendimiento general supera el nivel esperado.";
      server.use(
        http.post(`${BASE}/nlp/feedback`, () =>
          HttpResponse.json({ feedback: expectedFeedback })
        )
      );

      const scores = {
        potencia:   90.0,
        equilibrio: 92.0,
        alineacion: 88.0,
        velocidad:  91.0,
      };

      // Act
      const result = await nlpService.getNlpFeedback(scores);

      // Assert — the returned object contains the feedback field
      expect(result.feedback).toBe(expectedFeedback);
    });

    it("envía los cuatro campos dimensionales requeridos", async () => {
      // Arrange — capture request body and verify all four keys are present
      let capturedBody: Record<string, number> | null = null;

      server.use(
        http.post(`${BASE}/nlp/feedback`, async ({ request }) => {
          capturedBody = await request.json() as Record<string, number>;
          return HttpResponse.json({ feedback: "OK" });
        })
      );

      const scores = { potencia: 50, equilibrio: 55, alineacion: 45, velocidad: 60 };

      // Act
      await nlpService.getNlpFeedback(scores);

      // Assert — all four dimension keys are present in the request
      expect(capturedBody).toHaveProperty("potencia");
      expect(capturedBody).toHaveProperty("equilibrio");
      expect(capturedBody).toHaveProperty("alineacion");
      expect(capturedBody).toHaveProperty("velocidad");
    });

    it("retorna el objeto completo de respuesta del servidor", async () => {
      // Arrange
      server.use(
        http.post(`${BASE}/nlp/feedback`, () =>
          HttpResponse.json({ feedback: "Buena sesión con resultados sólidos." })
        )
      );

      const scores = { potencia: 65, equilibrio: 70, alineacion: 60, velocidad: 68 };

      // Act
      const result = await nlpService.getNlpFeedback(scores);

      // Assert — getNlpFeedback resolves to the response data object
      expect(result).toEqual({ feedback: "Buena sesión con resultados sólidos." });
    });

    it("lanza error cuando el servidor responde con 422", async () => {
      // Arrange — simulate validation rejection
      server.use(
        http.post(`${BASE}/nlp/feedback`, () =>
          HttpResponse.json(
            { detail: [{ msg: "Value is not a valid float" }] },
            { status: 422 }
          )
        )
      );

      const scores = { potencia: 50, equilibrio: 50, alineacion: 50, velocidad: 50 };

      // Act / Assert — the service must propagate the error
      await expect(nlpService.getNlpFeedback(scores)).rejects.toThrow();
    });

    it("envía el Content-Type correcto en la solicitud", async () => {
      // Arrange
      let contentType: string | null = null;

      server.use(
        http.post(`${BASE}/nlp/feedback`, ({ request }) => {
          contentType = request.headers.get("content-type");
          return HttpResponse.json({ feedback: "OK" });
        })
      );

      const scores = { potencia: 50, equilibrio: 50, alineacion: 50, velocidad: 50 };

      // Act
      await nlpService.getNlpFeedback(scores);

      // Assert — axios sets application/json by default
      expect(contentType).toContain("application/json");
    });
  });
});
