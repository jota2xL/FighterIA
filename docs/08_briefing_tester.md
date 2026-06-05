# Documento 8: Briefing para el Tester — QA FighterIA

> **Destinatario:** Agente Tester — QA Engineer Senior
> **Remitente:** Agente Product Owner Senior
> **Proyecto:** FighterIA | **Fecha:** 2026-05-28 | **Plazo:** 6 días

---

## 1. Contexto del Proyecto

FighterIA es una plataforma web de análisis de técnicas de artes marciales mediante visión por computadora. El sistema procesa vídeos con MediaPipe Pose, calcula ángulos articulares, los compara con referencias biomecánicas, genera un vídeo con overlay y devuelve puntuación + feedback priorizado. Incluye autenticación JWT, gamificación (XP, cinturones, badges, rachas) y modo instructor.

**Tu trabajo:** generar la suite completa de tests para el backend y frontend. Trabaja de forma autónoma sin preguntar nada al equipo.

---

## 2. Stack de Testing

| Herramienta | Uso |
|------------|-----|
| **Pytest** | Tests unitarios e integración del backend |
| **FastAPI TestClient** | Tests de endpoints HTTP |
| **Pytest-cov** | Cobertura de código |
| **Faker** | Datos de prueba realistas |
| **Vitest** | Tests unitarios del frontend |
| **React Testing Library** | Tests de componentes React |
| **MSW (Mock Service Worker)** | Mocking de API en tests frontend |
| **@testing-library/user-event** | Simulación de interacciones |

---

## 3. Configuración de Tests Backend

### `backend/tests/conftest.py`
```python
"""
Test configuration and shared fixtures for FighterIA backend test suite.
"""
import pytest
import pathlib
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.utils.security import hash_password, create_access_token
from seed.seed_data import run_seed

TEST_DB_URL = "sqlite:///./test_fighterai.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables and seed test database once per session."""
    Base.metadata.create_all(bind=engine)
    # Temporarily override DB URL for seed
    from app import database as db_module
    original_engine = db_module.engine
    original_session = db_module.SessionLocal
    db_module.engine = engine
    db_module.SessionLocal = TestingSessionLocal
    run_seed()
    db_module.engine = original_engine
    db_module.SessionLocal = original_session
    yield
    Base.metadata.drop_all(bind=engine)
    pathlib.Path("./test_fighterai.db").unlink(missing_ok=True)


@pytest.fixture(scope="function")
def db():
    """Provide a clean session per test, rolling back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    """Test client with overridden DB dependency."""
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a standard alumno test user."""
    user = User(
        email="testfighter@example.com",
        username="testfighter",
        password_hash=hash_password("TestPass123!"),
        full_name="Test Fighter",
        account_type="alumno"
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def test_instructor(db):
    """Create a test instructor user."""
    user = User(
        email="instructor@example.com",
        username="sensei_test",
        password_hash=hash_password("InstructorPass123!"),
        full_name="Test Instructor",
        account_type="instructor"
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def auth_headers(test_user):
    """Return Authorization headers for test_user."""
    token = create_access_token({"sub": str(test_user.id), "type": "access"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def instructor_headers(test_instructor):
    """Return Authorization headers for test_instructor."""
    token = create_access_token({"sub": str(test_instructor.id), "type": "access"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_video_bytes():
    """Generate a minimal valid MP4-like bytes for upload testing."""
    # In a real test suite, use a small real MP4 file. Here we use a stub.
    return b"FAKE_VIDEO_CONTENT_FOR_TESTING"
```

---

## 4. Tests de Autenticación

