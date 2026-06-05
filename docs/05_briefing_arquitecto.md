# Documento 5: Briefing para el Arquitecto — FighterIA

> **Destinatario:** Agente Arquitecto de Software Senior
> **Remitente:** Agente Product Owner Senior
> **Proyecto:** FighterIA | **Fecha:** 2026-05-28 | **Plazo:** 6 días

---

## 1. Contexto del Proyecto

FighterIA es una plataforma web de entrenamiento de artes marciales que utiliza visión por computadora (MediaPipe Pose) para analizar la técnica de los usuarios a través de vídeos. El sistema detecta 33 puntos del cuerpo, calcula ángulos articulares, los compara con referencias biomecánicas correctas, genera un vídeo con overlay visual (articulaciones en verde/rojo con valores numéricos), devuelve puntuación 0-100 y feedback priorizado de correcciones.

**El objetivo académico** es demostrar el uso de una oficina de agentes IA (PO, Arquitecto, Dev1, Dev2, Tester) trabajando coordinadamente para construir una aplicación real. El proyecto es el Assignment Brief de la unidad 47 Emerging Technologies del PEARSON HND en Computer Science / Data Science & AI.

---

## 2. Stack Tecnológico Fijo

| Capa | Tecnología | Versión recomendada |
|------|-----------|-------------------|
| Backend framework | Python + FastAPI | Python 3.11, FastAPI 0.111+ |
| Visión por computadora | MediaPipe + OpenCV | mediapipe 0.10.14, opencv-python-headless 4.9.0 |
| Base de datos | SQLite + SQLAlchemy | SQLAlchemy 2.0+ |
| Validación | Pydantic v2 | 2.7+ |
| Autenticación | JWT | python-jose + passlib[bcrypt] |
| Frontend framework | React + TypeScript | React 18, TS 5 |
| Bundler | Vite | 5.x |
| Estilos | Tailwind CSS | 3.x |
| OS destino | Windows | localhost únicamente |
| Puertos | Backend: 8000, Frontend: 3000 | No modificar |

---

## 3. Estructura de Carpetas del Proyecto

