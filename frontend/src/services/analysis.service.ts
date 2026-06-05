import apiClient from "./api.client";
import type { Analysis, AnalysisList, CompareResponse, Discipline, Technique } from "@/types/analysis.types";
import { useAuthStore } from "@/store/auth.store";

export const analysisService = {
  create: (techniqueId: number, videoFile: File) => {
    const form = new FormData();
    form.append("technique_id", String(techniqueId));
    form.append("video", videoFile);
    return apiClient
      .post<Analysis>("/analysis", form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },

  getById: (id: number) =>
    apiClient.get<Analysis>(`/analysis/${id}`).then((r) => r.data),

  getMyHistory: (page = 1, limit = 20, disciplineId?: number) =>
    apiClient
      .get<AnalysisList>("/analysis/me", {
        params: { page, limit, discipline_id: disciplineId },
      })
      .then((r) => r.data),

  compare: (id1: number, id2: number) =>
    apiClient
      .get<CompareResponse>("/analysis/compare", { params: { id1, id2 } })
      .then((r) => r.data),

  getOverlayUrl: (id: number) => {
    const token = useAuthStore.getState().accessToken ?? "";
    return `${import.meta.env.VITE_API_BASE_URL}/analysis/${id}/download/overlay?token=${encodeURIComponent(token)}`;
  },

  getOriginalUrl: (id: number) => {
    const token = useAuthStore.getState().accessToken ?? "";
    return `${import.meta.env.VITE_API_BASE_URL}/analysis/${id}/download/original?token=${encodeURIComponent(token)}`;
  },
};

export const disciplineService = {
  getAll: () =>
    apiClient.get<Discipline[]>("/disciplines").then((r) => r.data),

  getTechniques: (disciplineId: number) =>
    apiClient
      .get<Technique[]>(`/disciplines/${disciplineId}/techniques`)
      .then((r) => r.data),
};