### `backend/tests/integration/test_auth.py`
```python
"""
Integration tests for /auth endpoints — register, login, refresh, forgot-password.
"""
import pytest


class TestRegister:

    def test_register_with_valid_data_returns_201(self, client):
        payload = {
            "email": "new.fighter@example.com",
            "username": "newfighter",
            "password": "SecurePass123!",
            "full_name": "New Fighter",
            "account_type": "alumno"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == payload["email"]
        assert "password" not in data["user"]
        assert "password_hash" not in data["user"]

    def test_register_with_duplicate_email_returns_409(self, client, test_user):
        payload = {
            "email": test_user.email,
            "username": "differentuser",
            "password": "AnotherPass123!",
            "full_name": "Duplicate Email",
            "account_type": "alumno"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 409

    def test_register_with_duplicate_username_returns_409(self, client, test_user):
        payload = {
            "email": "unique@example.com",
            "username": test_user.username,
            "password": "AnotherPass123!",
            "full_name": "Duplicate Username",
            "account_type": "alumno"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 409

    def test_register_with_short_password_returns_422(self, client):
        payload = {
            "email": "short@example.com",
            "username": "shortpass",
            "password": "abc",
            "full_name": "Short Password",
            "account_type": "alumno"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_invalid_email_returns_422(self, client):
        payload = {
            "email": "not-an-email",
            "username": "bademail",
            "password": "ValidPass123!",
            "full_name": "Bad Email",
            "account_type": "alumno"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_invalid_account_type_returns_422(self, client):
        payload = {
            "email": "valid@example.com",
            "username": "validuser",
            "password": "ValidPass123!",
            "full_name": "Valid User",
            "account_type": "superadmin"  # invalid
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422


class TestLogin:

    def test_login_with_correct_credentials_returns_200(self, client, test_user):
        response = client.post("/auth/login", json={
            "email": test_user.email,
            "password": "TestPass123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_wrong_password_returns_401(self, client, test_user):
        response = client.post("/auth/login", json={
            "email": test_user.email,
            "password": "WrongPassword!"
        })
        assert response.status_code == 401
        # Error message must not reveal which field is wrong
        assert "incorrectos" in response.json()["detail"].lower()

    def test_login_with_nonexistent_email_returns_401(self, client):
        response = client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "AnyPassword123!"
        })
        assert response.status_code == 401

    def test_forgot_password_always_returns_200(self, client):
        """Should return 200 regardless of whether email exists (prevents enumeration)."""
        for email in ["real@example.com", "fake@example.com", "test_user@example.com"]:
            response = client.post("/auth/forgot-password", json={"email": email})
            assert response.status_code == 200


class TestProtectedEndpoints:

    def test_get_me_with_valid_token_returns_200(self, client, auth_headers):
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert "email" in response.json()

    def test_get_me_without_token_returns_401(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_get_me_with_invalid_token_returns_401(self, client):
        response = client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert response.status_code == 401
```

---

## 5. Tests del Módulo de Disciplinas

### `backend/tests/integration/test_disciplines.py`
```python
"""
Integration tests for /disciplines endpoints.
"""


class TestDisciplines:

    def test_get_disciplines_returns_three_disciplines(self, client, auth_headers):
        response = client.get("/disciplines", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        names = {d["name"] for d in data}
        assert names == {"muay_thai", "bjj", "boxing"}

    def test_get_techniques_for_boxing_returns_four_techniques(self, client, auth_headers, db):
        from app.models.discipline import Discipline
        boxing = db.query(Discipline).filter(Discipline.name == "boxing").first()
        response = client.get(f"/disciplines/{boxing.id}/techniques", headers=auth_headers)
        assert response.status_code == 200
        techniques = response.json()
        assert len(techniques) == 4
        names = {t["name"] for t in techniques}
        assert "jab" in names
        assert "cross" in names

    def test_get_techniques_for_invalid_discipline_returns_404(self, client, auth_headers):
        response = client.get("/disciplines/99999/techniques", headers=auth_headers)
        assert response.status_code == 404

    def test_disciplines_require_authentication(self, client):
        response = client.get("/disciplines")
        assert response.status_code == 401
```

---

## 6. Tests del Servicio de Scoring

