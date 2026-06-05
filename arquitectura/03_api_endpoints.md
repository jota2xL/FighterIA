# Arquitectura FighterIA — Entregable 3: Contratos de API

> **Autor:** Agente Arquitecto de Software Senior | **Fecha:** 2026-05-28
> **Base URL:** `http://localhost:8000`
> **Auth:** Bearer JWT en header `Authorization: Bearer {token}` salvo indicación contraria

---

## ROUTER: /auth — Autenticación

### POST /auth/register

**Descripción:** Registra un nuevo usuario y retorna tokens de acceso.
**Auth:** No requerida

**Request body (JSON):**
```json
{
  "email": "string — email válido, unique",
  "username": "string — 3-30 chars, alfanumérico + guiones bajos, unique",
  "password": "string — mínimo 8 caracteres",
  "full_name": "string — mínimo 2 caracteres",
  "account_type": "string — 'alumno' | 'instructor'"
}
```

**Response 201:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "user": {
    "id": 1, "email": "user@example.com", "username": "fighter",
    "full_name": "Carlos López", "account_type": "alumno",
    "xp": 0, "belt_level": "blanco", "current_streak": 0,
    "avatar_url": null, "created_at": "2026-05-28T10:00:00"
  }
}
```

**Errores:**
| Código | Motivo |
|--------|--------|
| 409 | Email o username ya registrado |
| 422 | Validación fallida (email inválido, password corta, etc.) |

---

### POST /auth/login

**Auth:** No requerida

**Request body:**
```json
{ "email": "string", "password": "string" }
```

**Response 200:** mismo schema que register (TokenResponse)

**Errores:**
| Código | Motivo |
|--------|--------|
| 401 | "Email o contraseña incorrectos" — mensaje genérico sin especificar cuál |

---

### POST /auth/refresh

**Auth:** No requerida (el refresh token va en el body)

**Request body:**
```json
{ "refresh_token": "string" }
```

**Response 200:**
```json
{ "access_token": "string", "refresh_token": "string", "token_type": "bearer" }
```

**Errores:** 401 (token inválido o expirado)

---

### POST /auth/forgot-password

**Auth:** No requerida

**Request body:** `{ "email": "string" }`

**Response 200:** `{ "message": "Si este email está registrado, recibirás instrucciones en breve" }`

> **NOTA IMPLEMENTACIÓN:** Respuesta fija independientemente de si el email existe. No envía email real.

---

### GET /auth/me

**Auth:** Bearer requerido

**Response 200:**
```json
{
  "id": 1, "email": "user@example.com", "username": "fighter",
  "full_name": "Carlos López", "account_type": "alumno",
  "bio": null, "gym": "CrossFight Madrid", "city": "Madrid",
  "country": "España", "experience_years": 3,
  "disciplines": ["boxing", "muay_thai"],
  "avatar_url": "/storage/avatars/avatar_1.jpg",
  "xp": 820, "belt_level": "amarillo",
  "current_streak": 5, "max_streak": 12, "streak_shields": 1,
  "is_active": true, "created_at": "2026-05-28T10:00:00"
}
```

---

## ROUTER: /users — Perfil de Usuario

### PUT /users/me

**Auth:** Bearer requerido
**Content-Type:** `multipart/form-data`

**Form fields (todos opcionales):**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| full_name | string | Nombre completo |
| bio | string | Biografía (máx 500 chars) |
| gym | string | Gimnasio |
| city | string | Ciudad |
| country | string | País |
| experience_years | int | Años de experiencia |
| disciplines | string | JSON array: '["boxing","bjj"]' |
| avatar | file | Imagen JPG/PNG ≤ 2MB |

**Response 200:** UserResponse completo (mismo schema que GET /auth/me)

**Errores:** 400 (imagen > 2MB o formato inválido)

---

### GET /users/{user_id}

**Auth:** Bearer requerido

**Path params:** `user_id: int`

**Response 200:**
```json
{
  "id": 2, "username": "striker_pro",
  "full_name": "Ahmed Karim", "account_type": "alumno",
  "bio": "Boxeador amateur.", "gym": "Ring Madrid",
  "belt_level": "verde", "xp": 3500,
  "current_streak": 8, "avatar_url": null,
  "total_analyses": 42, "best_score": 91.5, "average_score": 74.2
}
```

**Errores:** 404 (usuario no existe)

---

## ROUTER: /disciplines — Catálogo

### GET /disciplines

**Auth:** Bearer requerido

**Response 200:**
```json
[
  { "id": 1, "name": "muay_thai", "display_name": "Muay Thai", "description": "Arte marcial tailandés...", "icon_name": "muay-thai" },
  { "id": 2, "name": "bjj",       "display_name": "BJJ",       "description": "Jiu-Jitsu Brasileño...", "icon_name": "bjj" },
  { "id": 3, "name": "boxing",    "display_name": "Boxeo",     "description": "Arte del boxeo occidental.", "icon_name": "boxing" }
]
```

---

### GET /disciplines/{discipline_id}/techniques

**Auth:** Bearer requerido

**Path params:** `discipline_id: int`

**Response 200:**
```json
[
  { "id": 1, "discipline_id": 3, "name": "jab", "display_name": "Jab", "description": "Golpe recto con brazo delantero.", "difficulty": "easy", "xp_multiplier": 1.0 },
  { "id": 2, "discipline_id": 3, "name": "cross", "display_name": "Cross", "description": "Golpe recto trasero con rotación.", "difficulty": "medium", "xp_multiplier": 1.5 }
]
```

**Errores:** 404 (disciplina no existe)

---

## ROUTER: /analysis — Análisis de Vídeo

### POST /analysis

**Auth:** Bearer requerido
**Content-Type:** `multipart/form-data`
**⚠️ TIMEOUT:** El cliente debe configurar timeout de 300 segundos (procesamiento síncrono)

**Form fields:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| technique_id | int | Sí | ID de la técnica seleccionada |
| video | file | Sí | MP4/MOV/AVI ≤ 60s ≤ 200MB |

**Response 201:**
```json
{
  "id": 42,
  "status": "completed",
  "technique": {
    "id": 1, "name": "jab", "display_name": "Jab",
    "discipline_name": "Boxeo", "difficulty": "easy"
  },
  "global_score": 73.5,
  "power_score": 80.0,
  "balance_score": 65.0,
  "alignment_score": 78.0,
  "speed_score": 70.0,
  "xp_awarded": 30,
  "belt_upgraded": false,
  "new_belt": null,
  "newly_earned_badges": [],
  "joint_results": [
    {
      "joint_name": "right_elbow",
      "measured_angle": 145.2,
      "reference_min": 165.0,
      "reference_max": 180.0,
      "optimal_angle": 175.0,
      "is_correct": false,
      "deviation": -29.8
    },
    {
      "joint_name": "right_shoulder",
      "measured_angle": 88.5,
      "reference_min": 80.0,
      "reference_max": 100.0,
      "optimal_angle": 90.0,
      "is_correct": true,
      "deviation": -1.5
    }
  ],
  "feedback": [
    {
      "priority_order": 1,
      "correction_title": "Extensión de codo derecho insuficiente",
      "correction_text": "Tu codo derecho alcanza 145° cuando el rango correcto es 165°-180°...",
      "biomechanical_explanation": "La extensión completa maximiza el alcance y la transferencia de fuerza...",
      "exercise_suggestion": "Practica shadow boxing frente al espejo enfocándote en extender el brazo.",
      "impact_score": 0.85
    }
  ],
  "video_overlay_url": "/analysis/42/download/overlay",
  "video_original_url": "/analysis/42/download/original",
  "created_at": "2026-05-28T10:00:00",
  "completed_at": "2026-05-28T10:01:30",
  "error_message": null
}
```

**Errores:**
| Código | Motivo |
|--------|--------|
| 400 | Formato de vídeo inválido, duración > 60s, o tamaño > 200MB |
| 404 | technique_id no existe |
| 422 | technique_id faltante |
| 500 | MediaPipe no detecta ninguna persona en el vídeo (error_message descriptivo) |

---

### GET /analysis/me

**Auth:** Bearer requerido

**Query params:**
| Param | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| page | int | 1 | Página de resultados |
| limit | int | 20 | Resultados por página (máx 50) |
| discipline_id | int | null | Filtro por disciplina |
| technique_id | int | null | Filtro por técnica |

**Response 200:**
```json
{
  "items": [
    {
      "id": 42,
      "technique_display_name": "Jab",
      "discipline_name": "Boxeo",
      "global_score": 73.5,
      "status": "completed",
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

### GET /analysis/{analysis_id}

**Auth:** Bearer requerido (propietario del análisis o instructor con el alumno en un grupo)

**Response 200:** AnalysisDetailResponse (mismo schema que POST /analysis response)

**Errores:** 404 (no existe), 403 (no tiene acceso)

---

### GET /analysis/compare

**Auth:** Bearer requerido

**Query params:** `id1: int` (requerido), `id2: int` (requerido)

**Validación:** Ambos análisis deben pertenecer al usuario autenticado y ser de la misma técnica.

**Response 200:**
```json
{
  "analysis_1": { "...AnalysisDetailResponse..." },
  "analysis_2": { "...AnalysisDetailResponse..." },
  "score_difference": 12.5,
  "improved_joints": ["right_elbow"],
  "regressed_joints": [],
  "improved": true
}
```

**Errores:** 400 (técnicas distintas o análisis de usuarios distintos), 404, 403

---

### GET /analysis/{analysis_id}/download/overlay

**Auth:** Bearer requerido

**Response 200:** `FileResponse` con `media_type="video/mp4"` y `Content-Disposition: attachment`

**Errores:** 404 (análisis no completado o sin overlay generado)

---

### GET /analysis/{analysis_id}/download/original

**Auth:** Bearer requerido

**Response 200:** `FileResponse` con el vídeo original (media_type según extensión)

**Errores:** 404

---

### GET /analysis/{analysis_id}/comments

**Auth:** Bearer requerido

**Response 200:**
```json
[
  {
    "id": 1,
    "content": "Buen trabajo, pero deberías extender más el brazo.",
    "author_username": "sensei_marta",
    "author_avatar_url": null,
    "created_at": "2026-05-28T15:00:00"
  }
]
```

---

## ROUTER: /dashboard — Panel de Progreso

### GET /dashboard/me

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
  "xp_next_belt_name": "naranja",
  "current_streak": 5,
  "max_streak": 12,
  "streak_shields": 1,
  "recent_badges": [
    { "badge_id": 1, "display_name": "Primer Golpe", "icon_name": "fist", "level": "bronze", "earned_at": "2026-05-28T10:00:00" }
  ],
  "recent_analyses": [
    { "id": 42, "technique_display_name": "Jab", "discipline_name": "Boxeo", "global_score": 73.5, "created_at": "2026-05-28T10:00:00" }
  ]
}
```

---

### GET /dashboard/me/progress

**Auth:** Bearer requerido

**Query params:**
| Param | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| discipline_id | int | null | Filtro por disciplina (null = todas) |
| days | int | 30 | Número de días hacia atrás (30, 60, 90) |

**Response 200:**
```json
{
  "labels": ["2026-05-01", "2026-05-08", "2026-05-15", "2026-05-22"],
  "datasets": [
    {
      "discipline": "Boxeo",
      "discipline_id": 3,
      "color": "#dc2626",
      "data": [65.0, 68.5, 71.2, 73.5]
    }
  ]
}
```

---

### GET /dashboard/me/heatmap

**Auth:** Bearer requerido

**Response 200:**
```json
{
  "data": [
    { "date": "2026-05-28", "count": 3 },
    { "date": "2026-05-27", "count": 1 },
    { "date": "2026-05-25", "count": 2 }
  ]
}
```

> Retorna solo los días con al menos 1 análisis, para los últimos 90 días.

---

## ROUTER: /gamification — Sistema de Progresión

### GET /gamification/badges

**Auth:** Bearer requerido

**Response 200:**
```json
[
  {
    "id": 1, "name": "first_analysis", "display_name": "Primer Golpe",
    "description": "Realiza tu primer análisis",
    "level": "bronze", "icon_name": "fist", "xp_reward": 50
  }
]
```

---

### GET /gamification/me/badges

**Auth:** Bearer requerido

**Response 200:**
```json
[
  {
    "badge_id": 1, "display_name": "Primer Golpe",
    "icon_name": "fist", "level": "bronze", "xp_reward": 50,
    "earned_at": "2026-05-28T10:00:00"
  }
]
```

---

### GET /gamification/ranking

**Auth:** Bearer requerido

**Query params:**
| Param | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| page | int | 1 | Página |
| limit | int | 50 | Resultados por página |
| discipline_id | int | null | Ranking por disciplina (null = XP global) |

**Response 200:**
```json
{
  "items": [
    {
      "rank": 1, "user_id": 5, "username": "fighter_mx",
      "full_name": "Miguel Hernández", "belt_level": "negro",
      "xp": 15000, "average_score": 88.5, "avatar_url": null
    }
  ],
  "my_rank": 12,
  "total_users": 150
}
```

---

### POST /gamification/me/buy-shield

**Auth:** Bearer requerido

**Request body:** (vacío)

**Response 200:** `{ "message": "Escudo de racha comprado", "shields_remaining": 2, "xp_remaining": 720 }`

**Errores:** 400 (XP insuficiente — cuesta 100 XP)

---

### POST /gamification/me/use-shield

**Auth:** Bearer requerido

**Request body:** (vacío)

**Response 200:** `{ "message": "Escudo activado para hoy", "shields_remaining": 1, "streak_protected": true }`

**Errores:** 400 (no tiene escudos disponibles)

---

## ROUTER: /instructor — Panel de Instructor

### POST /instructor/groups

**Auth:** Bearer requerido — solo `account_type='instructor'`

**Request body:**
```json
{ "name": "Equipo Avanzado 2026", "description": "Grupo de alumnos nivel avanzado" }
```

**Response 201:**
```json
{
  "id": 1, "name": "Equipo Avanzado 2026", "description": "...",
  "invite_code": "FIGHT2026", "member_count": 0,
  "is_active": true, "created_at": "2026-05-28T10:00:00"
}
```

**Errores:** 403 (usuario no es instructor)

---

### GET /instructor/groups

**Auth:** Bearer requerido (instructor)

**Response 200:**
```json
[
  {
    "id": 1, "name": "Equipo Avanzado 2026", "invite_code": "FIGHT2026",
    "member_count": 8, "is_active": true, "created_at": "2026-05-28T10:00:00"
  }
]
```

---

### GET /instructor/groups/{group_id}

**Auth:** Bearer requerido (instructor propietario del grupo)

**Response 200:**
```json
{
  "id": 1, "name": "Equipo Avanzado 2026", "invite_code": "FIGHT2026",
  "members": [
    {
      "student_id": 3, "username": "carlos_fighter",
      "full_name": "Carlos López", "belt_level": "amarillo",
      "xp": 820, "total_analyses": 12,
      "last_activity_date": "2026-05-28", "average_score": 72.3,
      "joined_at": "2026-05-10T09:00:00"
    }
  ]
}
```

---

### POST /instructor/groups/join

**Auth:** Bearer requerido (alumno)

**Request body:** `{ "invite_code": "FIGHT2026" }`

**Response 200:** `{ "message": "Te has unido al grupo Equipo Avanzado 2026 correctamente", "group_name": "Equipo Avanzado 2026" }`

**Errores:** 404 (código no existe), 409 (ya es miembro), 403 (instructores no pueden unirse como alumnos)

---

### GET /instructor/students/{student_id}/analyses

**Auth:** Bearer requerido (instructor que tiene al alumno en algún grupo)

**Query params:** `page=1`, `limit=20`

**Response 200:** Mismo schema que `GET /analysis/me`

**Errores:** 403 (alumno no está en ningún grupo del instructor), 404

---

### GET /instructor/students/{student_id}/stats

**Auth:** Bearer requerido (instructor con acceso)

**Response 200:** Mismo schema que `GET /dashboard/me` pero con los datos del alumno

---

### POST /instructor/analyses/{analysis_id}/comment

**Auth:** Bearer requerido (instructor con acceso al análisis)

**Request body:** `{ "content": "string — mínimo 5 caracteres" }`

**Response 201:**
```json
{
  "id": 1, "content": "Buen progreso en la extensión del codo.",
  "author_username": "sensei_marta", "author_avatar_url": null,
  "created_at": "2026-05-28T15:00:00"
}
```

**Errores:** 403 (no tiene acceso), 404

---

## Resumen de Endpoints

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | /auth/register | No | Registro de usuario |
| POST | /auth/login | No | Login |
| POST | /auth/refresh | No | Renovar access token |
| POST | /auth/forgot-password | No | Recuperar contraseña (mock) |
| GET | /auth/me | Sí | Perfil del usuario autenticado |
| PUT | /users/me | Sí | Actualizar perfil + avatar |
| GET | /users/{id} | Sí | Perfil público de un usuario |
| GET | /disciplines | Sí | Lista de disciplinas |
| GET | /disciplines/{id}/techniques | Sí | Técnicas de una disciplina |
| POST | /analysis | Sí | Subir vídeo y analizarlo |
| GET | /analysis/me | Sí | Historial paginado del usuario |
| GET | /analysis/compare | Sí | Comparar dos análisis |
| GET | /analysis/{id} | Sí | Detalle de un análisis |
| GET | /analysis/{id}/download/overlay | Sí | Descargar vídeo overlay |
| GET | /analysis/{id}/download/original | Sí | Descargar vídeo original |
| GET | /analysis/{id}/comments | Sí | Comentarios de un análisis |
| GET | /dashboard/me | Sí | Dashboard resumen |
| GET | /dashboard/me/progress | Sí | Datos gráfica evolución |
| GET | /dashboard/me/heatmap | Sí | Datos heatmap actividad |
| GET | /gamification/badges | Sí | Catálogo de badges |
| GET | /gamification/me/badges | Sí | Badges del usuario |
| GET | /gamification/ranking | Sí | Ranking global/por disciplina |
| POST | /gamification/me/buy-shield | Sí | Comprar escudo de racha |
| POST | /gamification/me/use-shield | Sí | Usar escudo de racha |
| POST | /instructor/groups | Instructor | Crear grupo |
| GET | /instructor/groups | Instructor | Listar grupos del instructor |
| GET | /instructor/groups/{id} | Instructor | Detalle grupo + miembros |
| POST | /instructor/groups/join | Alumno | Unirse a grupo con código |
| GET | /instructor/students/{id}/analyses | Instructor | Análisis de un alumno |
| GET | /instructor/students/{id}/stats | Instructor | Stats de un alumno |
| POST | /instructor/analyses/{id}/comment | Instructor | Comentar análisis |
| GET | /health | No | Health check |

**Total: 31 endpoints**

✅ ENTREGABLE 3 COMPLETADO
