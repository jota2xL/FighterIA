# Changelog — FighterIA v2.0.0

## [2.0.0] — 2026-06-05

### Added — Backend (Models)

- **`backend/app/models/crm.py`** — Tres modelos ORM SQLAlchemy: `Gym` (tenant con plan free/pro/enterprise), `Trainer` (vinculación user↔gym con roles coach/head_coach/admin) y `Lead` (pipeline de ventas con estados new/contacted/qualified/converted/lost y fuentes organic/referral/paid_ad/event/direct). Relaciones bidireccionales definidas con `relationship()`.
- **`backend/app/models/blockchain.py`** — Modelo `Certificate` con hash SHA-256 de 64 caracteres, FK única a `analyses.id`, contador `verified_count` y timestamp `issued_at`. Constraint UNIQUE en `analysis_id` garantiza un certificado por análisis.

### Added — Backend (Schemas)

- **`backend/app/schemas/crm.py`** — Schemas Pydantic para CRM: `GymCreate`, `GymUpdate`, `GymOut`; `TrainerCreate`, `TrainerUpdate`, `TrainerOut`; `LeadCreate`, `LeadUpdate`, `LeadOut`; `GymMetricsResponse` (métricas agregadas con `total_trainers`, `total_athletes`, `total_sessions`, `avg_score`, `estimated_revenue`, `leads_in_pipeline`, `leads_converted`). Validación con `EmailStr` y `Field(pattern=...)` en todos los enum fields.
- **`backend/app/schemas/blockchain.py`** — Schemas `CertificateOut` y `CertificateVerifyResponse` (con campo `valid: bool`, certificado opcional y mensaje descriptivo).

### Added — Backend (Services)

- **`backend/app/services/crm_service.py`** — Lógica de negocio CRM: CRUD completo para Gym, Trainer y Lead delegando en el ORM. Función `get_gym_metrics(db, gym_id)` que agrega datos cruzando tablas `gyms`, `trainers`, `users`, `analyses` y `leads`. Revenue estimado calculado como `PLAN_PRICE[plan] × active_trainer_count` (free=0, pro=29.99, enterprise=99.99).
- **`backend/app/services/blockchain_service.py`** — Generación y verificación SHA-256: función `_build_payload()` construye el string canónico `"{id}:{user_id}:{score:.4f}:{completed_at_iso}"`. `get_or_create_certificate()` es idempotente (devuelve el existente si ya fue emitido). `verify_certificate()` recomputa el hash para confirmar integridad e incrementa `verified_count`. Sin dependencias externas — solo stdlib `hashlib`.
- **`backend/app/services/nlp_service.py`** — Generación de feedback textual local sin API externa: función `_classify(score)` mapea 0-100 a cinco niveles (deficiente/básico/intermedio/avanzado/sobresaliente). `generate_nlp_feedback(scores)` compone un párrafo de 7-9 oraciones con apertura contextual, descripción por dimensión, resumen de fortalezas/debilidades, hasta 3 recomendaciones priorizadas y cierre motivacional. Función pura sin efectos secundarios.

### Added — Backend (Routers)

- **`backend/app/routers/crm.py`** — 16 endpoints CRM con prefijo `/crm` y auth JWT requerida en todos. Rutas nested: gyms CRUD en `/crm/gyms/...`, trainers en `/crm/gyms/{gym_id}/trainers/...`, leads en `/crm/gyms/{gym_id}/leads/...`. Paginación `?page&limit` en todos los endpoints GET de listado. Filtros opcionales `?status=&source=` en listado de leads. Endpoint de métricas en `GET /crm/gyms/{gym_id}/metrics`.
- **`backend/app/routers/blockchain.py`** — 2 endpoints con prefijo `/blockchain`. `POST /blockchain/certificates/generate/{analysis_id}` requiere JWT y verifica propiedad del análisis (403 si no es propietario, 404 si no existe, 422 si no está completado). `GET /blockchain/certificates/{hash_value}` es público (sin auth) y siempre devuelve HTTP 200.
- **`backend/app/routers/nlp.py`** — 1 endpoint `POST /nlp/feedback` sin autenticación. Validación de scores en rango [0, 100] mediante `Field(ge=0.0, le=100.0)`. Operación stateless sin acceso a base de datos. Tiempo de respuesta esperado < 5ms.

### Added — Backend (Tests)