```
fighterai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app, CORS, routers, startup
│   │   ├── config.py                # Settings con pydantic-settings
│   │   ├── database.py              # Engine SQLite, SessionLocal, Base, get_db
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # User model
│   │   │   ├── discipline.py        # Discipline + Technique models
│   │   │   ├── biomechanical.py     # BiomechanicalReference model
│   │   │   ├── analysis.py          # Analysis + AnalysisJointResult + AnalysisFeedback models
│   │   │   ├── gamification.py      # Badge + UserBadge models
│   │   │   └── instructor.py        # InstructorGroup + GroupMember + AnalysisComment models
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # RegisterRequest, LoginRequest, TokenResponse
│   │   │   ├── user.py              # UserResponse, UserProfileResponse, UserUpdate
│   │   │   ├── discipline.py        # DisciplineResponse, TechniqueResponse
│   │   │   ├── analysis.py          # AnalysisCreateRequest, AnalysisResponse, AnalysisDetailResponse
│   │   │   ├── dashboard.py         # DashboardResponse, ProgressResponse, HeatmapResponse
│   │   │   ├── gamification.py      # BadgeResponse, UserBadgeResponse, RankingResponse
│   │   │   └── instructor.py        # GroupResponse, GroupMemberResponse, CommentResponse
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # /auth/*
│   │   │   ├── users.py             # /users/*
│   │   │   ├── disciplines.py       # /disciplines/*
│   │   │   ├── analysis.py          # /analysis/*
│   │   │   ├── dashboard.py         # /dashboard/*
│   │   │   ├── gamification.py      # /gamification/*
│   │   │   └── instructor.py        # /instructor/*
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py      # hash_password, verify_password, create_token, decode_token
│   │   │   ├── user_service.py      # CRUD de usuarios, get_current_user dependency
│   │   │   ├── video_service.py     # save_video, validate_video, get_video_duration
│   │   │   ├── mediapipe_service.py # PoseAnalyzer class (MediaPipe + OpenCV)
│   │   │   ├── analysis_service.py  # orchestrate full analysis pipeline
│   │   │   ├── scoring_service.py   # calculate_scores (power, balance, alignment, speed, global)
│   │   │   ├── feedback_service.py  # generate_feedback from joint results
│   │   │   ├── gamification_service.py # award_xp, update_belt, check_badges, update_streak
│   │   │   └── instructor_service.py   # group management, student views
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── security.py          # JWT helpers (create_access_token, create_refresh_token)
│   │       └── storage.py           # get_video_path, ensure_storage_dirs (using pathlib)
│   ├── seed/
│   │   ├── __init__.py
│   │   └── seed_data.py             # Populates disciplines, techniques, biomechanical refs
│   ├── storage/
│   │   └── videos/                  # Runtime: user_{id}/original/ and user_{id}/overlay/
│   ├── storage/
│   │   └── avatars/                 # Profile pictures
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── unit/
│   │   └── integration/
│   ├── .env.example
│   ├── .env
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                  # Button, Input, Modal, Badge, Spinner, etc.
│   │   │   ├── auth/                # LoginForm, RegisterForm
│   │   │   ├── analysis/            # VideoUploader, AnalysisResult, JointScoreCard, FeedbackList
│   │   │   ├── dashboard/           # ProgressChart, HeatmapCalendar, StatsCard
│   │   │   ├── gamification/        # BeltProgress, BadgeCard, StreakCounter
│   │   │   └── instructor/          # GroupCard, StudentRow, CommentBox
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── NewAnalysisPage.tsx
│   │   │   ├── AnalysisResultPage.tsx
│   │   │   ├── HistoryPage.tsx
│   │   │   ├── ProfilePage.tsx
│   │   │   ├── BadgesPage.tsx
│   │   │   ├── InstructorPanel.tsx
│   │   │   ├── InstructorGroupPage.tsx
│   │   │   ├── InstructorStudentPage.tsx
│   │   │   └── NotFoundPage.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useAnalysis.ts
│   │   │   └── useGamification.ts
│   │   ├── layouts/
│   │   │   ├── MainLayout.tsx       # Navbar + Outlet
│   │   │   └── AuthLayout.tsx       # Centered card for login/register
│   │   ├── services/
│   │   │   ├── api.client.ts        # Axios instance with interceptors
│   │   │   ├── auth.service.ts
│   │   │   ├── analysis.service.ts
│   │   │   ├── dashboard.service.ts
│   │   │   ├── gamification.service.ts
│   │   │   └── instructor.service.ts
│   │   ├── store/
│   │   │   └── auth.store.ts        # Zustand store for auth state
│   │   ├── types/
│   │   │   ├── auth.types.ts
│   │   │   ├── analysis.types.ts
│   │   │   ├── dashboard.types.ts
│   │   │   ├── gamification.types.ts
│   │   │   └── instructor.types.ts
│   │   ├── utils/
│   │   │   ├── cn.ts                # clsx + tailwind-merge helper
│   │   │   └── format.ts            # date formatters, score formatters
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css                # Tailwind directives + custom CSS vars
│   ├── public/
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── vite.config.ts
│   └── tsconfig.json
├── docs/                            # PO documentation (this directory)
└── README.md
```

---

## 4. Modelos de Base de Datos

### 4.1 User

**Tabla:** `users`

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Email de login |
| username | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Nombre de usuario público |
| password_hash | VARCHAR(255) | NOT NULL | Hash bcrypt |
| full_name | VARCHAR(100) | NOT NULL | Nombre completo |
| account_type | VARCHAR(20) | NOT NULL, DEFAULT 'alumno' | 'alumno' o 'instructor' |
| bio | TEXT | NULLABLE | Biografía |
| gym | VARCHAR(100) | NULLABLE | Gimnasio |
| city | VARCHAR(100) | NULLABLE | Ciudad |
| country | VARCHAR(100) | NULLABLE | País |
| experience_years | INTEGER | DEFAULT 0 | Años de experiencia |
| disciplines | VARCHAR(255) | NULLABLE | JSON array como string: '["muay_thai","bjj"]' |
| avatar_url | VARCHAR(500) | NULLABLE | Ruta relativa a la imagen |
| xp | INTEGER | DEFAULT 0, NOT NULL | XP acumulado |
| belt_level | VARCHAR(20) | DEFAULT 'blanco', NOT NULL | Cinturón actual |
| current_streak | INTEGER | DEFAULT 0 | Racha actual en días |
| max_streak | INTEGER | DEFAULT 0 | Racha máxima histórica |
| last_activity_date | DATE | NULLABLE | Último día con análisis |
| streak_shield_active | BOOLEAN | DEFAULT FALSE | Escudo de racha activo |
| streak_shields | INTEGER | DEFAULT 0 | Número de escudos disponibles |
| is_active | BOOLEAN | DEFAULT TRUE | Cuenta activa |
| created_at | DATETIME | DEFAULT NOW | Fecha de registro |
| updated_at | DATETIME | ON UPDATE NOW | Última actualización |

