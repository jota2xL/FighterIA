import apiClient from "./api.client";
import type {
  DashboardStats,
  ProgressResponse,
  HeatmapResponse,
  BeltProgressInfo,
  RecentAnalysis,
} from "@/types/dashboard.types";

export const dashboardService = {
  getStats: () =>
    apiClient.get<DashboardStats>("/dashboard/me").then((r) => r.data),

  getProgress: (periodDays: number = 30, disciplineId?: number) =>
    apiClient
      .get<ProgressResponse>("/dashboard/me/progress", {
        params: { period_days: periodDays, discipline_id: disciplineId },
      })
      .then((r) => r.data),

  getHeatmap: (days: number = 90) =>
    apiClient
      .get<HeatmapResponse>("/dashboard/me/heatmap", { params: { days } })
      .then((r) => r.data),

  getBeltProgress: () =>
    apiClient
      .get<BeltProgressInfo>("/dashboard/me/belt-progress")
      .then((r) => r.data),

  getRecentAnalyses: (limit: number = 3) =>
    apiClient
      .get<RecentAnalysis[]>("/dashboard/me/recent", { params: { limit } })
      .then((r) => r.data),
};
