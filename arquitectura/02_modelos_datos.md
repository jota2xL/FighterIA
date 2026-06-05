# Arquitectura FighterIA — Entregable 2: Modelos de Datos

> **Autor:** Agente Arquitecto de Software Senior | **Fecha:** 2026-05-28

---

## Diagrama de Relaciones

```
users ──────────────────────────────────────────────────────────┐
  │ 1:N analyses                                                  │
  │ 1:N user_badges                                               │
  │ 1:N instructor_groups (FK instructor_id)                      │
  │ 1:N group_members (FK student_id)                             │
  │                                                               │
analyses ──────────────────────────────────────────────────────┐  │
  │ 1:N analysis_joint_results                                  │  │
  │ 1:N analysis_feedback                                        │  │
  │ 1:N analysis_comments                                        │  │
  │ N:1 techniques                                               │  │
  │                                                               │  │
techniques ────────────────────────────────────────────────────┐│  │
  │ N:1 disciplines                                              ││  │
  │ 1:N biomechanical_references                                 ││  │
  │                                                               ││  │
badges ─── 1:N user_badges ─────────────────────────────────── ┘│  │
instructor_groups ─── 1:N group_members ──────────────────────  ┘  │
analysis_comments ─── N:1 users (author_id) ──────────────────────┘
```

---

## Entidad: User

**Tabla:** `users`
**Descripción:** Usuario registrado. Contiene autenticación, perfil, estado de gamificación y racha de entrenamiento.

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Email de login |
| username | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Nombre público único |
| password_hash | VARCHAR(255) | NOT NULL | Hash bcrypt — nunca exponer |
| full_name | VARCHAR(100) | NOT NULL | Nombre completo |
| account_type | VARCHAR(20) | NOT NULL, DEFAULT 'alumno' | 'alumno' \| 'instructor' |
| bio | VARCHAR(500) | NULLABLE | Biografía corta |
| gym | VARCHAR(100) | NULLABLE | Gimnasio donde entrena |
| city | VARCHAR(100) | NULLABLE | Ciudad (opcional para ranking) |
| country | VARCHAR(100) | NULLABLE | País (opcional para ranking) |
| experience_years | INTEGER | DEFAULT 0 | Años de experiencia en MMAA |
| disciplines | VARCHAR(255) | NULLABLE | JSON array: '["muay_thai","bjj"]' |
| avatar_url | VARCHAR(500) | NULLABLE | Ruta relativa: /storage/avatars/avatar_{id}.jpg |
| xp | INTEGER | DEFAULT 0, NOT NULL | XP acumulado total |
| belt_level | VARCHAR(20) | DEFAULT 'blanco', NOT NULL | Cinturón actual |
| current_streak | INTEGER | DEFAULT 0 | Días consecutivos de entrenamiento |
| max_streak | INTEGER | DEFAULT 0 | Racha máxima histórica |
| last_activity_date | DATE | NULLABLE | Último día con análisis completado |
| streak_shield_active | BOOLEAN | DEFAULT FALSE | Escudo de racha activo para hoy |
| streak_shields | INTEGER | DEFAULT 0 | Escudos de racha disponibles |
| is_active | BOOLEAN | DEFAULT TRUE | Cuenta activa |
| created_at | DATETIME | DEFAULT NOW | Fecha de registro |
| updated_at | DATETIME | ON UPDATE NOW | Última modificación |

**Relaciones:**
- `User` tiene muchos `Analysis` → `analyses.user_id`
- `User` tiene muchos `UserBadge` → `user_badges.user_id`
- `User` tiene muchos `InstructorGroup` (como instructor) → `instructor_groups.instructor_id`
- `User` tiene muchos `GroupMember` (como alumno) → `group_members.student_id`

**Índices:** `idx_users_email`, `idx_users_username`

---

## Entidad: Discipline

