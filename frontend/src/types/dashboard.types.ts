import type { BeltLevel } from "./auth.types";

export interface DashboardStats {
  total_analyses: number;
  best_score: number | null;
  average_score: number | null;
  favorite_discipline: string | null;
  most_analyzed_technique: string | null;
  xp: number;
  belt_level: BeltLevel;
  xp_for_next_belt: number | null;
  xp_next_belt_name: string | null;
  current_streak: number;
  max_streak: number;
  streak_shields: number;
}

export interface ProgressDataPoint {
  date: string;
  score: number;
  technique: string;
  discipline: string;
}

export interface ProgressResponse {
  data: ProgressDataPoint[];
  discipline_id: number | null;
  period_days: number;
}

export interface HeatmapDay {
  date: string;
  count: number;
}

export interface HeatmapResponse {
  data: HeatmapDay[];
  total_days_active: number;
}

export interface BeltProgressInfo {
  current_belt: BeltLevel;
  current_xp: number;
  xp_for_next: number;
  xp_needed: number;
  next_belt: BeltLevel | null;
  progress_percent: number;
}

export interface RecentAnalysis {
  id: number;
  technique_display_name: string;
  discipline_name: string;
  global_score: number | null;
  created_at: string;
  video_overlay_url: string;
}
