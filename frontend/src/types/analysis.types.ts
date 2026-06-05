export interface JointResult {
  joint_name: string;
  measured_angle: number;
  reference_min: number;
  reference_max: number;
  optimal_angle: number;
  is_correct: boolean;
  deviation: number;
}

export interface FeedbackItem {
  priority_order: number;
  correction_title: string;
  correction_text: string;
  biomechanical_explanation: string;
  exercise_suggestion: string;
  impact_score: number;
}

export interface Analysis {
  id: number;
  status: "pending" | "processing" | "completed" | "failed";
  technique: { id: number; display_name: string; discipline: string };
  global_score: number | null;
  power_score: number | null;
  balance_score: number | null;
  alignment_score: number | null;
  speed_score: number | null;
  xp_awarded: number;
  joint_results: JointResult[];
  feedback: FeedbackItem[];
  video_overlay_url: string;
  video_original_url: string;
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
}

export interface AnalysisListItem {
  id: number;
  technique_display_name: string;
  discipline_name: string;
  global_score: number | null;
  status: string;
  video_overlay_url: string;
  created_at: string;
}

export interface AnalysisList {
  items: AnalysisListItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface CompareResponse {
  analysis_1: Analysis;
  analysis_2: Analysis;
  score_diff: number;
  joint_comparison: {
    joint_name: string;
    angle_1: number;
    angle_2: number;
    diff: number;
    improved: boolean;
  }[];
}

export interface Discipline {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
}

export interface Technique {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
  difficulty: string;
  discipline_id: number;
}
