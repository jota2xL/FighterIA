export interface Badge {
  id: number;
  name: string;
  display_name: string;
  description: string;
  icon_url: string | null;
  category: "streak" | "score" | "volume" | "technique" | "special";
  rarity: "common" | "rare" | "epic" | "legendary";
  xp_reward: number;
  earned_at: string | null;
  is_earned: boolean;
}

export interface BadgesResponse {
  earned: Badge[];
  available: Badge[];
  total_earned: number;
  total_available: number;
}

export interface XPTransaction {
  id: number;
  amount: number;
  reason: string;
  created_at: string;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: number;
  username: string;
  full_name: string;
  avatar_url: string | null;
  xp: number;
  belt_level: string;
  analyses_count: number;
}
