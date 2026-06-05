export interface InstructorGroup {
  id: number;
  name: string;
  description: string | null;
  invite_code: string;
  instructor_id: number;
  student_count: number;
  created_at: string;
}

export interface GroupCreate {
  name: string;
  description?: string;
}

export interface GroupStudent {
  id: number;
  username: string;
  full_name: string;
  avatar_url: string | null;
  belt_level: string;
  xp: number;
  current_streak: number;
  total_analyses: number;
  last_analysis_at: string | null;
  average_score: number | null;
}

export interface InstructorComment {
  id: number;
  content: string;
  instructor_id: number;
  student_id: number;
  analysis_id: number | null;
  created_at: string;
}

export interface CommentCreate {
  content: string;
  student_id: number;
  analysis_id?: number;
}

export interface StudentDetail {
  user: GroupStudent;
  recent_analyses: {
    id: number;
    technique_display_name: string;
    global_score: number | null;
    created_at: string;
  }[];
  comments: InstructorComment[];
  progress_summary: {
    best_score: number | null;
    average_score: number | null;
    total_analyses: number;
    analyses_last_30_days: number;
  };
}
