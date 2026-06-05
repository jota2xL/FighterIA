import { http, HttpResponse } from "msw";
import { mockUser, mockInstructor } from "./fixtures/users";
import { mockAnalysis, mockAnalysisListItem } from "./fixtures/analysis";

const BASE = "http://localhost:8000";

const mockDashboardStats = {
  total_analyses: 5,
  best_score: 85.0,
  average_score: 72.3,
  favorite_discipline: "Boxeo",
  xp: 820,
  belt_level: "amarillo",
  xp_for_next_belt: 1500,
  current_streak: 5,
  max_streak: 12,
  streak_shields: 1,
  recent_badges: [],
  recent_analyses: [],
};

const mockDisciplines = [
  { id: 1, name: "muay_thai", display_name: "Muay Thai", description: null },
  { id: 2, name: "bjj", display_name: "BJJ", description: null },
  { id: 3, name: "boxing", display_name: "Boxeo", description: null },
];

const mockTechniques = [
  { id: 1, discipline_id: 3, name: "jab", display_name: "Jab", difficulty: "easy", xp_multiplier: 1.0 },
  { id: 2, discipline_id: 3, name: "cross", display_name: "Cross", difficulty: "medium", xp_multiplier: 1.5 },
];

export const handlers = [
  // Auth
  http.get(`${BASE}/auth/me`, () => HttpResponse.json(mockUser)),

  http.post(`${BASE}/auth/login`, () =>
    HttpResponse.json({
      access_token: "fake-access-token",
      refresh_token: "fake-refresh-token",
      token_type: "bearer",
      user: mockUser,
    })
  ),

  http.post(`${BASE}/auth/register`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;
    return HttpResponse.json(
      {
        access_token: "fake-access-token",
        refresh_token: "fake-refresh-token",
        token_type: "bearer",
        user: { ...mockUser, email: body.email as string, username: body.username as string },
      },
      { status: 201 }
    );
  }),

  http.post(`${BASE}/auth/forgot-password`, () =>
    HttpResponse.json({ message: "Si el email existe, recibirás un enlace de recuperación." })
  ),

  // Disciplines
  http.get(`${BASE}/disciplines`, () => HttpResponse.json(mockDisciplines)),

  http.get(`${BASE}/disciplines/:id/techniques`, () =>
    HttpResponse.json(mockTechniques)
  ),

  // Analysis
  http.get(`${BASE}/analysis/me`, () =>
    HttpResponse.json({
      items: [mockAnalysisListItem],
      total: 1,
      page: 1,
      limit: 20,
      pages: 1,
    })
  ),

  http.get(`${BASE}/analysis/:id`, ({ params }) =>
    HttpResponse.json({ ...mockAnalysis, id: Number(params.id) })
  ),

  http.post(`${BASE}/analysis`, () =>
    HttpResponse.json(mockAnalysis, { status: 201 })
  ),

  // Dashboard
  http.get(`${BASE}/dashboard/me`, () => HttpResponse.json(mockDashboardStats)),

  http.get(`${BASE}/dashboard/me/progress`, () =>
    HttpResponse.json({
      data: [
        { date: "2026-05-01", score: 65.0, technique: "Jab", discipline: "Boxeo" },
        { date: "2026-05-08", score: 68.5, technique: "Cross", discipline: "Boxeo" },
        { date: "2026-05-15", score: 71.2, technique: "Jab", discipline: "Boxeo" },
        { date: "2026-05-22", score: 73.0, technique: "Uppercut", discipline: "Boxeo" },
      ],
      discipline_id: null,
      period_days: 30,
    })
  ),

  http.get(`${BASE}/dashboard/me/heatmap`, () =>
    HttpResponse.json({
      data: [
        { date: "2026-05-28", count: 2 },
        { date: "2026-05-27", count: 1 },
        { date: "2026-05-25", count: 3 },
      ],
      total_days_active: 15,
    })
  ),

  http.get(`${BASE}/dashboard/me/belt-progress`, () =>
    HttpResponse.json({
      current_belt: "amarillo",
      current_xp: 820,
      xp_for_next: 1501,
      xp_needed: 681,
      next_belt: "naranja",
      progress_percent: 47.3,
    })
  ),

  http.get(`${BASE}/dashboard/me/recent`, () =>
    HttpResponse.json([mockAnalysisListItem])
  ),

  // Gamification
  http.get(`${BASE}/gamification/badges`, () =>
    HttpResponse.json({
      earned: [],
      available: [],
      total_earned: 0,
      total_available: 12,
    })
  ),

  // Instructor
  http.get(`${BASE}/instructor/groups`, () => HttpResponse.json([])),

  http.post(`${BASE}/instructor/groups`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;
    return HttpResponse.json(
      {
        id: 1,
        name: body.name,
        description: body.description ?? null,
        invite_code: "TEST-CODE-001",
        instructor_id: 2,
        student_count: 0,
        created_at: "2026-05-28T12:00:00",
      },
      { status: 201 }
    );
  }),
];
