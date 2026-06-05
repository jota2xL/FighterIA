# Reporte de Implementación — Backend FighterIA

> **Autor:** Agente Dev1 — Desarrollador Backend Senior
> **Fecha:** 2026-05-28

---

## Resumen

Se ha implementado el backend completo de FighterIA: una API REST con FastAPI que procesa vídeos de artes marciales con MediaPipe Pose, calcula ángulos articulares, genera vídeos con overlay visual y devuelve puntuación técnica + feedback priorizado. El sistema incluye autenticación JWT, gamificación (XP, cinturones, badges, rachas) y modo instructor con grupos de alumnos.

---

## Decisiones de Implementación

### DI-01: `DeclarativeBase` de SQLAlchemy 2.0
**Decisión:** Se usa `class Base(DeclarativeBase): pass` en lugar de `declarative_base()`.
**Motivo:** SQLAlchemy 2.0 deprecó `declarative_base()`. La nueva API es más limpia y evita warnings en consola.

### DI-02: Importación de modelos en `app/models/__init__.py`
**Decisión:** Todos los modelos se importan en `__init__.py` y ese módulo se importa en `main.py` antes de `create_all()`.
**Motivo:** SQLAlchemy solo crea las tablas que conoce en el momento de llamar a `create_all()`. Sin este import, las tablas de modelos no cargados se omiten silenciosamente.

### DI-03: Orden de rutas en `analysis.py`
**Decisión:** `GET /analysis/me` y `GET /analysis/compare` se definen **antes** de `GET /analysis/{analysis_id}`.
**Motivo:** FastAPI evalúa rutas en orden de declaración. Si `/{analysis_id}` estuviera primero, FastAPI intentaría parsear "me" y "compare" como enteros y lanzaría 422.

### DI-04: `email-validator` añadido a `requirements.txt`
**Decisión:** Se añadió `email-validator==2.1.1` como dependencia explícita.
**Motivo:** Pydantic v2 requiere esta librería para que `EmailStr` funcione. Sin ella el servidor falla al arrancar con un ImportError.

### DI-05: `dashboard_service` como módulo separado
**Decisión:** Se extrajo la lógica del dashboard a `services/dashboard_service.py` además de los mencionados en el briefing.
**Motivo:** El Arquitecto lo referenciaba implícitamente en los routers pero no lo listó explícitamente. Implementar la lógica directamente en el router habría violado el principio de separación de capas.

### DI-06: `UserResponse.model_validate` con normalización de `disciplines`
**Decisión:** Se sobrescribe `model_validate` en `UserResponse` para convertir el campo `disciplines` de JSON string a `List[str]` antes de la validación Pydantic.
**Motivo:** SQLite no tiene tipo array. Las disciplinas se almacenan como `'["boxing","bjj"]'` en la columna. Pydantic necesita recibirlo como lista antes de serializar.

### DI-07: Alias `_BASE_URL` en `analysis_service.py`
**Decisión:** La URL base de los links de descarga se hardcodea como `http://localhost:8000`.
**Motivo:** El proyecto corre exclusivamente en localhost. En producción este valor vendría de `settings`.

---

## Desviaciones del Briefing del Arquitecto

1. **`email-validator` añadido** — dependencia no listada pero necesaria para `EmailStr` en Pydantic v2.
2. **`dashboard_service.py` creado** — el Arquitecto lo referenciaba en routers pero no lo listó en `services/`. Se creó para mantener la separación de capas.
3. **`DeclarativeBase` en lugar de `declarative_base()`** — migración a la API moderna de SQLAlchemy 2.0.

---

## Instrucciones de Ejecución

```bash
# 1. Crear y activar entorno virtual (Windows)
cd backend
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear archivo .env (copiar del ejemplo)
copy .env.example .env
# Editar SECRET_KEY en .env

# 4. Arrancar el servidor
uvicorn app.main:app --reload --port 8000

# El seed se ejecuta automáticamente en el primer arranque.
# Documentación interactiva disponible en: http://localhost:8000/docs
```

---

## Endpoints Disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /auth/register | Registro de usuario |
| POST | /auth/login | Login con email/contraseña |
| POST | /auth/refresh | Renovar access token |
| POST | /auth/forgot-password | Recuperar contraseña (mock) |
| GET | /auth/me | Perfil del usuario autenticado |
| PUT | /users/me | Actualizar perfil + avatar |
| GET | /users/{id} | Perfil público de un usuario |
| GET | /disciplines | Listado de disciplinas |
| GET | /disciplines/{id}/techniques | Técnicas de una disciplina |
| POST | /analysis | Subir vídeo y analizarlo |
| GET | /analysis/me | Historial paginado |
| GET | /analysis/compare | Comparar dos análisis |
| GET | /analysis/{id} | Detalle de un análisis |
| GET | /analysis/{id}/download/overlay | Descargar vídeo con overlay |
| GET | /analysis/{id}/download/original | Descargar vídeo original |
| GET | /analysis/{id}/comments | Comentarios del análisis |
| GET | /dashboard/me | Dashboard resumen |
| GET | /dashboard/me/progress | Datos gráfica de progreso |
| GET | /dashboard/me/heatmap | Datos heatmap de actividad |
| GET | /gamification/badges | Catálogo de badges |
| GET | /gamification/me/badges | Badges del usuario |
| GET | /gamification/ranking | Ranking global |
| POST | /gamification/me/buy-shield | Comprar escudo de racha |
| POST | /gamification/me/use-shield | Usar escudo de racha |
| POST | /instructor/groups | Crear grupo |
| GET | /instructor/groups | Grupos del instructor |
| GET | /instructor/groups/{id} | Detalle de grupo |
| POST | /instructor/groups/join | Unirse a grupo con código |
| GET | /instructor/students/{id}/analyses | Análisis de un alumno |
| GET | /instructor/students/{id}/stats | Stats de un alumno |
| POST | /instructor/analyses/{id}/comment | Comentar análisis |

---

## Notas para el Tester

### Datos necesarios para comenzar
- El seed genera automáticamente: 3 disciplinas, 12 técnicas, ~40 referencias biomecánicas, 7 badges
- No es necesario crear datos manualmente antes de los tests

### Orden de operaciones recomendado para tests de integración
1. `POST /auth/register` → obtener token
2. `GET /disciplines` → obtener IDs de técnicas
3. `POST /analysis` con vídeo MP4 real de 5-10 segundos con una persona visible
4. `GET /analysis/me` → verificar que el historial se actualiza
5. `GET /dashboard/me` → verificar XP y cinturón actualizados

### Casos límite conocidos
- **Vídeo sin persona visible:** retorna HTTP 500 con mensaje descriptivo "No se detectó ninguna persona..."
- **Token expirado:** retorna 401; usar `/auth/refresh` para renovar
- **Instructor intentando unirse a grupo:** retorna 403
- **Alumno intentando crear grupo:** retorna 403
- **Comparar análisis de distinta técnica:** retorna 400
- **Comprar escudo sin XP suficiente:** retorna 400 con mensaje de XP insuficiente
- **El endpoint `/analysis` puede tardar 30-120 segundos** — el Tester debe configurar timeout adecuado en su cliente HTTP

### Consideraciones de MediaPipe en Windows
- Verificar que `mediapipe==0.10.14` y `opencv-python-headless==4.9.0.80` están instalados correctamente
- Si MediaPipe falla al importar, ejecutar: `pip install mediapipe==0.10.14 --no-deps` y luego instalar dependencias manualmente
- El codec `mp4v` usado por OpenCV VideoWriter produce archivos `.mp4` compatibles con todos los navegadores modernos