---

### 4.2 Discipline

**Tabla:** `disciplines`

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| name | VARCHAR(50) | UNIQUE, NOT NULL | 'muay_thai', 'bjj', 'boxing' |
| display_name | VARCHAR(100) | NOT NULL | 'Muay Thai', 'BJJ', 'Boxeo' |
| description | TEXT | NULLABLE | Descripción de la disciplina |
| icon_name | VARCHAR(50) | NULLABLE | Nombre del icono (para frontend) |

---

### 4.3 Technique

**Tabla:** `techniques`

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| discipline_id | INTEGER | FK → disciplines.id, NOT NULL | Disciplina a la que pertenece |
| name | VARCHAR(100) | NOT NULL | 'jab', 'roundkick_medio', 'armbar' |
| display_name | VARCHAR(100) | NOT NULL | 'Jab', 'Roundkick Medio', 'Armbar' |
| description | TEXT | NULLABLE | Descripción y puntos clave |
| difficulty | VARCHAR(20) | DEFAULT 'medium' | 'easy', 'medium', 'hard' |
| xp_multiplier | FLOAT | DEFAULT 1.0 | Multiplicador XP: easy=1.0, medium=1.5, hard=2.0 |

**Índices:** `idx_techniques_discipline_id` sobre `discipline_id`

---

### 4.4 BiomechanicalReference

**Tabla:** `biomechanical_references`

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| technique_id | INTEGER | FK → techniques.id, NOT NULL | Técnica a la que aplica |
| joint_name | VARCHAR(50) | NOT NULL | 'left_elbow', 'right_shoulder', 'left_knee', etc. |
| phase | VARCHAR(30) | DEFAULT 'execution' | 'execution' o 'final_position' |
| min_angle | FLOAT | NOT NULL | Ángulo mínimo correcto (grados) |
| max_angle | FLOAT | NOT NULL | Ángulo máximo correcto (grados) |
| optimal_angle | FLOAT | NOT NULL | Ángulo ideal de referencia |
| weight | FLOAT | DEFAULT 1.0 | Peso en el cálculo de puntuación |
| description | TEXT | NULLABLE | Explicación biomecánica de la referencia |

**Índices:** `idx_bio_refs_technique_id` sobre `technique_id`

---

### 4.5 Analysis

**Tabla:** `analyses`

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| user_id | INTEGER | FK → users.id, NOT NULL, INDEX | Usuario propietario |
| technique_id | INTEGER | FK → techniques.id, NOT NULL | Técnica analizada |
| video_original_path | VARCHAR(500) | NOT NULL | Ruta al vídeo original |
| video_overlay_path | VARCHAR(500) | NULLABLE | Ruta al vídeo con overlay |
| status | VARCHAR(20) | DEFAULT 'pending' | 'pending', 'processing', 'completed', 'failed' |
| global_score | FLOAT | NULLABLE | Puntuación global 0-100 |
| power_score | FLOAT | NULLABLE | Sub-puntuación potencia |
| balance_score | FLOAT | NULLABLE | Sub-puntuación equilibrio |
| alignment_score | FLOAT | NULLABLE | Sub-puntuación alineación |
| speed_score | FLOAT | NULLABLE | Sub-puntuación velocidad |
| xp_awarded | INTEGER | DEFAULT 0 | XP otorgado por este análisis |
| is_public | BOOLEAN | DEFAULT FALSE | ¿Accesible por link público? |
| error_message | TEXT | NULLABLE | Mensaje si status='failed' |
| created_at | DATETIME | DEFAULT NOW | Fecha de subida |
| completed_at | DATETIME | NULLABLE | Fecha de finalización del análisis |

**Índices:** `idx_analyses_user_id`, `idx_analyses_status`

---

### 4.6 AnalysisJointResult

**Tabla:** `analysis_joint_results`

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| analysis_id | INTEGER | FK → analyses.id, NOT NULL | Análisis al que pertenece |
| joint_name | VARCHAR(50) | NOT NULL | Articulación medida |
| measured_angle | FLOAT | NOT NULL | Ángulo real medido en el frame clave |
| reference_min | FLOAT | NOT NULL | Referencia mínima correcta |
| reference_max | FLOAT | NOT NULL | Referencia máxima correcta |
| optimal_angle | FLOAT | NOT NULL | Ángulo óptimo |
| is_correct | BOOLEAN | NOT NULL | ¿Está dentro del rango? |
| deviation | FLOAT | NOT NULL | Desviación del óptimo (puede ser negativa) |

