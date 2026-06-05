import type { User } from "@/types/auth.types";

export const mockUser: User = {
  id: 1,
  email: "fighter@example.com",
  username: "fighter_test",
  full_name: "Test Fighter",
  account_type: "alumno",
  bio: null,
  gym: "Test Gym",
  city: "Madrid",
  country: "España",
  experience_years: 3,
  disciplines: ["boxing"],
  avatar_url: null,
  xp: 820,
  belt_level: "amarillo",
  current_streak: 5,
  max_streak: 12,
  streak_shields: 1,
  created_at: "2026-05-01T10:00:00",
};

export const mockInstructor: User = {
  ...mockUser,
  id: 2,
  email: "sensei@example.com",
  username: "sensei_test",
  full_name: "Test Sensei",
  account_type: "instructor",
};
