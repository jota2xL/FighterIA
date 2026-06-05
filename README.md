# FighterIA

**AI-powered martial arts technique analysis platform.**

FighterIA analyzes martial arts technique videos using computer vision and AI, providing biomechanical feedback, technical scoring, performance certificates and commercial CRM tooling — all in a single platform.

---

**Stack:** Python 3.11 | FastAPI 0.111 | SQLAlchemy 2.0 | SQLite | MediaPipe 0.10 | React 18 | TypeScript 5 | Vite 5 | Tailwind CSS 3

---

## Table of Contents

1. [Features v1](#features-v1)
2. [Features v2 — New in this release](#features-v2--new-in-this-release)
3. [Project Architecture](#project-architecture)
4. [Installation & Setup](#installation--setup)
5. [API Reference — v2 Endpoints](#api-reference--v2-endpoints)
6. [Running Tests](#running-tests)
7. [Modules v2 in Detail](#modules-v2-in-detail)
   - [CRM Module](#crm-module)
   - [Blockchain Certificate Module](#blockchain-certificate-module)
   - [NLP Feedback Module](#nlp-feedback-module)
8. [License](#license)

---

## Features v1

The original platform (v1) provides:

- **Video analysis with MediaPipe Pose** — 33-point skeleton tracking, real-time joint angle computation.
- **Visual overlay** — frame-by-frame overlay highlighting correct (green) and incorrect (red) joint positions with numeric angle values.
- **Technical scoring** — global score and per-joint breakdown for each submitted technique.
- **Prioritized text feedback** — articulación-level corrections ranked by severity.
- **Discipline and technique catalog** — Muay Thai, Boxing, BJJ techniques with biomechanical reference ranges.
- **User authentication** — JWT-based register/login with refresh token support.
- **Personal analysis history** — paginated list of past sessions with score trends.
- **Progress dashboard** — XP earned, current belt rank, weekly activity heatmap.
- **Gamification system** — XP points, martial arts belt progression, achievement badges, daily streaks.
- **Instructor mode** — groups management, student assignment, inline comments on analyses.
- **Comparison mode** — side-by-side view of two analyses to track technique evolution.

---

## Features v2 — New in this release

### CRM — Commercial Management

- **Gym management** — register gyms as tenants with plan tiers (free / pro / enterprise), city and country.
- **Trainer assignment** — link FighterIA user accounts to gyms with roles (coach / head_coach / admin) and status tracking (active / inactive / pending).
- **Lead pipeline** — full sales funnel management for prospective gyms. Leads move through states: new → contacted → qualified → converted / lost. Sources tracked: organic, referral, paid_ad, event, direct.
- **Gym metrics dashboard** — aggregated per-gym view: active trainer count, total athletes, analysis sessions, average score, estimated monthly revenue and lead conversion rate.

### Blockchain — Certificate of Authenticity

- **SHA-256 certificate generation** — any completed analysis can be issued a tamper-evident certificate. The hash is computed from `analysis_id + user_id + global_score + completed_at timestamp`, making it deterministic and reproducible.
- **Idempotent issuance** — calling the generate endpoint twice returns the same certificate, never creating duplicates.
- **Public verification** — anyone with a certificate hash can verify it without authentication. The platform recomputes the hash from stored data and confirms whether it matches, incrementing a `verified_count` on valid checks.
- **Zero external dependencies** — implemented entirely with Python stdlib `hashlib`.

### NLP — Dynamic Textual Feedback

- **Holistic performance paragraph** — given the four biomechanical scores (potencia, equilibrio, alineacion, velocidad), the NLP service generates a personalized, multi-sentence feedback paragraph covering strengths, weaknesses and concrete drill recommendations.
- **Five performance levels** — deficiente (0-39), básico (40-59), intermedio (60-74), avanzado (75-89), sobresaliente (90-100). Each dimension has distinct descriptions and recommendations per level.
- **No external API** — pure template composition logic. Response time < 5ms. Stateless endpoint, no database access.
- **Priority-ordered recommendations** — weak dimensions are addressed first (up to 3 recommendations), followed by middle and strong dimensions.

---

## Project Architecture

```
FighterIA/
├── backend/                    # FastAPI + SQLAlchemy + SQLite
│   ├── app/
│   │   ├── main.py             # App entrypoint, router registration
│   │   ├── config.py           # Settings via pydantic-settings
│   │   ├── database.py         # SQLAlchemy engine + session factory
│   │   │
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── user.py         # User (auth, profile, XP, belt)
│   │   │   ├── analysis.py     # Analysis, JointResult, Feedback
│   │   │   ├── discipline.py   # Discipline, Technique
│   │   │   ├── biomechanical.py # BiomechanicalReference
│   │   │   ├── gamification.py # Badge, UserBadge, Streak
│   │   │   ├── instructor.py   # InstructorGroup, GroupMember, Comment
│   │   │   ├── crm.py          # [v2] Gym, Trainer, Lead
│   │   │   └── blockchain.py   # [v2] Certificate
│   │   │
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   │   ├── auth.py
│   │   │   ├── analysis.py
│   │   │   ├── dashboard.py
│   │   │   ├── gamification.py
│   │   │   ├── instructor.py
│   │   │   ├── crm.py          # [v2] GymCreate/Out, TrainerCreate/Out, LeadCreate/Out, GymMetricsResponse
│   │   │   └── blockchain.py   # [v2] CertificateOut, CertificateVerifyResponse
│   │   │
│   │   ├── routers/            # FastAPI route handlers
│   │   │   ├── auth.py         # /auth
│   │   │   ├── users.py        # /users
│   │   │   ├── disciplines.py  # /disciplines
│   │   │   ├── analysis.py     # /analysis
│   │   │   ├── dashboard.py    # /dashboard
│   │   │   ├── gamification.py # /gamification
│   │   │   ├── instructor.py   # /instructor
│   │   │   ├── crm.py          # [v2] /crm
│   │   │   ├── blockchain.py   # [v2] /blockchain
│   │   │   └── nlp.py          # [v2] /nlp
│   │   │
│   │   ├── services/           # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── mediapipe_service.py
│   │   │   ├── video_service.py
│   │   │   ├── scoring_service.py
│   │   │   ├── feedback_service.py
│   │   │   ├── analysis_service.py
│   │   │   ├── gamification_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── instructor_service.py
│   │   │   ├── crm_service.py        # [v2]
│   │   │   ├── blockchain_service.py # [v2]
│   │   │   └── nlp_service.py        # [v2]
│   │   │
│   │   └── utils/
│   │       ├── security.py     # JWT helpers
│   │       └── storage.py      # File storage helpers
│   │
│   └── tests/
│       ├── conftest.py
│       ├── fixtures/
│       ├── unit/               # Pure logic tests (no HTTP, no DB)
│       │   ├── test_scoring_service.py
│       │   ├── test_feedback_service.py
│       │   ├── test_gamification_service.py
│       │   ├── test_security.py
│       │   ├── test_mediapipe_service.py
│       │   ├── test_nlp_service.py        # [v2]
│       │   └── test_blockchain_service.py # [v2]
│       └── integration/        # Full HTTP round-trip tests
│           ├── test_auth.py
│           ├── test_disciplines.py
│           ├── test_dashboard.py
│           ├── test_analysis.py
│           ├── test_instructor.py
│           ├── test_crm.py        # [v2]
│           ├── test_blockchain.py # [v2]
│           └── test_nlp.py        # [v2]
│
└── frontend/                   # React 18 + TypeScript + Vite + Tailwind
    └── src/
        ├── App.tsx
        ├── main.tsx
        │
        ├── pages/
        │   ├── LandingPage.tsx
        │   ├── LoginPage.tsx
        │   ├── RegisterPage.tsx
        │   ├── DashboardPage.tsx
        │   ├── NewAnalysisPage.tsx
        │   ├── AnalysisResultPage.tsx
        │   ├── HistoryPage.tsx
        │   ├── ProfilePage.tsx
        │   ├── BadgesPage.tsx
        │   ├── InstructorPanelPage.tsx
        │   ├── InstructorGroupPage.tsx
        │   ├── InstructorStudentPage.tsx
        │   ├── GymManagementPage.tsx   # [v2]
        │   ├── LeadPipelinePage.tsx    # [v2]
        │   ├── BusinessDashboardPage.tsx # [v2]
        │   ├── CertificatePage.tsx     # [v2]
        │   └── NotFoundPage.tsx
        │
        ├── components/
        │   ├── ui/             # Button, Input, Card, Badge, Spinner, Modal...
        │   ├── analysis/       # TechniqueSelector, VideoUploader, ScoreDisplay...
        │   ├── dashboard/      # StatsCard, ActivityHeatmap, ProgressChart, BeltProgress
        │   ├── gamification/   # BadgeCard, StreakCounter, XPBar
        │   ├── instructor/     # GroupCard, StudentRow, CommentBox
        │   └── layout/         # Navbar
        │
        └── services/           # Axios API clients
            ├── api.client.ts
            ├── auth.service.ts
            ├── analysis.service.ts
            ├── dashboard.service.ts
            ├── gamification.service.ts
            ├── instructor.service.ts
            ├── crm.service.ts        # [v2]
            ├── blockchain.service.ts # [v2]
            └── nlp.service.ts        # [v2]
```

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/your-org/fighterai.git
cd fighterai
```

### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your values (see Variables de entorno below)

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.
Interactive documentation (Swagger UI): `http://localhost:8000/docs`.

### 3. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

### 4. Environment variables

Create `backend/.env` from the example below:

```env
# Security
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./fighterai.db

# File storage
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=100

# CORS
FRONTEND_URL=http://localhost:5173
```

> The SQLite database file (`fighterai.db`) is created automatically on first startup. All tables — including the four new v2 tables (`gyms`, `trainers`, `leads`, `certificates`) — are created via `Base.metadata.create_all()`. No manual migrations are needed.

---

## API Reference — v2 Endpoints

All v2 endpoints are additive. Existing v1 endpoints (~30) are unchanged.

### CRM Module — prefix `/crm`

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 1 | POST | `/crm/gyms` | JWT | Create a new gym |
| 2 | GET | `/crm/gyms` | JWT | List all gyms (paginated: `?page=1&limit=20`) |
| 3 | GET | `/crm/gyms/{gym_id}` | JWT | Get gym detail |
| 4 | PUT | `/crm/gyms/{gym_id}` | JWT | Update gym fields |
| 5 | DELETE | `/crm/gyms/{gym_id}` | JWT | Delete gym and all associated records |
| 6 | GET | `/crm/gyms/{gym_id}/metrics` | JWT | Get aggregated gym metrics |
| 7 | POST | `/crm/gyms/{gym_id}/trainers` | JWT | Assign trainer to gym |
| 8 | GET | `/crm/gyms/{gym_id}/trainers` | JWT | List trainers for a gym (paginated) |
| 9 | GET | `/crm/gyms/{gym_id}/trainers/{trainer_id}` | JWT | Get trainer detail |
| 10 | PUT | `/crm/gyms/{gym_id}/trainers/{trainer_id}` | JWT | Update trainer role or status |
| 11 | DELETE | `/crm/gyms/{gym_id}/trainers/{trainer_id}` | JWT | Remove trainer from gym |
| 12 | POST | `/crm/gyms/{gym_id}/leads` | JWT | Register a new sales lead |
| 13 | GET | `/crm/gyms/{gym_id}/leads` | JWT | List leads (`?status=&source=&page=&limit=`) |
| 14 | GET | `/crm/gyms/{gym_id}/leads/{lead_id}` | JWT | Get lead detail |
| 15 | PUT | `/crm/gyms/{gym_id}/leads/{lead_id}` | JWT | Update lead data or status |
| 16 | DELETE | `/crm/gyms/{gym_id}/leads/{lead_id}` | JWT | Delete lead record |

### Blockchain Module — prefix `/blockchain`

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 17 | POST | `/blockchain/certificates/generate/{analysis_id}` | JWT | Generate SHA-256 certificate for a completed analysis. 403 if not owner, 422 if not completed, idempotent (returns existing on repeat). |
| 18 | GET | `/blockchain/certificates/{hash_value}` | None (public) | Verify certificate by hash. Always HTTP 200. Returns `{"valid": bool, "certificate": ..., "message": ...}` |

### NLP Module — prefix `/nlp`

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 19 | POST | `/nlp/feedback` | None (public) | Generate personalized feedback paragraph from scores. Input: `{"potencia": float, "equilibrio": float, "alineacion": float, "velocidad": float}` (each 0-100). Output: `{"feedback": "string"}`. 422 if any score out of range. |

**Total v2 endpoints: 19** (16 CRM + 2 Blockchain + 1 NLP)

---

## Running Tests

### Backend (pytest)

```bash
cd backend

# Run the full test suite
pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run only unit tests (fast, no DB)
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run v2-specific tests only
pytest tests/unit/test_nlp_service.py tests/unit/test_blockchain_service.py tests/integration/test_crm.py tests/integration/test_blockchain.py tests/integration/test_nlp.py
```

### Frontend (Vitest)

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

---

## Modules v2 in Detail

### CRM Module

**Purpose:** Manage the full commercial lifecycle of the FighterIA platform — the gyms that subscribe (Gym), the trainers assigned to each gym (Trainer), and the prospects in the sales pipeline (Lead).

**Models:**

| Model | Table | Key Fields |
|-------|-------|------------|
| `Gym` | `gyms` | `name`, `city`, `country`, `plan` (free/pro/enterprise), `created_at` |
| `Trainer` | `trainers` | `gym_id` (FK), `user_id` (FK), `role` (coach/head_coach/admin), `status` (active/inactive/pending) |
| `Lead` | `leads` | `gym_id` (FK, nullable), `name`, `email`, `phone`, `status` (new/contacted/qualified/converted/lost), `source` (organic/referral/paid_ad/event/direct), `notes` |

**Gym metrics available via `GET /crm/gyms/{gym_id}/metrics`:**

```json
{
  "gym_id": 1,
  "gym_name": "Elite Muay Thai",
  "total_trainers": 3,
  "total_athletes": 24,
  "total_sessions": 187,
  "avg_score": 74.3,
  "estimated_revenue": 89.97,
  "leads_in_pipeline": 5,
  "leads_converted": 12
}
```

Revenue is calculated as `PLAN_PRICE[plan] × active_trainer_count` (free = 0, pro = 29.99, enterprise = 99.99 per active trainer per month).

---

### Blockchain Certificate Module

**Purpose:** Issue a tamper-evident, publicly verifiable certificate for each completed analysis. Suitable for sharing in athletic portfolios or digital CVs.

**How the SHA-256 hash is generated:**

```
payload  = "{analysis_id}:{user_id}:{global_score:.4f}:{completed_at.isoformat()}"
hash     = hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

Concrete example:

```
analysis_id  = 42
user_id      = 7
global_score = 83.25  →  "83.2500"
completed_at = "2026-06-05T14:32:00+00:00"

payload  = "42:7:83.2500:2026-06-05T14:32:00+00:00"
hash     = "a3f1e9..."  (64 hex characters)
```

**How to verify a certificate:**

```bash
# Generate (requires JWT token, analysis must be completed)
curl -X POST http://localhost:8000/blockchain/certificates/generate/42 \
     -H "Authorization: Bearer <your_jwt_token>"

# Response:
# { "id": 1, "analysis_id": 42, "hash": "a3f1e9...", "issued_at": "...", "verified_count": 0 }

# Verify publicly (no token needed)
curl http://localhost:8000/blockchain/certificates/a3f1e9...

# Response (valid):
# { "valid": true, "certificate": { ... }, "message": "Certificado válido." }

# Response (not found):
# { "valid": false, "certificate": null, "message": "Certificado no encontrado." }
```

**Key properties:**
- One certificate per analysis (UNIQUE constraint on `analysis_id`).
- Idempotent: generating twice returns the existing certificate.
- `verified_count` increments on every successful public verification.
- No external dependencies — pure stdlib `hashlib`.

---

### NLP Feedback Module

**Purpose:** Generate a personalized, multi-sentence performance paragraph from the four biomechanical scores. Complements the existing per-joint feedback with a holistic, athlete-facing summary.

**How it works:**

1. Each score (0-100) is classified into one of five levels: deficiente / básico / intermedio / avanzado / sobresaliente.
2. An opening sentence is selected based on the average score across all four dimensions.
3. Per-dimension descriptions are composed based on each dimension's level.
4. Strengths (avanzado+) and weaknesses (básico-) are summarized in separate sentences.
5. Up to three recommendations are selected, prioritizing weak dimensions first.
6. A motivational closing sentence is appended.

**Input / Output example:**

Request:
```json
POST /nlp/feedback
{
  "potencia":   85,
  "equilibrio": 42,
  "alineacion": 78,
  "velocidad":  91
}
```

Response:
```json
{
  "feedback": "Buena sesión con resultados sólidos en varias dimensiones. Tu potencia muestra un nivel avanzado, con una cadena cinética bien desarrollada. Tu equilibrio requiere atención — la inestabilidad de la base compromete la eficacia de tus técnicas. Tu alineación corporal ya se encuentra en un nivel sólido con muy pocas desviaciones. Tu velocidad de ejecución es sobresaliente — el timing y la explosividad son excelentes. En cuanto a fortalezas, potencia, alineación corporal y velocidad de ejecución muestran un rendimiento notable. Sin embargo, equilibrio requiere atención prioritaria. Incorpora de forma prioritaria trabajo de equilibrio estático (posición de árbol) y dinámico (kicks lentos). Mantén los ejercicios de postura y usa grabaciones periódicas para detectar pequeñas desviaciones. Añade drills de potencia explosiva (clean & press, saltos pliométricos) para superar el siguiente umbral. La constancia es la clave: mantén el ritmo de entrenamiento y los resultados llegarán."
}
```

**Performance characteristics:**
- Response time < 5ms (no network calls, no database access).
- Stateless — does not persist data.
- No authentication required.
- Scores outside [0, 100] return HTTP 422 Unprocessable Entity.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