### `backend/tests/unit/test_scoring_service.py`
```python
"""
Unit tests for scoring_service — score calculation logic in isolation.
"""
from app.services.scoring_service import calculate_scores


class TestCalculateScores:

    def _make_joint_result(self, joint_name, measured, ref_min, ref_max, optimal, weight=1.0):
        is_correct = ref_min <= measured <= ref_max
        deviation = measured - optimal
        return {
            "joint_name": joint_name,
            "measured_angle": measured,
            "ref_min": ref_min,
            "ref_max": ref_max,
            "optimal_angle": optimal,
            "is_correct": is_correct,
            "deviation": deviation,
            "weight": weight
        }

    def test_all_correct_joints_produces_high_alignment_score(self):
        joints = [
            self._make_joint_result("right_elbow", 170, 165, 180, 175),
            self._make_joint_result("right_shoulder", 88, 80, 100, 90),
            self._make_joint_result("left_elbow", 92, 85, 100, 90),
        ]
        scores = calculate_scores(joints, speed_proxy=0.02, frame_count=60)
        assert scores["alignment_score"] == 100.0
        assert scores["global_score"] > 70.0

    def test_all_incorrect_joints_produces_low_global_score(self):
        joints = [
            self._make_joint_result("right_elbow", 90, 165, 180, 175),   # very wrong
            self._make_joint_result("right_shoulder", 150, 80, 100, 90), # very wrong
        ]
        scores = calculate_scores(joints, speed_proxy=0.0, frame_count=30)
        assert scores["global_score"] < 50.0

    def test_empty_joint_results_returns_zero_scores(self):
        scores = calculate_scores([], speed_proxy=0.0, frame_count=0)
        assert scores["global_score"] == 0.0
        assert scores["alignment_score"] == 0.0

    def test_scores_are_clamped_to_0_100(self):
        joints = [self._make_joint_result("right_elbow", 175, 165, 180, 175)]
        scores = calculate_scores(joints, speed_proxy=1.0, frame_count=60)
        for key, value in scores.items():
            assert 0.0 <= value <= 100.0, f"{key} = {value} is out of range"

    def test_partial_credit_for_joint_within_10_degrees_of_range(self):
        # Joint is 5° outside range — should receive partial credit (50%)
        joints = [self._make_joint_result("right_elbow", 160, 165, 180, 175)]
        scores = calculate_scores(joints, speed_proxy=0.0, frame_count=30)
        # Partial credit means alignment is not 0 but also not 100
        assert 0.0 < scores["alignment_score"] < 100.0
```

---

## 7. Tests del Servicio de Feedback

### `backend/tests/unit/test_feedback_service.py`
```python
"""
Unit tests for feedback_service — feedback generation from joint results.
"""
from app.services.feedback_service import generate_feedback


class TestGenerateFeedback:

    def _joint_result(self, joint_name, measured, ref_min, ref_max, optimal):
        is_correct = ref_min <= measured <= ref_max
        return {
            "joint_name": joint_name,
            "measured_angle": measured,
            "ref_min": ref_min,
            "ref_max": ref_max,
            "optimal_angle": optimal,
            "is_correct": is_correct,
            "deviation": measured - optimal,
            "weight": 1.0
        }

    def test_generates_no_feedback_when_all_joints_correct(self):
        joints = [
            self._joint_result("right_elbow", 172, 165, 180, 175),
            self._joint_result("right_shoulder", 88, 80, 100, 90),
        ]
        feedback = generate_feedback(joints)
        assert len(feedback) == 0

    def test_generates_feedback_for_each_incorrect_joint(self):
        joints = [
            self._joint_result("right_elbow", 140, 165, 180, 175),    # incorrect
            self._joint_result("right_shoulder", 88, 80, 100, 90),    # correct
            self._joint_result("hip_rotation_proxy", 5, 35, 55, 45),  # incorrect
        ]
        feedback = generate_feedback(joints)
        assert len(feedback) == 2

    def test_feedback_is_ordered_by_largest_deviation_first(self):
        joints = [
            self._joint_result("right_elbow", 100, 165, 180, 175),   # deviation = 75
            self._joint_result("hip_rotation_proxy", 30, 35, 55, 45),# deviation = 15
        ]
        feedback = generate_feedback(joints)
        assert feedback[0]["priority_order"] == 1
        assert feedback[0]["impact_score"] > feedback[1]["impact_score"]

    def test_feedback_items_contain_required_fields(self):
        joints = [self._joint_result("right_elbow", 100, 165, 180, 175)]
        feedback = generate_feedback(joints)
        assert len(feedback) == 1
        item = feedback[0]
        assert "correction_title" in item
        assert "correction_text" in item
        assert "biomechanical_explanation" in item
        assert "exercise_suggestion" in item
        assert "priority_order" in item
        assert "impact_score" in item
        assert 0.0 <= item["impact_score"] <= 1.0
```