**Índices:** `idx_joint_results_analysis_id`

---

### 4.7 AnalysisFeedback

**Tabla:** `analysis_feedback`

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| analysis_id | INTEGER | FK → analyses.id, NOT NULL | Análisis al que pertenece |
| correction_title | VARCHAR(200) | NOT NULL | Título corto del error |
| correction_text | TEXT | NOT NULL | Descripción completa de la corrección |
| biomechanical_explanation | TEXT | NULLABLE | Por qué importa biomecánicamente |
| exercise_suggestion | TEXT | NULLABLE | Ejercicio para corregirlo |
| priority_order | INTEGER | NOT NULL | 1 = más impacto, n = menor impacto |
| impact_score | FLOAT | NOT NULL | 0.0 - 1.0, peso del error en la puntuación |

**Índices:** `idx_feedback_analysis_id`

---

### 4.8 Badge

**Tabla:** `badges`

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Identificador interno |
| display_name | VARCHAR(100) | NOT NULL | Nombre visible |
| description | TEXT | NOT NULL | Cómo se consigue |
| level | VARCHAR(20) | NOT NULL | 'bronze', 'silver', 'gold' |
| icon_name | VARCHAR(50) | NOT NULL | Nombre del icono para frontend |
| condition_type | VARCHAR(50) | NOT NULL | 'first_analysis', 'streak_7', 'score_100', etc. |
| condition_value | INTEGER | DEFAULT 1 | Valor numérico de la condición |
| xp_reward | INTEGER | DEFAULT 50 | XP otorgado al desbloquear |

---

### 4.9 UserBadge

**Tabla:** `user_badges`

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| user_id | INTEGER | FK → users.id, NOT NULL | Usuario |
| badge_id | INTEGER | FK → badges.id, NOT NULL | Badge desbloqueado |
| earned_at | DATETIME | DEFAULT NOW | Fecha de desbloqueo |

**Constraint:** UNIQUE(user_id, badge_id)

---

### 4.10 InstructorGroup

**Tabla:** `instructor_groups`

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| instructor_id | INTEGER | FK → users.id, NOT NULL | Instructor dueño del grupo |
| name | VARCHAR(100) | NOT NULL | Nombre del grupo |
| description | TEXT | NULLABLE | Descripción del grupo |
| invite_code | VARCHAR(20) | UNIQUE, NOT NULL | Código de invitación |
| is_active | BOOLEAN | DEFAULT TRUE | Grupo activo |
| created_at | DATETIME | DEFAULT NOW | Fecha de creación |

---

### 4.11 GroupMember

**Tabla:** `group_members`

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| group_id | INTEGER | FK → instructor_groups.id, NOT NULL | Grupo |
| student_id | INTEGER | FK → users.id, NOT NULL | Alumno |
| joined_at | DATETIME | DEFAULT NOW | Fecha de unión |

**Constraint:** UNIQUE(group_id, student_id)

---

### 4.12 AnalysisComment

**Tabla:** `analysis_comments`

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| analysis_id | INTEGER | FK → analyses.id, NOT NULL | Análisis comentado |
| author_id | INTEGER | FK → users.id, NOT NULL | Autor del comentario |
| content | TEXT | NOT NULL | Texto del comentario |
| created_at | DATETIME | DEFAULT NOW | Fecha |

---

## 5. Contratos de API (Endpoints Completos)

### 5.1 Router: Auth — `/auth`

#### POST /auth/register
**Descripción:** Registra un nuevo usuario
**Auth:** No requerida

**Request body:**
```json
{
  "email": "string — email válido",
  "username": "string — 3-30 chars, alfanumérico y guiones bajos",
  "password": "string — mínimo 8 caracteres",
  "full_name": "string — mínimo 2 caracteres",
  "account_type": "string — 'alumno' o 'instructor'"
}
```
**Response 201:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "user": { "id": 1, "email": "...", "username": "...", "full_name": "...", "account_type": "..." }
}
```
**Errores:** 409 (email o username duplicado), 422 (validación)

---

#### POST /auth/login
**Auth:** No requerida

**Request body:**
```json
{ "email": "string", "password": "string" }
```
**Response 200:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "user": { "id": 1, "email": "...", "username": "...", "account_type": "..." }
}
```
**Errores:** 401 (credenciales incorrectas)

---

#### POST /auth/refresh
**Auth:** No requerida (el refresh token va en el body)

