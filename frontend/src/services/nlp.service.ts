import apiClient from "./api.client";

interface NlpScores {
  potencia: number;
  equilibrio: number;
  alineacion: number;
  velocidad: number;
}

interface NlpFeedbackResponse {
  feedback: string;
}

export const nlpService = {
  getNlpFeedback: (scores: NlpScores) =>
    apiClient
      .post<NlpFeedbackResponse>("/nlp/feedback", scores)
      .then((r) => r.data),
};