---

## 8. Tests de Gamificación

### `backend/tests/unit/test_gamification_service.py`
```python
"""
Unit tests for gamification_service — XP, belt, streak and badge logic.
"""
import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock
from app.services.gamification_service import (
    calculate_xp_reward, get_belt_for_xp, award_xp_and_update_belt, update_streak
)


class TestCalculateXpReward:

    def test_score_0_to_49_with_multiplier_1_returns_10(self):
        assert calculate_xp_reward(0.0, 1.0) == 10
        assert calculate_xp_reward(49.0, 1.0) == 10

    def test_score_50_to_74_returns_20(self):
        assert calculate_xp_reward(50.0, 1.0) == 20
        assert calculate_xp_reward(74.9, 1.0) == 20

    def test_score_100_returns_60(self):
        assert calculate_xp_reward(100.0, 1.0) == 60

    def test_multiplier_2_doubles_xp(self):
        assert calculate_xp_reward(75.0, 2.0) == 60  # 30 * 2.0

    def test_multiplier_1_5_rounds_correctly(self):
        assert calculate_xp_reward(50.0, 1.5) == 30  # 20 * 1.5


class TestGetBeltForXp:

    def test_0_xp_returns_blanco(self):
        assert get_belt_for_xp(0) == "blanco"

    def test_500_xp_returns_blanco(self):
        assert get_belt_for_xp(500) == "blanco"

    def test_501_xp_returns_amarillo(self):
        assert get_belt_for_xp(501) == "amarillo"

    def test_12001_xp_returns_negro(self):
        assert get_belt_for_xp(12001) == "negro"

    def test_5001_xp_returns_azul(self):
        assert get_belt_for_xp(5001) == "azul"


class TestUpdateStreak:

    def _make_user(self, last_activity=None, current_streak=0, shield_active=False, shields=0):
        user = MagicMock()
        user.last_activity_date = last_activity
        user.current_streak = current_streak
        user.max_streak = current_streak
        user.streak_shield_active = shield_active
        user.streak_shields = shields
        return user

    def test_first_activity_sets_streak_to_1(self):
        user = self._make_user()
        db = MagicMock()
        update_streak(user, db)
        assert user.current_streak == 1

    def test_consecutive_day_increments_streak(self):
        yesterday = date.today() - timedelta(days=1)
        user = self._make_user(last_activity=yesterday, current_streak=5)
        update_streak(user, MagicMock())
        assert user.current_streak == 6

    def test_same_day_does_not_change_streak(self):
        user = self._make_user(last_activity=date.today(), current_streak=3)
        update_streak(user, MagicMock())
        assert user.current_streak == 3

    def test_missed_day_without_shield_resets_streak(self):
        two_days_ago = date.today() - timedelta(days=2)
        user = self._make_user(last_activity=two_days_ago, current_streak=10, shield_active=False)
        update_streak(user, MagicMock())
        assert user.current_streak == 1

    def test_missed_day_with_shield_preserves_streak(self):
        two_days_ago = date.today() - timedelta(days=2)
        user = self._make_user(last_activity=two_days_ago, current_streak=10, shield_active=True)
        update_streak(user, MagicMock())
        assert user.current_streak == 1  # shield consumed, but next consecutive adds 1
        assert user.streak_shield_active is False
```

---

## 9. Tests del Dashboard