- **`backend/tests/unit/test_nlp_service.py`** — Tests unitarios para `generate_nlp_feedback`: cobertura de todos los niveles de clasificación, apertura por rango de media, composición de fortalezas/debilidades, manejo de scores faltantes, función `_classify()` en todos los umbrales.
- **`backend/tests/unit/test_blockchain_service.py`** — Tests unitarios para la lógica SHA-256: determinismo del hash, longitud de 64 caracteres, sensibilidad a cambios en payload, formato hexadecimal, propiedades de colisión.
- **`backend/tests/integration/test_crm.py`** — Tests de integración para los 16 endpoints CRM: ciclo completo de CRUD para Gym, Trainer y Lead; validación de campos enum; respuesta de métricas; paginación y filtros.
- **`backend/tests/integration/test_blockchain.py`** — Tests de integración para generación y verificación de certificados: idempotencia, 403 en análisis ajeno, 422 en análisis no completado, verificación pública, incremento de `verified_count`.
- **`backend/tests/integration/test_nlp.py`** — Tests de integración para el endpoint NLP: scores válidos, scores fuera de rango (422), scores faltantes, respuesta con campo `feedback` de tipo string no vacío.

### Added — Frontend (Pages)

- **`frontend/src/pages/GymManagementPage.tsx`** — Página de gestión de gimnasios: CRUD de gyms con formulario de creación/edición, listado paginado, visualización de plan y datos de contacto.
- **`frontend/src/pages/LeadPipelinePage.tsx`** — Pipeline visual de leads por estado de funnel (new → contacted → qualified → converted/lost) con filtros y formulario de actualización de estado.
- **`frontend/src/pages/BusinessDashboardPage.tsx`** — Dashboard de negocio con métricas agregadas del CRM: revenue estimado, trainers activos, leads en pipeline, tasa de conversión.
- **`frontend/src/pages/CertificatePage.tsx`** — Página de certificado blockchain: muestra el hash SHA-256 generado, permite verificar certificados por hash y visualiza el resultado de la verificación.

### Added — Frontend (Services)

- **`frontend/src/services/crm.service.ts`** — Cliente API para todos los endpoints CRM: funciones tipadas para CRUD de gyms, trainers y leads, y consulta de métricas.
- **`frontend/src/services/blockchain.service.ts`** — Cliente API para generación y verificación de certificados blockchain.
- **`frontend/src/services/nlp.service.ts`** — Cliente API para el endpoint de feedback NLP.

### Added — Frontend (Tests)

- **`frontend/src/tests/pages/GymManagementPage.test.tsx`** — Tests de la página de gestión de gimnasios.
- **`frontend/src/tests/pages/CertificatePage.test.tsx`** — Tests de la página de certificados blockchain.

### Added — Docs

- **`c:\FighterIA\arquitectura\v2.md`** — Documento de arquitectura completo de los tres módulos v2: modelos de datos con tablas detalladas, schemas Pydantic, servicios con lógica de negocio, routers con todos los endpoints, diagrama de relaciones extendido y notas de implementación.

---

### Modified

- **`backend/app/models/__init__.py`** — Añadidos imports de los nuevos modelos `Gym`, `Trainer`, `Lead` (desde `models.crm`) y `Certificate` (desde `models.blockchain`), y sus nombres en `__all__`. Esto permite que `Base.metadata.create_all()` cree automáticamente las 4 tablas nuevas (`gyms`, `trainers`, `leads`, `certificates`) al arrancar el servidor.
- **`backend/app/main.py`** — Registrados los tres routers nuevos con `app.include_router()`: `crm.router` (prefijo `/crm`), `blockchain.router` (prefijo `/blockchain`) y `nlp.router` (prefijo `/nlp`).

---

### Technical Details

- **Python / FastAPI:** fastapi==0.111.0, uvicorn[standard]==0.29.0, pydantic==2.7.1, sqlalchemy==2.0.30
- **React / TypeScript:** react==18.3.1, typescript==5.4.5, vite==5.3.1, tailwindcss==3.4.4
- **SHA-256 hashing:** stdlib `hashlib` — sin dependencias externas. Payload canónico: `"{analysis_id}:{user_id}:{global_score:.4f}:{completed_at_iso}"`.
- **NLP:** lógica interna basada en rangos de score con plantillas de texto — sin API externa, sin modelos de ML. Cinco niveles: deficiente (0-39), básico (40-59), intermedio (60-74), avanzado (75-89), sobresaliente (90-100).
- **Base de datos:** SQLite con 4 tablas nuevas creadas automáticamente vía `create_all()`. FK nuevas: `trainers.gym_id → gyms.id`, `trainers.user_id → users.id`, `leads.gym_id → gyms.id` (nullable), `certificates.analysis_id → analyses.id` (UNIQUE).
- **Tests nuevos v2:** 5 archivos de test (2 unitarios + 3 de integración backend) + 2 archivos de test frontend = **7 archivos de test nuevos**.
- **Backward compatibility:** Cero cambios en archivos v1 existentes (modelos, schemas, routers, servicios). La integración es exclusivamente aditiva.