**Request body:**
```json
{ "refresh_token": "string" }
```
**Response 200:**
```json
{ "access_token": "string", "refresh_token": "string", "token_type": "bearer" }
```
**Errores:** 401 (refresh token inválido o expirado)

---

#### POST /auth/forgot-password
**Auth:** No requerida

**Request body:** `{ "email": "string" }`
**Response 200:** `{ "message": "Si este email está registrado, recibirás instrucciones en breve" }`
*(No envía email real — respuesta fija)*

---

#### GET /auth/me
**Auth:** Bearer token requerido

**Response 200:**
```json
{
  "id": 1, "email": "...", "username": "...", "full_name": "...",
  "account_type": "alumno", "bio": null, "gym": null, "city": null,
  "country": null, "experience_years": 0, "disciplines": [],
  "avatar_url": null, "xp": 0, "belt_level": "blanco",
  "current_streak": 0, "max_streak": 0, "streak_shields": 0,
  "created_at": "2026-05-28T10:00:00"
}
```

---

### 5.2 Router: Users — `/users`

#### PUT /users/me
**Auth:** Bearer requerido
**Content-Type:** multipart/form-data (para foto de perfil) o application/json (sin foto)

**Fields (todos opcionales):**
- `full_name: string`
- `bio: string`
- `gym: string`
- `city: string`
- `country: string`
- `experience_years: int`
- `disciplines: string` (JSON array)
- `avatar: file` (imagen JPG/PNG ≤ 2MB)

**Response 200:** UserProfileResponse (mismo schema que GET /auth/me)
**Errores:** 400 (imagen demasiado grande o formato incorrecto)

---

#### GET /users/{user_id}
**Auth:** Bearer requerido

**Response 200:**
```json
{
  "id": 1, "username": "...", "full_name": "...", "account_type": "...",
  "bio": null, "gym": null, "city": null, "belt_level": "blanco",
  "xp": 0, "current_streak": 0, "total_analyses": 0,
  "best_score": null, "average_score": null
}
```

---

### 5.3 Router: Disciplines — `/disciplines`

#### GET /disciplines
**Auth:** Bearer requerido

**Response 200:**
```json
[
  { "id": 1, "name": "muay_thai", "display_name": "Muay Thai", "description": "...", "icon_name": "..." },
  { "id": 2, "name": "bjj", "display_name": "BJJ", "description": "...", "icon_name": "..." },
  { "id": 3, "name": "boxing", "display_name": "Boxeo", "description": "...", "icon_name": "..." }
]
```

---

#### GET /disciplines/{discipline_id}/techniques
**Auth:** Bearer requerido

**Response 200:**
```json
[
  { "id": 1, "discipline_id": 1, "name": "jab", "display_name": "Jab", "description": "...", "difficulty": "easy", "xp_multiplier": 1.0 },
  ...
]
```
**Errores:** 404 (disciplina no encontrada)

---

### 5.4 Router: Analysis — `/analysis`

#### POST /analysis
**Auth:** Bearer requerido
**Content-Type:** multipart/form-data

**Form fields:**
- `technique_id: int` (requerido)
- `video: file` (requerido — MP4/MOV/AVI ≤ 60s, ≤ 200MB)

**Response 201:**
```json
{
  "id": 42,
  "status": "completed",
  "technique": { "id": 1, "display_name": "Jab", "discipline": "Boxeo" },
  "global_score": 73.5,
  "power_score": 80.0,
  "balance_score": 65.0,
  "alignment_score": 78.0,
  "speed_score": 70.0,
  "xp_awarded": 30,
  "joint_results": [
    {
      "joint_name": "right_elbow",
      "measured_angle": 145.2,
      "reference_min": 155.0,
      "reference_max": 180.0,
      "optimal_angle": 170.0,
      "is_correct": false,
      "deviation": -24.8
    }
  ],
  "feedback": [
    {
      "priority_order": 1,
      "correction_title": "Extensión de codo insuficiente",
      "correction_text": "Tu codo derecho alcanza solo 145° cuando debería llegar a 170°...",
      "biomechanical_explanation": "La extensión completa del codo maximiza el alcance y la transferencia de fuerza...",
      "exercise_suggestion": "Practica shadow boxing frente a un espejo enfocándote en la extensión total del brazo"
    }
  ],
  "video_overlay_url": "/analysis/42/download/overlay",
  "video_original_url": "/analysis/42/download/original",
  "created_at": "2026-05-28T10:00:00",
  "completed_at": "2026-05-28T10:01:30"
}
```
**Errores:** 400 (formato inválido, duración excedida), 404 (técnica no encontrada), 422 (validación), 500 (fallo de MediaPipe)