### `backend/tests/integration/test_dashboard.py`
```python
"""
Integration tests for /dashboard/me endpoints.
"""
from app.models.analysis import Analysis
from app.models.discipline import Technique
from datetime import datetime


class TestDashboard:

    def test_dashboard_me_returns_200_with_empty_history(self, client, auth_headers):
        response = client.get("/dashboard/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_analyses" in data
        assert "xp" in data
        assert "belt_level" in data
        assert data["total_analyses"] == 0

    def test_dashboard_requires_authentication(self, client):
        assert client.get("/dashboard/me").status_code == 401

    def test_dashboard_me_stats_update_after_analysis(self, client, auth_headers, db, test_user):
        # Create a completed analysis directly in DB
        technique = db.query(Technique).first()
        analysis = Analysis(
            user_id=test_user.id,
            technique_id=technique.id,
            video_original_path="test/path.mp4",
            status="completed",
            global_score=75.0,
            power_score=80.0,
            balance_score=70.0,
            alignment_score=75.0,
            speed_score=65.0,
            xp_awarded=30
        )
        db.add(analysis)
        db.flush()

        response = client.get("/dashboard/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_analyses"] == 1
        assert data["best_score"] == 75.0
```

---

## 10. Tests del Frontend

### `frontend/src/mocks/handlers.ts`
```typescript
import { http, HttpResponse } from "msw";

const mockUser = {
  id: 1, email: "fighter@example.com", username: "fighter_test",
  full_name: "Test Fighter", account_type: "alumno",
  xp: 820, belt_level: "amarillo", current_streak: 5, max_streak: 12,
  streak_shields: 1, bio: null, gym: "Test Gym", city: "Madrid",
  country: "España", experience_years: 3, disciplines: ["boxing"],
  avatar_url: null, created_at: "2026-05-01T10:00:00"
};

const mockAnalysis = {
  id: 1, status: "completed",
  technique: { id: 1, display_name: "Jab", discipline: "Boxeo" },
  global_score: 73.5, power_score: 80.0, balance_score: 65.0,
  alignment_score: 78.0, speed_score: 70.0, xp_awarded: 30,
  joint_results: [
    { joint_name: "right_elbow", measured_angle: 145.2, reference_min: 165, reference_max: 180, optimal_angle: 175, is_correct: false, deviation: -29.8 }
  ],
  feedback: [
    { priority_order: 1, correction_title: "Extensión de codo insuficiente", correction_text: "Tu codo derecho alcanza 145°...", biomechanical_explanation: "La extensión completa...", exercise_suggestion: "Practica shadow boxing...", impact_score: 0.85 }
  ],
  video_overlay_url: "/analysis/1/download/overlay",
  video_original_url: "/analysis/1/download/original",
  created_at: "2026-05-28T10:00:00", completed_at: "2026-05-28T10:01:30",
  error_message: null
};

export const handlers = [
  http.get("http://localhost:8000/auth/me", () => HttpResponse.json(mockUser)),
  http.post("http://localhost:8000/auth/login", () =>
    HttpResponse.json({ access_token: "fake-token", refresh_token: "fake-refresh", token_type: "bearer", user: mockUser })
  ),
  http.post("http://localhost:8000/auth/register", async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;
    return HttpResponse.json({ access_token: "fake-token", refresh_token: "fake-refresh", token_type: "bearer", user: { ...mockUser, email: body.email as string } }, { status: 201 });
  }),
  http.get("http://localhost:8000/disciplines", () => HttpResponse.json([
    { id: 1, name: "muay_thai", display_name: "Muay Thai", icon_name: "muay-thai" },
    { id: 2, name: "bjj", display_name: "BJJ", icon_name: "bjj" },
    { id: 3, name: "boxing", display_name: "Boxeo", icon_name: "boxing" },
  ])),
  http.get("http://localhost:8000/disciplines/:id/techniques", ({ params }) => {
    const techniques = [
      { id: 1, discipline_id: Number(params.id), name: "jab", display_name: "Jab", difficulty: "easy", xp_multiplier: 1.0 },
      { id: 2, discipline_id: Number(params.id), name: "cross", display_name: "Cross", difficulty: "medium", xp_multiplier: 1.5 },
    ];
    return HttpResponse.json(techniques);
  }),
  http.get("http://localhost:8000/analysis/me", () => HttpResponse.json({
    items: [mockAnalysis], total: 1, page: 1, limit: 20, pages: 1
  })),
  http.get("http://localhost:8000/analysis/:id", ({ params }) =>
    HttpResponse.json({ ...mockAnalysis, id: Number(params.id) })
  ),
  http.get("http://localhost:8000/dashboard/me", () => HttpResponse.json({
    total_analyses: 5, best_score: 85.0, average_score: 72.3,
    favorite_discipline: "Boxeo", xp: 820, belt_level: "amarillo",
    xp_for_next_belt: 1500, current_streak: 5, max_streak: 12,
    streak_shields: 1, recent_badges: [], recent_analyses: []
  })),
  http.get("http://localhost:8000/dashboard/me/progress", () => HttpResponse.json({
    labels: ["2026-05-01", "2026-05-08", "2026-05-15", "2026-05-22"],
    datasets: [{ discipline: "Boxeo", data: [65.0, 68.5, 71.2, 73.5] }]
  })),
  http.get("http://localhost:8000/dashboard/me/heatmap", () => HttpResponse.json({
    data: [{ date: "2026-05-28", count: 2 }, { date: "2026-05-27", count: 1 }]
  })),
];
```

