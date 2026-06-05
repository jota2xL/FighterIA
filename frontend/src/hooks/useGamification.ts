import { useQuery } from "@tanstack/react-query";
import { gamificationService } from "@/services/gamification.service";

export function useBadges() {
  return useQuery({
    queryKey: ["badges"],
    queryFn: gamificationService.getBadges,
  });
}

export function useLeaderboard(limit = 20) {
  return useQuery({
    queryKey: ["leaderboard", limit],
    queryFn: () => gamificationService.getLeaderboard(limit),
  });
}