---

#### GET /analysis/{analysis_id}
**Auth:** Bearer requerido (propietario o instructor del alumno)

**Response 200:** AnalysisDetailResponse (mismo schema que POST /analysis response)
**Errores:** 404, 403 (no es el propietario ni instructor autorizado)

---

#### GET /analysis/me
**Auth:** Bearer requerido
**Query params:** `page=1`, `limit=20`, `discipline_id=int (opcional)`, `technique_id=int (opcional)`

**Response 200:**
```json
{
  "items": [
    {
      "id": 42, "technique_display_name": "Jab", "discipline_name": "Boxeo",
      "global_score": 73.5, "status": "completed",
      "video_overlay_url": "/analysis/42/download/overlay",
      "created_at": "2026-05-28T10:00:00"
    }
  ],
  "total": 15,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

---

#### GET /analysis/compare
**Auth:** Bearer requerido
**Query params:** `id1=int`, `id2=int` (ambos requeridos, deben ser del mismo usuario)

**Response 200:**
```json
{
  "analysis_1": { ...AnalysisDetailResponse... },
  "analysis_2": { ...AnalysisDetailResponse... },
  "score_difference": 12.5,
  "improved_joints": ["right_elbow", "left_shoulder"],
  "regressed_joints": []
}
```
**Errores:** 400 (técnicas distintas), 404, 403

---

#### GET /analysis/{analysis_id}/download/overlay
**Auth:** Bearer requerido

**Response 200:** FileResponse (video/mp4)
**Errores:** 404 (análisis no completado o sin overlay)

---

#### GET /analysis/{analysis_id}/download/original
**Auth:** Bearer requerido

**Response 200:** FileResponse (video/mp4 o video/quicktime)
**Errores:** 404

---

### 5.5 Router: Dashboard — `/dashboard`

#### GET /dashboard/me
**Auth:** Bearer requerido

**Response 200:**
```json
{
  "total_analyses": 25,
  "best_score": 94.5,
  "average_score": 72.3,
  "favorite_discipline": "Boxeo",
  "most_analyzed_technique": "Jab",
  "xp": 820,
  "belt_level": "amarillo",
  "xp_for_next_belt": 1500,
  "current_streak": 5,
  "max_streak": 12,
  "streak_shields": 1,
  "recent_badges": [
    { "badge_id": 1, "display_name": "Primer Golpe", "icon_name": "...", "earned_at": "..." }
  ],
  "recent_analyses": [
    { "id": 42, "technique_display_name": "Jab", "global_score": 73.5, "created_at": "..." }
  ]
}
```

---

#### GET /dashboard/me/progress
**Auth:** Bearer requerido
**Query params:** `discipline_id=int (opcional)`, `days=30 (default)`

**Response 200:**
```json
{
  "labels": ["2026-05-01", "2026-05-08", "2026-05-15", "2026-05-22"],
  "datasets": [
    { "discipline": "Boxeo", "data": [65.0, 68.5, 71.2, 73.5] }
  ]
}
```

---

#### GET /dashboard/me/heatmap
**Auth:** Bearer requerido

**Response 200:**
```json
{
  "data": [
    { "date": "2026-05-28", "count": 3 },
    { "date": "2026-05-27", "count": 1 }
  ]
}
```

---

### 5.6 Router: Gamification — `/gamification`

#### GET /gamification/badges
**Auth:** Bearer requerido

**Response 200:** Lista de todos los badges del sistema (sin importar si el usuario los tiene o no)
```json
[
  { "id": 1, "name": "first_analysis", "display_name": "Primer Golpe", "description": "...", "level": "bronze", "icon_name": "...", "xp_reward": 50 }
]
```

---

#### GET /gamification/me/badges
**Auth:** Bearer requerido

**Response 200:**
```json
[
  { "badge_id": 1, "display_name": "Primer Golpe", "icon_name": "...", "level": "bronze", "earned_at": "2026-05-28T10:00:00" }
]
```

---

#### GET /gamification/ranking
**Auth:** Bearer requerido
**Query params:** `page=1`, `limit=50`

**Response 200:**
```json
{
  "items": [
    { "rank": 1, "user_id": 5, "username": "fighter_mx", "full_name": "...", "belt_level": "negro", "xp": 15000, "avatar_url": null }
  ],
  "my_rank": 12,
  "total": 150
}
```

---

#### POST /gamification/me/buy-shield
**Auth:** Bearer requerido

**Response 200:** `{ "message": "Escudo de racha comprado", "shields_remaining": 2, "xp_remaining": 720 }`
**Errores:** 400 (XP insuficiente — cuesta 100 XP)

---

#### POST /gamification/me/use-shield
**Auth:** Bearer requerido

**Response 200:** `{ "message": "Escudo activado para hoy", "shields_remaining": 1 }`
**Errores:** 400 (no tiene escudos)

---

### 5.7 Router: Instructor — `/instructor`

#### POST /instructor/groups
**Auth:** Bearer requerido (account_type='instructor')

**Request body:** `{ "name": "string", "description": "string|null" }`
**Response 201:** `{ "id": 1, "name": "...", "description": "...", "invite_code": "ABC12345", "member_count": 0, "created_at": "..." }`
**Errores:** 403 (no es instructor)

---

#### GET /instructor/groups
**Auth:** Bearer requerido (account_type='instructor')

**Response 200:** Lista de grupos del instructor con conteo de miembros

---

#### GET /instructor/groups/{group_id}
**Auth:** Bearer requerido (instructor propietario)

**Response 200:** Detalle del grupo + lista de miembros con estadísticas básicas

---

#### POST /instructor/groups/join
**Auth:** Bearer requerido (account_type='alumno')

**Request body:** `{ "invite_code": "string" }`
**Response 200:** `{ "message": "Te has unido al grupo correctamente", "group_name": "..." }`
**Errores:** 404 (código inválido), 409 (ya es miembro)

---

#### GET /instructor/students/{student_id}/analyses
**Auth:** Bearer requerido (instructor con el alumno en algún grupo)

**Query params:** `page=1`, `limit=20`
**Response 200:** Mismo schema que GET /analysis/me

---

#### GET /instructor/students/{student_id}/stats
**Auth:** Bearer requerido (instructor con el alumno en algún grupo)

**Response 200:** Mismo schema que GET /dashboard/me pero del alumno indicado

---

#### POST /instructor/analyses/{analysis_id}/comment
**Auth:** Bearer requerido (instructor con acceso al análisis)

**Request body:** `{ "content": "string — mínimo 5 caracteres" }`
**Response 201:** `{ "id": 1, "content": "...", "author_username": "...", "created_at": "..." }`
**Errores:** 403 (no tiene acceso al análisis), 404

---

#### GET /analysis/{analysis_id}/comments
**Auth:** Bearer requerido

**Response 200:**
```json
[
  { "id": 1, "content": "...", "author_username": "...", "created_at": "..." }
]
```

---

## 6. Decisiones Técnicas

### DT-01: Procesamiento síncrono de vídeo
**Decisión:** El análisis de vídeo se ejecuta de forma síncrona en el endpoint POST /analysis. El cliente espera hasta que el procesamiento termina.
**Justificación:** El plazo de 6 días no permite implementar una cola de tareas (Celery, ARQ) de forma robusta. Los vídeos tienen un máximo de 60 segundos y el procesamiento en local es suficientemente rápido para una demo académica.
**Consecuencias:** El cliente (Axios) debe configurar timeout de 300 segundos.

### DT-02: SQLite como motor de base de datos
**Decisión:** SQLite con SQLAlchemy ORM. El archivo de base de datos se crea en `backend/fighterai.db`.
**Justificación:** Sin requisitos de concurrencia, escala ni despliegue. SQLite es suficiente para un entorno de demo local y simplifica enormemente el setup.
**Consecuencias:** `connect_args={"check_same_thread": False}` es obligatorio para FastAPI con async.

### DT-03: Codec de vídeo en Windows
**Decisión:** OpenCV VideoWriter usará el codec `mp4v` (MPEG-4) como primario y `XVID` como fallback. El fichero de salida será siempre `.mp4`.
**Justificación:** H264 puede no estar disponible en todos los sistemas Windows sin instalar codecs adicionales. `mp4v` es el más compatible.

### DT-04: Rutas de archivo con pathlib
**Decisión:** Todas las operaciones de sistema de archivos usarán `pathlib.Path` exclusivamente.
**Justificación:** Abstrae las diferencias entre separadores Windows (`\`) y Unix (`/`), evitando bugs de rutas.

### DT-05: JWT sin persistencia de refresh tokens
**Decisión:** Los refresh tokens se validan solo por firma criptográfica. No se almacenan en base de datos.
**Justificación:** Simplicidad para el plazo disponible. En producción se debería implementar una lista negra de tokens revocados.
**Consecuencias:** No es posible invalidar un refresh token sin cambiar el SECRET_KEY. Aceptable para entorno académico.

### DT-06: Almacenamiento local de vídeos
**Decisión:** Los vídeos se almacenan en `backend/storage/videos/user_{user_id}/original/` y `backend/storage/videos/user_{user_id}/overlay/`.
**Justificación:** Sin servicios de almacenamiento en la nube. Local es suficiente para demo académica.
**Consecuencias:** Los vídeos no persisten entre reinstalaciones. La carpeta `storage/` debe estar en `.gitignore`.

### DT-07: Seed automático al arrancar
**Decisión:** El archivo `seed/seed_data.py` se ejecuta automáticamente en el evento `startup` de FastAPI si las tablas están vacías.
**Justificación:** Garantiza que disciplinas, técnicas y referencias biomecánicas estén disponibles desde el primer arranque sin pasos manuales.

### DT-08: Autenticación por Bearer token en header
**Decisión:** Todos los endpoints protegidos usan `Authorization: Bearer {token}`.
**Justificación:** Estándar de la industria, compatible con el interceptor de Axios del frontend.

### DT-09: CORS configurado para localhost:3000
**Decisión:** El backend permite CORS desde `http://localhost:3000`.
**Justificación:** El frontend corre en ese puerto según los requisitos del cliente.

