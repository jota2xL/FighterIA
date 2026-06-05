import apiClient from "./api.client";
import type { Badge, BadgesResponse, LeaderboardEntry } from "@/types/gamification.types";

// Backend shapes (not exported — internal to this service)
interface _BackendBadge {
  id: number;
  name: string;
  display_name: string;
  description: string;
  level: string; // bronze | silver | gold
  icon_name: string;
  xp_reward: number;
}

interface _BackendUserBadge {
  badge_id: number;
  display_name: string;
  icon_name: string;
  level: string;
  xp_reward: number;
  earned_at: string;
}

const LEVEL_TO_RARITY: Record<string, Badge["rarity"]> = {
  bronze: "common",
  silver: "rare",
  gold: "epic",
};

const NAME_TO_CATEGORY: Record<string, Badge["category"]> = {
  first_analysis: "volume",
  streak_7: "streak",
  streak_30: "streak",
  score_100: "score",
  muay_thai_50: "technique",
  bjj_50: "technique",
  boxing_50: "technique",
  belt_negro: "special",
};

export const gamificationService = {
  getBadges: async (): Promise<BadgesResponse> => {
    const [allBadges, earnedBadges] = await Promise.all([
      apiClient.get<_BackendBadge[]>("/gamification/badges").then((r) => r.data),
      apiClient.get<_BackendUserBadge[]>("/gamification/me/badges").then((r) => r.data),
    ]);

    const earnedMap = new Map(earnedBadges.map((ub) => [ub.badge_id, ub.earned_at]));

    const all: Badge[] = allBadges.map((b) => ({
      id: b.id,
      name: b.name,
      display_name: b.display_name,
      description: b.description,
      icon_url: null,
      category: NAME_TO_CATEGORY[b.name] ?? "special",
      rarity: LEVEL_TO_RARITY[b.level] ?? "common",
      xp_reward: b.xp_reward,
      earned_at: earnedMap.get(b.id) ?? null,
      is_earned: earnedMap.has(b.id),
    }));

    const earned = all.filter((b) => b.is_earned);
    const available = all.filter((b) => !b.is_earned);

    return {
      earned,
      available,
      total_earned: earned.length,
      total_available: all.length,
    };
  },

  getLeaderboard: (limit = 20) =>
    apiClient
      .get<LeaderboardEntry[]>("/gamification/ranking", { params: { limit } })
      .then((r) => r.data),

  claimDailyBonus: () =>
    apiClient.post("/gamification/daily-bonus").then((r) => r.data),
};