**Tabla:** `disciplines`
**Descripción:** Disciplina marcial (Muay Thai, BJJ, Boxeo). Catálogo fijo, poblado por seed.

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| name | VARCHAR(50) | UNIQUE, NOT NULL | Identificador: 'muay_thai', 'bjj', 'boxing' |
| display_name | VARCHAR(100) | NOT NULL | 'Muay Thai', 'BJJ', 'Boxeo' |
| description | TEXT | NULLABLE | Descripción para mostrar al usuario |
| icon_name | VARCHAR(50) | NULLABLE | Nombre del icono (frontend lo resuelve) |

**Relaciones:**
- `Discipline` tiene muchos `Technique` → `techniques.discipline_id`

---

## Entidad: Technique

**Tabla:** `techniques`
**Descripción:** Técnica marcial específica dentro de una disciplina. Cada técnica tiene referencias biomecánicas.

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| discipline_id | INTEGER | FK → disciplines.id, NOT NULL, INDEX | Disciplina propietaria |
| name | VARCHAR(100) | NOT NULL | 'jab', 'roundkick_medio', 'armbar' |
| display_name | VARCHAR(100) | NOT NULL | 'Jab', 'Roundkick Medio', 'Armbar' |
| description | TEXT | NULLABLE | Descripción y puntos clave de la técnica |
| difficulty | VARCHAR(20) | DEFAULT 'medium' | 'easy' \| 'medium' \| 'hard' |
| xp_multiplier | FLOAT | DEFAULT 1.0 | easy=1.0, medium=1.5, hard=2.0 |

**Relaciones:**
- `Technique` pertenece a `Discipline` → `discipline_id`
- `Technique` tiene muchos `BiomechanicalReference` → `biomechanical_references.technique_id`
- `Technique` tiene muchos `Analysis` → `analyses.technique_id`

**Índices:** `idx_techniques_discipline_id`

---

## Entidad: BiomechanicalReference

**Tabla:** `biomechanical_references`
**Descripción:** Ángulos articulares de referencia correcta para una técnica específica. Base de comparación del análisis.

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| technique_id | INTEGER | FK → techniques.id, NOT NULL, INDEX | Técnica a la que aplica |
| joint_name | VARCHAR(50) | NOT NULL | 'left_elbow', 'right_shoulder', etc. |
| phase | VARCHAR(30) | DEFAULT 'execution' | 'execution' \| 'final_position' |
| min_angle | FLOAT | NOT NULL | Ángulo mínimo correcto (grados) |
| max_angle | FLOAT | NOT NULL | Ángulo máximo correcto (grados) |
| optimal_angle | FLOAT | NOT NULL | Ángulo ideal de referencia |
| weight | FLOAT | DEFAULT 1.0 | Peso en el cálculo de puntuación |
| description | TEXT | NULLABLE | Explicación biomecánica de esta referencia |

**Relaciones:**
- `BiomechanicalReference` pertenece a `Technique` → `technique_id`

**Índices:** `idx_bio_refs_technique_id`

**Valores de joint_name válidos:**
```
left_elbow, right_elbow, left_shoulder, right_shoulder,
left_knee, right_knee, left_hip, right_hip,
kicking_hip, kicking_knee, support_knee,
hip_rotation_proxy, hip_flexion, hip_extension,
target_arm_extension, target_arm_lock,
knee_pinch, knee_bend, knee_flexion,
front_knee, rear_knee, ankle_behind_knee
```

---

## Entidad: Analysis