---

## 7. Datos Biomecánicos de Referencia (Seed)

La base de datos se pobla con las siguientes técnicas y referencias (12 técnicas, ~6 joints por técnica):

### Boxeo (discipline_id=3)
- **Jab** (difficulty: easy, xp_multiplier: 1.0): right_elbow [165-180°, opt 175°], right_shoulder [80-100°, opt 90°], left_elbow [85-100°, opt 90°], hip_rotation_proxy [10-30°, opt 20°], front_knee [145-165°, opt 155°]
- **Cross** (difficulty: medium, xp_multiplier: 1.5): right_elbow [165-180°, opt 175°], right_shoulder [80-100°, opt 90°], hip_rotation_proxy [35-55°, opt 45°], rear_knee [155-175°, opt 165°]
- **Hook** (difficulty: medium, xp_multiplier: 1.5): right_elbow [80-100°, opt 90°], right_shoulder [75-95°, opt 85°], hip_rotation_proxy [40-60°, opt 50°]
- **Uppercut** (difficulty: hard, xp_multiplier: 2.0): right_elbow [70-90°, opt 80°], front_knee [120-145°, opt 130°], right_hip [150-170°, opt 160°]

### Muay Thai (discipline_id=1)
- **Jab MT** (difficulty: easy, xp_multiplier: 1.0): right_elbow [165-180°, opt 175°], right_shoulder [80-100°, opt 90°], hip_rotation_proxy [10-30°, opt 20°]
- **Roundkick Medio** (difficulty: hard, xp_multiplier: 2.0): kicking_hip [80-110°, opt 95°], kicking_knee [150-175°, opt 165°], support_knee [135-155°, opt 145°], hip_rotation_proxy [45-65°, opt 55°]
- **Teep** (difficulty: medium, xp_multiplier: 1.5): kicking_hip [80-100°, opt 90°], kicking_knee [160-180°, opt 170°], support_knee [145-165°, opt 155°]
- **Cross MT** (difficulty: medium, xp_multiplier: 1.5): right_elbow [165-180°, opt 175°], hip_rotation_proxy [35-55°, opt 45°]

### BJJ (discipline_id=2)
- **Armbar desde guardia** (difficulty: hard, xp_multiplier: 2.0): hip_flexion [85-105°, opt 95°], target_arm_extension [165-180°, opt 175°], knee_pinch [80-100°, opt 90°]
- **Guardia Cerrada** (difficulty: easy, xp_multiplier: 1.0): hip_flexion [85-110°, opt 100°], knee_bend [100-130°, opt 115°]
- **Montada** (difficulty: medium, xp_multiplier: 1.5): hip_extension [155-175°, opt 165°], knee_flexion [85-110°, opt 95°]
- **Triángulo** (difficulty: hard, xp_multiplier: 2.0): hip_flexion [90-115°, opt 105°], ankle_behind_knee [80-100°, opt 90°], target_arm_lock [160-180°, opt 170°]

---

## 8. Briefing para Dev1 (Backend)
*(Ver documento 06_briefing_dev1.md)*

## 9. Briefing para Dev2 (Frontend)
*(Ver documento 07_briefing_dev2.md)*

✅ DOCUMENTO COMPLETADO