### `frontend/src/tests/components/LoginForm.test.tsx`
```tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import LoginPage from "@/pages/LoginPage";

const renderWithProviders = (ui: React.ReactElement) => {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}><MemoryRouter>{ui}</MemoryRouter></QueryClientProvider>
  );
};

describe("LoginPage", () => {

  it("renders email and password inputs", () => {
    renderWithProviders(<LoginPage />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
  });

  it("shows validation error when email is empty on submit", async () => {
    renderWithProviders(<LoginPage />);
    fireEvent.click(screen.getByRole("button", { name: /iniciar sesión/i }));
    await waitFor(() => {
      expect(screen.getByText(/email requerido|introduce tu email/i)).toBeInTheDocument();
    });
  });

  it("shows validation error for invalid email format", async () => {
    renderWithProviders(<LoginPage />);
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "not-email" } });
    fireEvent.click(screen.getByRole("button", { name: /iniciar sesión/i }));
    await waitFor(() => {
      expect(screen.getByText(/email válido|formato de email/i)).toBeInTheDocument();
    });
  });

  it("calls login API with correct data on valid submit", async () => {
    renderWithProviders(<LoginPage />);
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "fighter@example.com" } });
    fireEvent.change(screen.getByLabelText(/contraseña/i), { target: { value: "ValidPass123!" } });
    fireEvent.click(screen.getByRole("button", { name: /iniciar sesión/i }));
    await waitFor(() => {
      expect(screen.queryByText(/email o contraseña incorrectos/i)).not.toBeInTheDocument();
    });
  });
});
```

### `frontend/src/tests/components/ScoreDisplay.test.tsx`
```tsx
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import ScoreDisplay from "@/components/analysis/ScoreDisplay";

describe("ScoreDisplay", () => {

  const defaultProps = {
    globalScore: 73.5,
    powerScore: 80.0,
    balanceScore: 65.0,
    alignmentScore: 78.0,
    speedScore: 70.0,
  };

  it("renders global score value", () => {
    render(<ScoreDisplay {...defaultProps} />);
    expect(screen.getByText("73.5")).toBeInTheDocument();
  });

  it("renders all four sub-score labels", () => {
    render(<ScoreDisplay {...defaultProps} />);
    expect(screen.getByText(/potencia/i)).toBeInTheDocument();
    expect(screen.getByText(/equilibrio/i)).toBeInTheDocument();
    expect(screen.getByText(/alineaci/i)).toBeInTheDocument();
    expect(screen.getByText(/velocidad/i)).toBeInTheDocument();
  });

  it("shows correct color class for score above 80", () => {
    render(<ScoreDisplay {...defaultProps} globalScore={85} />);
    const scoreEl = screen.getByText("85");
    expect(scoreEl.className).toMatch(/excellent|green/i);
  });

  it("shows correct color class for score below 60", () => {
    render(<ScoreDisplay {...defaultProps} globalScore={45} />);
    const scoreEl = screen.getByText("45");
    expect(scoreEl.className).toMatch(/poor|red/i);
  });
});
```

