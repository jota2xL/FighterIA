# Arquitectura FighterIA — Entregable 1: Estructura de Carpetas

> **Autor:** Agente Arquitecto de Software Senior
> **Proyecto:** FighterIA | **Fecha:** 2026-05-28
> **Basado en:** Briefing del PO (docs/05_briefing_arquitecto.md)

---

## Backend — Árbol de Directorios

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app: CORS, routers, static files, startup event
│   ├── config.py                    # Settings via pydantic-settings (carga .env)
│   ├── database.py                  # Engine SQLite, SessionLocal, Base declarativa, get_db
│   │
│   ├── models/                      # ORM — mapean clases Python a tablas SQLite
│   │   ├── __init__.py              # Importa todos los modelos para que Base los registre
│   │   ├── user.py                  # User (auth + perfil + gamificación + racha)
│   │   ├── discipline.py            # Discipline + Technique
│   │   ├── biomechanical.py         # BiomechanicalReference (ángulos correctos por joint/técnica)
│   │   ├── analysis.py              # Analysis + AnalysisJointResult + AnalysisFeedback
│   │   ├── gamification.py          # Badge + UserBadge
│   │   └── instructor.py            # InstructorGroup + GroupMember + AnalysisComment
│   │
│   ├── schemas/                     # Pydantic v2 — contratos de request/response
│   │   ├── __init__.py
│   │   ├── auth.py                  # RegisterRequest, LoginRequest, RefreshRequest, TokenResponse, ForgotPasswordRequest
│   │   ├── user.py                  # UserResponse, UserUpdate, PublicUserResponse, UserStatsResponse
│   │   ├── discipline.py            # DisciplineResponse, TechniqueResponse
│   │   ├── analysis.py              # AnalysisCreateResponse, AnalysisListItem, AnalysisListResponse,
│   │   │                            #   AnalysisDetailResponse, JointResultSchema, FeedbackItemSchema,
│   │   │                            #   CompareResponse, CommentResponse, CommentCreate
│   │   ├── dashboard.py             # DashboardResponse, ProgressResponse, HeatmapResponse,
│   │   │                            #   ProgressDataset, HeatmapEntry
│   │   ├── gamification.py          # BadgeResponse, UserBadgeResponse, RankingItem, RankingResponse,
│   │   │                            #   ShieldResponse
│   │   └── instructor.py            # GroupCreate, GroupResponse, GroupDetailResponse,
│   │                                #   GroupMemberSummary, JoinGroupRequest
│   │
│   ├── routers/                     # FastAPI routers — reciben HTTP, llaman a services
│   │   ├── __init__.py
│   │   ├── auth.py                  # POST /auth/register|login|refresh|forgot-password, GET /auth/me
│   │   ├── users.py                 # PUT /users/me, GET /users/{id}
│   │   ├── disciplines.py           # GET /disciplines, GET /disciplines/{id}/techniques
│   │   ├── analysis.py              # POST /analysis, GET /analysis/me|compare|{id},
│   │   │                            #   GET /analysis/{id}/download/overlay|original,
│   │   │                            #   GET /analysis/{id}/comments
│   │   ├── dashboard.py             # GET /dashboard/me, /progress, /heatmap
│   │   ├── gamification.py          # GET /gamification/badges, /me/badges, /ranking,
│   │   │                            #   POST /gamification/me/buy-shield, /me/use-shield
│   │   └── instructor.py            # POST /instructor/groups, GET /instructor/groups|groups/{id},
│   │                                #   POST /instructor/groups/join,
│   │                                #   GET /instructor/students/{id}/analyses|stats,
│   │                                #   POST /instructor/analyses/{id}/comment
│   │
│   ├── services/                    # Lógica de negocio — sin dependencia de HTTP
│   │   ├── __init__.py
│   │   ├── auth_service.py          # get_current_user (Depends), verify credentials
│   │   ├── user_service.py          # get_by_id, get_by_email, update_profile, upload_avatar
│   │   ├── video_service.py         # validate_format, validate_duration, save_upload
│   │   ├── mediapipe_service.py     # PoseAnalyzer (OpenCV + MediaPipe, overlay generation)
│   │   ├── analysis_service.py      # *** ORQUESTADOR PRINCIPAL *** del pipeline completo
│   │   ├── scoring_service.py       # calculate_scores (alignment, power, balance, speed, global)
│   │   ├── feedback_service.py      # generate_feedback (texto por joint fuera de rango)
│   │   ├── gamification_service.py  # award_xp, get_belt_for_xp, update_streak, check_badges
│   │   └── instructor_service.py    # create_group, join_group, get_student_stats
│   │
│   └── utils/
│       ├── __init__.py
│       ├── security.py              # create_access_token, create_refresh_token, decode_token,
│       │                            #   hash_password, verify_password
│       └── storage.py               # get_original_video_path, get_overlay_video_path,
│                                    #   get_avatar_path (todas usan pathlib.Path)
│
├── seed/
│   ├── __init__.py
│   └── seed_data.py                 # Pobla disciplines, techniques, bio_refs, badges (idempotente)
│
├── storage/                         # Runtime — en .gitignore
│   ├── videos/
│   │   └── user_{id}/
│   │       ├── original/            # {analysis_id}_original.{ext}
│   │       └── overlay/             # {analysis_id}_overlay.mp4
│   └── avatars/                     # avatar_{user_id}.{ext}
│
├── tests/
│   ├── conftest.py                  # Fixtures: engine test, db, client, test_user, auth_headers
│   ├── unit/
│   │   ├── test_scoring_service.py
│   │   ├── test_feedback_service.py
│   │   └── test_gamification_service.py
│   └── integration/
│       ├── test_auth.py
│       ├── test_disciplines.py
│       ├── test_analysis.py
│       └── test_dashboard.py
│
├── .env
├── .env.example
├── requirements.txt
└── fighterai.db                     # Creado en runtime — en .gitignore
```

---

## Frontend — Árbol de Directorios

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                      # Átomos reutilizables
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx            # Input + Label + error message
│   │   │   ├── Card.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Spinner.tsx          # Con mensajes motivacionales opcionales
│   │   │   ├── ErrorMessage.tsx     # Error state con retry opcional
│   │   │   └── EmptyState.tsx       # Empty state con acción opcional
│   │   │
│   │   ├── layout/
│   │   │   ├── Navbar.tsx           # Logo, nav links, avatar dropdown, belt indicator
│   │   │   └── ProtectedRoute.tsx   # Wrapper de autenticación
│   │   │
│   │   ├── analysis/
│   │   │   ├── TechniqueSelector.tsx # Selector cascada disciplina → técnica
│   │   │   ├── VideoUploader.tsx    # Drag & drop + validación cliente
│   │   │   ├── AnalysisCard.tsx     # Card de análisis en historial
│   │   │   ├── ScoreDisplay.tsx     # Puntuación global + 4 sub-scores
│   │   │   ├── JointResultsTable.tsx# Tabla articulaciones medidas vs referencia
│   │   │   ├── FeedbackList.tsx     # Lista de correcciones expandibles
│   │   │   └── VideoPlayer.tsx      # Player HTML5 con controles
│   │   │
│   │   ├── dashboard/
│   │   │   ├── StatsCard.tsx        # Card de estadística individual
│   │   │   ├── ProgressChart.tsx    # Recharts LineChart con filtros
│   │   │   ├── ActivityHeatmap.tsx  # react-calendar-heatmap 90 días
│   │   │   └── BeltProgress.tsx     # Cinturón + barra XP
│   │   │
│   │   ├── gamification/
│   │   │   ├── BadgeCard.tsx        # Card de badge con estado earned/locked
│   │   │   ├── StreakCounter.tsx    # Contador de racha con flame icon
│   │   │   └── XPBar.tsx            # Mini barra XP para navbar
│   │   │
│   │   └── instructor/
│   │       ├── GroupCard.tsx
│   │       ├── StudentRow.tsx
│   │       └── CommentBox.tsx
│   │
│   ├── pages/
│   │   ├── LandingPage.tsx          # Pública — hero + features + CTA
│   │   ├── LoginPage.tsx            # Formulario login
│   │   ├── RegisterPage.tsx         # Formulario registro
│   │   ├── DashboardPage.tsx        # Dashboard principal autenticado
│   │   ├── NewAnalysisPage.tsx      # Flujo: selector → upload → loader → redirect
│   │   ├── AnalysisResultPage.tsx   # Resultado: vídeo + scores + feedback
│   │   ├── HistoryPage.tsx          # Grid de análisis paginados
│   │   ├── ProfilePage.tsx          # Edición de perfil + estadísticas
│   │   ├── BadgesPage.tsx           # Galería de todos los badges
│   │   ├── InstructorPanelPage.tsx  # Lista de grupos
│   │   ├── InstructorGroupPage.tsx  # Detalle grupo + alumnos
│   │   ├── InstructorStudentPage.tsx# Dashboard individual del alumno
│   │   └── NotFoundPage.tsx
│   │
│   ├── layouts/
│   │   ├── MainLayout.tsx           # Navbar + <Outlet /> + footer
│   │   └── AuthLayout.tsx           # Centrado con logo para login/register
│   │
│   ├── hooks/
│   │   ├── useAuth.ts               # Wrapper de authStore con helpers
│   │   ├── useAnalysis.ts           # useQuery/useMutation para análisis
│   │   └── useGamification.ts       # useQuery para badges, ranking, XP
│   │
│   ├── services/
│   │   ├── api.client.ts            # Axios instance + interceptors (auth + refresh)
│   │   ├── auth.service.ts
│   │   ├── analysis.service.ts
│   │   ├── dashboard.service.ts
│   │   ├── gamification.service.ts
│   │   └── instructor.service.ts
│   │
│   ├── store/
│   │   └── auth.store.ts            # Zustand + persist: user, tokens, logout
│   │
│   ├── types/
│   │   ├── auth.types.ts
│   │   ├── analysis.types.ts
│   │   ├── dashboard.types.ts
│   │   ├── gamification.types.ts
│   │   └── instructor.types.ts
│   │
│   ├── utils/
│   │   ├── cn.ts                    # clsx + tailwind-merge
│   │   └── format.ts                # formatDate, formatScore, formatBelt
│   │
│   ├── App.tsx                      # Router + rutas protegidas + instructor guard
│   ├── main.tsx                     # QueryClient + Toaster + StrictMode
│   └── index.css                    # Tailwind directives + fuentes
│
├── public/
│   └── favicon.ico
├── .env
├── .env.example
├── index.html
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── vite.config.ts                   # port: 3000, proxy /api → 8000, alias @/
```

---

## Reglas de Nomenclatura

| Elemento | Convención | Ejemplo |
|----------|-----------|---------|
| Tablas BD | snake_case plural | `analysis_joint_results` |
| Columnas BD | snake_case | `global_score`, `created_at` |
| Modelos Python | PascalCase | `AnalysisJointResult` |
| Schemas Pydantic | PascalCase + sufijo | `AnalysisDetailResponse` |
| Routers FastAPI | snake_case módulo | `analysis.py` |
| Componentes React | PascalCase | `ScoreDisplay.tsx` |
| Servicios frontend | camelCase + sufijo | `analysisService` |
| Tipos TypeScript | PascalCase | `AnalysisDetailResponse` |
| Variables Python | snake_case | `global_score` |
| Variables TS | camelCase | `globalScore` |

✅ ENTREGABLE 1 COMPLETADO
