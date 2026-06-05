import apiClient from "./api.client";
import type { BadgesResponse, LeaderboardEntry } from "@/types/gamification.types";

export const gamificationService = {
  getBadges: () =>
    apiClient.get<BadgesResponse>("/gamification/badges").then((r) => r.data),

  getLeaderboard: (limit: number = 20) =>
    apiClient
      .get<LeaderboardEntry[]>("/gamification/leaderboard", {
        params: { limit },
      })
      .then((r) => r.data),

  claimDailyBonus: () =>
    apiClient.post("/gamification/daily-bonus").then((r) => r.data),
};