**Tabla:** `analyses`
**Descripción:** Registro de un análisis de vídeo completo. Contiene rutas de vídeo, puntuaciones y estado del procesamiento.

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| user_id | INTEGER | FK → users.id, NOT NULL, INDEX | Usuario propietario |
| technique_id | INTEGER | FK → techniques.id, NOT NULL | Técnica analizada |
| video_original_path | VARCHAR(500) | NOT NULL | Ruta absoluta al vídeo original |
| video_overlay_path | VARCHAR(500) | NULLABLE | Ruta absoluta al vídeo con overlay |
| status | VARCHAR(20) | DEFAULT 'pending' | 'pending'\|'processing'\|'completed'\|'failed' |
| global_score | FLOAT | NULLABLE | Puntuación global 0-100 (null si no completado) |
| power_score | FLOAT | NULLABLE | Sub-score potencia 0-100 |
| balance_score | FLOAT | NULLABLE | Sub-score equilibrio 0-100 |
| alignment_score | FLOAT | NULLABLE | Sub-score alineación 0-100 |
| speed_score | FLOAT | NULLABLE | Sub-score velocidad 0-100 |
| xp_awarded | INTEGER | DEFAULT 0 | XP otorgado por este análisis |
| is_public | BOOLEAN | DEFAULT FALSE | Accesible por link público |
| error_message | TEXT | NULLABLE | Motivo del fallo si status='failed' |
| created_at | DATETIME | DEFAULT NOW | Fecha de subida |
| completed_at | DATETIME | NULLABLE | Fecha en que terminó el procesamiento |

**Relaciones:**
- `Analysis` pertenece a `User` → `user_id`
- `Analysis` pertenece a `Technique` → `technique_id`
- `Analysis` tiene muchos `AnalysisJointResult` (cascade delete)
- `Analysis` tiene muchos `AnalysisFeedback` (cascade delete, ordered by priority_order)
- `Analysis` tiene muchos `AnalysisComment` (cascade delete)

**Índices:** `idx_analyses_user_id`, `idx_analyses_status`, `idx_analyses_created_at`

---

## Entidad: AnalysisJointResult

**Tabla:** `analysis_joint_results`
**Descripción:** Ángulo medido en cada articulación para el frame clave de un análisis. Un análisis tiene entre 3 y 6 joint results.

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| analysis_id | INTEGER | FK → analyses.id, NOT NULL, INDEX | Análisis al que pertenece |
| joint_name | VARCHAR(50) | NOT NULL | Articulación medida |
| measured_angle | FLOAT | NOT NULL | Ángulo real en el frame clave (grados) |
| reference_min | FLOAT | NOT NULL | Referencia mínima correcta |
| reference_max | FLOAT | NOT NULL | Referencia máxima correcta |
| optimal_angle | FLOAT | NOT NULL | Ángulo óptimo de referencia |
| is_correct | BOOLEAN | NOT NULL | TRUE si measured ∈ [min, max] |
| deviation | FLOAT | NOT NULL | measured_angle − optimal_angle |

**Relaciones:** `AnalysisJointResult` pertenece a `Analysis`

---

## Entidad: AnalysisFeedback

**Tabla:** `analysis_feedback`
**Descripción:** Corrección textual priorizada generada para una articulación fuera de rango. Solo existe si hay errores.

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| analysis_id | INTEGER | FK → analyses.id, NOT NULL, INDEX | Análisis al que pertenece |
| correction_title | VARCHAR(200) | NOT NULL | Título corto del error |
| correction_text | TEXT | NOT NULL | Descripción completa |
| biomechanical_explanation | TEXT | NULLABLE | Por qué importa biomecánicamente |
| exercise_suggestion | TEXT | NULLABLE | Ejercicio para corregirlo |
| priority_order | INTEGER | NOT NULL | 1 = mayor impacto |
| impact_score | FLOAT | NOT NULL | 0.0–1.0, derivado de la desviación |

**Relaciones:** `AnalysisFeedback` pertenece a `Analysis`

---

## Entidad: AnalysisComment

**Tabla:** `analysis_comments`
**Descripción:** Comentario de un instructor sobre el análisis de un alumno.

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| analysis_id | INTEGER | FK → analyses.id, NOT NULL, INDEX | Análisis comentado |
| author_id | INTEGER | FK → users.id, NOT NULL | Autor del comentario |
| content | TEXT | NOT NULL | Texto del comentario (mín. 5 chars) |
| created_at | DATETIME | DEFAULT NOW | Fecha |

