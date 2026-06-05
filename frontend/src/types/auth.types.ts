export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  account_type: "alumno" | "instructor";
  bio: string | null;
  gym: string | null;
  city: string | null;
  country: string | null;
  experience_years: number;
  disciplines: string[];
  avatar_url: string | null;
  xp: number;
  belt_level: BeltLevel;
  current_streak: number;
  max_streak: number;
  streak_shields: number;
  created_at: string;
}

export type BeltLevel =
  | "blanco"
  | "amarillo"
  | "naranja"
  | "verde"
  | "azul"
  | "marron"
  | "negro";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name: string;
  account_type: "alumno" | "instructor";
}
