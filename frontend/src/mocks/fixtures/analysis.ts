import type { Analysis, AnalysisListItem } from "@/types/analysis.types";

export const mockAnalysis: Analysis = {
  id: 1,
  status: "completed",
  technique: { id: 1, display_name: "Jab", discipline: "Boxeo" },
  global_score: 73,
  power_score: 80,
  balance_score: 65,
  alignment_score: 78,
  speed_score: 70,
  xp_awarded: 30,
  joint_results: [
    {
      joint_name: "right_elbow",
      measured_angle: 145.2,
      reference_min: 165,
      reference_max: 180,
      optimal_angle: 175,
      is_correct: false,
      deviation: -29.8,
    },
    {
      joint_name: "right_shoulder",
      measured_angle: 88.0,
      reference_min: 80,
      reference_max: 100,
      optimal_angle: 90,
      is_correct: true,
      deviation: -2.0,
    },
  ],
  feedback: [
    {
      priority_order: 1,
      correction_title: "Extensión de codo insuficiente",
      correction_text: "Tu codo derecho alcanza 145°...",
      biomechanical_explanation: "La extensión completa del codo maximiza el alcance.",
      exercise_suggestion: "Practica shadow boxing con espejo.",
      impact_score: 0.85,
    },
  ],
  video_overlay_url: "/analysis/1/download/overlay",
  video_original_url: "/analysis/1/download/original",
  created_at: "2026-05-28T10:00:00",
  completed_at: "2026-05-28T10:01:30",
  error_message: null,
};

export const mockAnalysisListItem: AnalysisListItem = {
  id: 1,
  technique_display_name: "Jab",
  discipline_name: "Boxeo",
  global_score: 73,
  status: "completed",
  video_overlay_url: "/analysis/1/download/overlay",
  created_at: "2026-05-28T10:00:00",
};

export const mockAnalysisFailed: Analysis = {
  ...mockAnalysis,
  id: 2,
  status: "failed",
  global_score: null,
  xp_awarded: 0,
  error_message: "Video processing failed: no pose detected.",
};

export const mockAnalysisPending: Analysis = {
  ...mockAnalysis,
  id: 3,
  status: "pending",
  global_score: null,
  xp_awarded: 0,
  completed_at: null,
};