---

## Entidad: Badge

**Tabla:** `badges`
**Descripción:** Catálogo de logros del sistema. Poblado por seed. 7 badges en el MVP.

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Clave interna: 'first_analysis', 'streak_7' |
| display_name | VARCHAR(100) | NOT NULL | Nombre visible: 'Primer Golpe' |
| description | TEXT | NOT NULL | Cómo se consigue |
| level | VARCHAR(20) | NOT NULL | 'bronze' \| 'silver' \| 'gold' |
| icon_name | VARCHAR(50) | NOT NULL | Nombre de icono para frontend |
| condition_type | VARCHAR(50) | NOT NULL | Tipo de condición para evaluar |
| condition_value | INTEGER | DEFAULT 1 | Valor numérico de la condición |
| xp_reward | INTEGER | DEFAULT 50 | XP al desbloquear |

**Tipos de condición:**

| condition_type | Evaluación |
|---------------|-----------|
| first_analysis | Total análisis completados ≥ 1 |
| streak_7 | current_streak ≥ 7 |
| score_100 | Algún analysis con global_score = 100 |
| muay_thai_50 | Total análisis de Muay Thai ≥ 50 |
| bjj_50 | Total análisis de BJJ ≥ 50 |
| boxing_50 | Total análisis de Boxeo ≥ 50 |
| belt_negro | belt_level = 'negro' |

---

## Entidad: UserBadge

**Tabla:** `user_badges`
**Descripción:** Asociación usuario-badge cuando se desbloquea un logro.

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| user_id | INTEGER | FK → users.id, NOT NULL, INDEX | Usuario |
| badge_id | INTEGER | FK → badges.id, NOT NULL | Badge desbloqueado |
| earned_at | DATETIME | DEFAULT NOW | Fecha de desbloqueo |

**Constraint:** `UNIQUE(user_id, badge_id)` — un badge solo se desbloquea una vez por usuario

---

## Entidad: InstructorGroup

**Tabla:** `instructor_groups`
**Descripción:** Grupo de alumnos creado por un instructor con código de invitación.

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| instructor_id | INTEGER | FK → users.id, NOT NULL, INDEX | Instructor propietario |
| name | VARCHAR(100) | NOT NULL | Nombre del grupo |
| description | TEXT | NULLABLE | Descripción opcional |
| invite_code | VARCHAR(20) | UNIQUE, NOT NULL | Código alfanumérico de 8 chars |
| is_active | BOOLEAN | DEFAULT TRUE | Grupo activo |
| created_at | DATETIME | DEFAULT NOW | Fecha de creación |

---

## Entidad: GroupMember

**Tabla:** `group_members`
**Descripción:** Alumno que pertenece a un grupo de instructor.

| Campo | Tipo SQL | Constraints | Descripción |
|-------|----------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | ID único |
| group_id | INTEGER | FK → instructor_groups.id, NOT NULL, INDEX | Grupo |
| student_id | INTEGER | FK → users.id, NOT NULL | Alumno |
| joined_at | DATETIME | DEFAULT NOW | Fecha de unión |

**Constraint:** `UNIQUE(group_id, student_id)` — un alumno no puede unirse dos veces al mismo grupo

---

## Notas de Implementación

1. **SQLite `check_same_thread=False`** es obligatorio en el engine para FastAPI (async)
2. **`cascade="all, delete-orphan"`** en relaciones padre-hijo (Analysis → JointResults, Feedback, Comments)
3. **`order_by="AnalysisFeedback.priority_order"`** en la relación `analysis.feedback` garantiza el orden en la carga
4. **`back_populates`** en todas las relaciones bidireccionales para consistencia del ORM
5. **`server_default=func.now()`** en lugar de `default=datetime.utcnow` para que SQLite lo gestione

✅ ENTREGABLE 2 COMPLETADO