---

## 11. Tabla de Casos de Prueba

| ID | Módulo | Tipo | Descripción | Datos de entrada | Resultado esperado | Prioridad |
|----|--------|------|-------------|----------------|--------------------|-----------|
| TC-001 | Auth | Integración | Registro con datos válidos | email, username, pass, nombre, tipo | 201 + tokens + user sin password | Crítica |
| TC-002 | Auth | Integración | Registro con email duplicado | email ya registrado | 409 Conflict | Crítica |
| TC-003 | Auth | Integración | Login correcto | credenciales válidas | 200 + access_token | Crítica |
| TC-004 | Auth | Integración | Login con contraseña incorrecta | contraseña errónea | 401, mensaje genérico | Crítica |
| TC-005 | Auth | Integración | Endpoint protegido sin token | sin cabecera Authorization | 401 | Crítica |
| TC-006 | Auth | Integración | Forgot password siempre 200 | email válido o inválido | 200 siempre | Alta |
| TC-007 | Disciplinas | Integración | GET /disciplines retorna 3 | — | 200 + array de 3 | Alta |
| TC-008 | Disciplinas | Integración | Técnicas de boxing retorna 4 | discipline_id válido | 200 + array de 4 | Alta |
| TC-009 | Scoring | Unitario | Todos correctos → alineación 100 | todos los joints en rango | alignment_score=100 | Crítica |
| TC-010 | Scoring | Unitario | Sin joints → scores en 0 | lista vacía | todos los scores = 0 | Alta |
| TC-011 | Scoring | Unitario | Scores acotados 0-100 | cualquier input | 0 ≤ score ≤ 100 | Alta |
| TC-012 | Feedback | Unitario | Sin errores → lista vacía | todos correctos | [] | Alta |
| TC-013 | Feedback | Unitario | Ordenado por mayor desviación | 2 joints incorrectos | mayor desviación = prioridad 1 | Crítica |
| TC-014 | Gamificación | Unitario | Score 0-49 → 10 XP | score=25, mult=1.0 | 10 | Alta |
| TC-015 | Gamificación | Unitario | Score 100 con mult 2 → 120 XP | score=100, mult=2.0 | 120 | Alta |
| TC-016 | Gamificación | Unitario | 501 XP → cinturón amarillo | xp=501 | "amarillo" | Alta |
| TC-017 | Gamificación | Unitario | Racha incrementa en día consecutivo | last_activity=ayer | current_streak+1 | Crítica |
| TC-018 | Gamificación | Unitario | Racha se resetea si falta un día | last_activity=anteayer, sin escudo | current_streak=1 | Crítica |
| TC-019 | Dashboard | Integración | Dashboard vacío retorna 200 | usuario sin análisis | 200, total_analyses=0 | Alta |
| TC-020 | LoginPage | Componente | Renderiza campos de formulario | — | inputs de email y contraseña visibles | Alta |
| TC-021 | LoginPage | Componente | Validación de email vacío | submit sin email | mensaje de error visible | Alta |
| TC-022 | ScoreDisplay | Componente | Muestra puntuación global | score=73.5 | "73.5" visible en DOM | Alta |
| TC-023 | ScoreDisplay | Componente | Muestra color verde para ≥80 | score=85 | clase CSS de color correcto | Media |

---

## 12. Criterios de Calidad de los Tests

- [ ] Todos los tests siguen el patrón Arrange / Act / Assert con separación visual
- [ ] Los nombres describen el comportamiento esperado, no la implementación
- [ ] Cada test es independiente (rollback de base de datos por fixture de función)
- [ ] Los datos de prueba son realistas (emails válidos, contraseñas con requisitos reales)
- [ ] Los tests de endpoints verifican código HTTP Y estructura del body
- [ ] Los handlers MSW cubren todos los endpoints consumidos por las páginas testeadas
- [ ] `pytest tests/ -v` pasa sin errores de configuración
- [ ] `npm run test` pasa sin errores de configuración
- [ ] No hay `print()` ni `console.log()` en los archivos de test

✅ DOCUMENTO COMPLETADO
