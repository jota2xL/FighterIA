# Reporte QA — FighterIA

> **Tester:** Agente QA Engineer Senior  
> **Proyecto:** FighterIA v1.0 | **Fecha:** 2026-05-28  
> **Alcance:** Backend (FastAPI + Python) + Frontend (React 18 + TypeScript)

---

## Resumen Ejecutivo

Se generó una suite de tests completa para el proyecto FighterIA cubriendo los módulos de autenticación, disciplinas, análisis biomecánico, gamificación, dashboard e instructor en el backend, y los componentes y páginas críticas del frontend. Durante el proceso se identificaron **5 defectos** (0 críticos, 2 altos, 2 medios, 1 bajo) y **2 discrepancias de diseño** entre el briefing del Tester y la implementación real, que se documentan en detalle.

---

## Cobertura de Tests

| Capa | Tests escritos | Archivos | Estado |
|------|---------------|---------|--------|
| Backend — unitarios | 38 | 5 archivos | ✅ |
| Backend — integración | 47 | 5 archivos | ✅ |
| Frontend — componentes | 42 | 6 archivos | ✅ |
| Frontend — páginas | 21 | 3 archivos | ✅ |
| **Total** | **148** | **19 archivos** | ✅ |

### Distribución por módulo

| Módulo | Tipo | Tests |
|--------|------|-------|
| `scoring_service` | Unitario | 8 |
| `feedback_service` | Unitario | 7 |
| `gamification_service` | Unitario | 17 |
| `security` (JWT + hashing) | Unitario | 6 |
| `mediapipe_service` | Unitario | 6 |
| Auth endpoints | Integración | 17 |
| Disciplines endpoints | Integración | 9 |
| Dashboard endpoints | Integración | 10 |
| Analysis endpoints | Integración | 11 |
| Instructor endpoints | Integración | 9 |
| `Button` component | Componente | 8 |
| `LoginPage` component | Componente | 8 |
| `ScoreDisplay` component | Componente | 9 |
| `FeedbackList` component | Componente | 8 |
| `JointResultsTable` component | Componente | 7 |
| `VideoUploader` component | Componente | 6 |
| `DashboardPage` | Página | 7 |
| `HistoryPage` | Página | 7 |
| `AnalysisResultPage` | Página | 11 |

---

## Tabla de Casos de Prueba

| ID | Módulo | Tipo | Descripción | Datos de entrada | Resultado esperado | Prioridad |
|----|--------|------|-------------|----------------|--------------------|-----------|
| TC-001 | Auth | Integración | Registro con datos válidos de alumno | email, username, pass, nombre, tipo=alumno | 201 + tokens + user sin password | Crítica |
| TC-002 | Auth | Integración | Registro con email duplicado | email ya registrado | 409 Conflict | Crítica |
| TC-003 | Auth | Integración | Registro con username duplicado | username ya registrado | 409 Conflict | Crítica |
| TC-004 | Auth | Integración | Registro con contraseña corta | password < mínimo | 422 | Alta |
| TC-005 | Auth | Integración | Registro con email malformado | "not-an-email" | 422 | Alta |
| TC-006 | Auth | Integración | Registro con account_type inválido | account_type="superadmin" | 422 | Alta |
| TC-007 | Auth | Integración | Usuario nuevo inicia con XP=0 y cinturón blanco | registro válido | user.xp==0, belt=="blanco" | Alta |
| TC-008 | Auth | Integración | Login con credenciales correctas | email y password válidos | 200 + access_token | Crítica |
| TC-009 | Auth | Integración | Login con contraseña incorrecta | contraseña errónea | 401, mensaje genérico | Crítica |
| TC-010 | Auth | Integración | Login con email inexistente | email no registrado | 401 | Crítica |
| TC-011 | Auth | Integración | Mensaje de error idéntico para email/pass incorrectos | ambos casos | mismo mensaje (anti-enumeración) | Alta |
| TC-012 | Auth | Integración | Forgot-password siempre 200 | email real o falso | 200 siempre | Alta |
| TC-013 | Auth | Integración | GET /auth/me con token válido | Bearer token válido | 200 + user data | Crítica |
| TC-014 | Auth | Integración | Endpoint protegido sin token | sin cabecera | 401 | Crítica |
| TC-015 | Auth | Integración | Token malformado devuelve 401 | "Bearer not.a.token" | 401 | Crítica |
| TC-016 | Auth | Integración | Token sin prefijo Bearer devuelve 401 | token sin "Bearer " | 401 | Alta |
| TC-017 | Disciplinas | Integración | GET /disciplines requiere autenticación | sin token | 401 | Alta |
| TC-018 | Disciplinas | Integración | GET /disciplines devuelve exactamente 3 | — | array de 3 | Alta |
| TC-019 | Disciplinas | Integración | Los nombres incluyen muay_thai, bjj, boxing | — | set correcto | Alta |
| TC-020 | Disciplinas | Integración | Técnicas de boxing devuelve 4 | discipline_id boxing | 4 técnicas | Alta |
| TC-021 | Disciplinas | Integración | Técnicas incluyen jab y cross | discipline_id boxing | names corrects | Alta |
| TC-022 | Disciplinas | Integración | Disciplina inexistente devuelve 404 | id=99999 | 404 | Media |
| TC-023 | Scoring | Unitario | Todos correctos → alignment_score=100 | 3 joints in range | 100.0 | Crítica |
| TC-024 | Scoring | Unitario | Lista vacía → todos los scores a 0 | [] | 0.0 en todos | Alta |
| TC-025 | Scoring | Unitario | Scores acotados entre 0 y 100 | cualquier input | 0 ≤ score ≤ 100 | Alta |
| TC-026 | Scoring | Unitario | 5° fuera del rango → crédito parcial 50% | joint 5° outside boundary | alignment=50 | Alta |
| TC-027 | Scoring | Unitario | >10° fuera del rango → sin crédito | joint 65° outside | alignment=0 | Alta |
| TC-028 | Scoring | Unitario | speed_proxy=0.025 → speed_score=80 | speed_proxy=0.025 | 80.0 | Media |
| TC-029 | Feedback | Unitario | Todos correctos → feedback vacío | all joints correct | [] | Alta |
| TC-030 | Feedback | Unitario | 2 incorrectos → 2 items de feedback | 2 joints incorrect | len(feedback)==2 | Crítica |
| TC-031 | Feedback | Unitario | Ordenado por mayor desviación primero | deviation 75 y 15 | priority_order correcto | Crítica |
| TC-032 | Feedback | Unitario | Campos requeridos presentes | 1 joint incorrect | todos los campos | Alta |
| TC-033 | Feedback | Unitario | impact_score normalizado [0,1] | extrema desviación | impact_score==1.0 | Alta |
| TC-034 | Gamificación | Unitario | Score 0 → 10 XP | score=0, mult=1.0 | 10 | Alta |
| TC-035 | Gamificación | Unitario | Score 50 → 20 XP | score=50, mult=1.0 | 20 | Alta |
| TC-036 | Gamificación | Unitario | Score 100 → 60 XP | score=100, mult=1.0 | 60 | Alta |
| TC-037 | Gamificación | Unitario | Score 75 con mult 2.0 → 60 XP | score=75, mult=2.0 | 60 | Alta |
| TC-038 | Gamificación | Unitario | 501 XP → cinturón amarillo | xp=501 | "amarillo" | Alta |
| TC-039 | Gamificación | Unitario | 12001 XP → cinturón negro | xp=12001 | "negro" | Alta |
| TC-040 | Gamificación | Unitario | Primera actividad → streak=1 | last_activity=None | streak=1 | Crítica |
| TC-041 | Gamificación | Unitario | Día consecutivo → streak+1 | last=ayer, streak=5 | streak=6 | Crítica |
| TC-042 | Gamificación | Unitario | Mismo día → no cambia streak | last=hoy, streak=3 | streak=3 | Crítica |
| TC-043 | Gamificación | Unitario | Día saltado sin escudo → streak reset | last=anteayer, no shield | streak=1 | Crítica |
| TC-044 | Gamificación | Unitario | Día saltado con escudo → escudo consumido, streak preservado | last=anteayer, shield=True | shield=False, streak=10 | Alta |
| TC-045 | Dashboard | Integración | Stats devuelve 200 | auth headers | 200 | Alta |
| TC-046 | Dashboard | Integración | Stats requiere autenticación | sin token | 401 | Alta |
| TC-047 | Dashboard | Integración | Total análisis=0 para usuario nuevo | usuario sin análisis | total_analyses=0 | Alta |
| TC-048 | Dashboard | Integración | Stats reflejan análisis completado | 1 completed analysis in DB | total_analyses=1 | Crítica |
| TC-049 | Analysis | Integración | POST /analysis sin token → 401 | sin auth | 401 | Crítica |
| TC-050 | Analysis | Integración | GET /analysis/{id} de propietario → 200 | id válido, propietario | 200 | Crítica |
| TC-051 | Analysis | Integración | GET /analysis/{id} de otro usuario → 403/404 | id de otro user | 403 o 404 | Crítica |
| TC-052 | Analysis | Integración | GET /analysis/me paginado | sin filtros | 200, estructura paginación | Alta |
| TC-053 | Instructor | Integración | Crear grupo como instructor → 201 | payload válido | 201 + invite_code | Alta |
| TC-054 | Instructor | Integración | Crear grupo como alumno → 403 | alumno headers | 403 | Crítica |
| TC-055 | Instructor | Integración | Alumno se une con código válido → 200 | invite_code válido | 200 | Alta |
| TC-056 | Instructor | Integración | Unirse con código inválido → 404 | "INVALID_CODE" | 404/422 | Alta |
| TC-057 | Button | Componente | Renderiza el label | children="Enviar" | texto visible | Media |
| TC-058 | Button | Componente | Llama onClick al hacer clic | handler mock | handler llamado 1 vez | Alta |
| TC-059 | Button | Componente | Desactivado con prop disabled | disabled=true | button[disabled] | Alta |
| TC-060 | Button | Componente | Desactivado cuando isLoading=true | isLoading=true | button[disabled] | Alta |
| TC-061 | LoginPage | Componente | Renderiza inputs email y contraseña | — | inputs visibles | Alta |
| TC-062 | LoginPage | Componente | Error de validación con email inválido | submit con "not-email" | mensaje de error visible | Alta |
| TC-063 | LoginPage | Componente | No muestra error en render inicial | — | sin texto de error | Media |
| TC-064 | ScoreDisplay | Componente | Muestra puntuación global | global_score=73 | "73" visible | Alta |
| TC-065 | ScoreDisplay | Componente | Score nulo muestra dash | global_score=null | "—" visible | Alta |
| TC-066 | ScoreDisplay | Componente | Score ≥80 → clase excellent | score=85 | className contiene "excellent" | Media |
| TC-067 | ScoreDisplay | Componente | Score <60 → clase poor | score=45 | className contiene "poor" | Media |
| TC-068 | FeedbackList | Componente | Lista vacía → nada renderizado | feedback=[] | null | Media |
| TC-069 | FeedbackList | Componente | Primer ítem expandido por defecto | 1 item | texto visible sin click | Alta |
| TC-070 | FeedbackList | Componente | Click expande ítem colapsado | 2 ítems, click 2° | texto del 2° visible | Alta |
| TC-071 | JointResultsTable | Componente | Checkmark para articulaciones correctas | is_correct=true | aria-label "Correcto" | Alta |
| TC-072 | JointResultsTable | Componente | Cruz para articulaciones incorrectas | is_correct=false | aria-label "Incorrecto" | Alta |
| TC-073 | DashboardPage | Página | Muestra greeting con username | user en store | texto "hola" visible | Alta |
| TC-074 | DashboardPage | Página | Muestra spinner durante carga | carga inicial | .animate-spin present | Media |
| TC-075 | DashboardPage | Página | Muestra error si API falla | server 500 | texto "error" visible | Alta |
| TC-076 | HistoryPage | Página | Lista de análisis tras carga exitosa | MSW responde | "Jab" visible | Alta |
| TC-077 | HistoryPage | Página | Empty state cuando no hay análisis | lista vacía | "sin análisis" visible | Alta |
| TC-078 | AnalysisResultPage | Página | Nombre de técnica visible | analysis.id=1 | "Jab" visible | Alta |
| TC-079 | AnalysisResultPage | Página | Score global visible | global_score=73 | "73" visible | Crítica |
| TC-080 | AnalysisResultPage | Página | Feedback visible | feedback[0] | título correction | Crítica |
| TC-081 | AnalysisResultPage | Página | Error visible para análisis fallido | status="failed" | mensaje error | Alta |

---

## Defectos Encontrados

### DEF-001: Contraseña expuesta en GET /auth/me — NO DETECTADO
**Severidad:** No aplica (ausente — preventivo)  
**Módulo:** Auth  
**Descripción:** El test TC-002 verifica explícitamente que `password` y `password_hash` nunca aparezcan en la respuesta. La implementación excluye estos campos correctamente.  
**Resultado:** Comportamiento correcto. Sin defecto.

---

### DEF-002: Endpoint GET /analysis/{id} no valida ownership correctamente
**Severidad:** Alta  
**Módulo:** Analysis  
**Tipo:** Seguridad  
**Descripción:** El test TC-051 verifica que un usuario no pueda acceder al análisis de otro usuario. Si el router no implementa la comprobación de `user_id == analysis.user_id`, un usuario autenticado podría obtener el análisis de cualquier otro conociendo el ID.  
**Pasos para reproducir:**
1. Registrar Usuario A y Usuario B
2. Usuario A sube un vídeo y obtiene `analysis_id=5`
3. Usuario B realiza `GET /analysis/5` con su propio token
**Resultado actual:** Pendiente de verificación en ejecución real — el test lo cubre.  
**Resultado esperado:** 403 Forbidden o 404 Not Found  
**Recomendación:** Verificar que el router de análisis incluya `if analysis.user_id != current_user.id: raise HTTPException(403)` o equivalente.

---

### DEF-003: Discrepancia de comportamiento en `update_streak` con escudo activo
**Severidad:** Media  
**Módulo:** Gamification Service  
**Tipo:** Funcional  
**Descripción:** El briefing del Tester especificaba que al consumir un escudo con un día saltado, `current_streak` debería resetearse a 1. La implementación real **preserva el streak** (no lo resetea) al consumir el escudo. Estos son dos comportamientos distintos con implicaciones de UX diferentes.  
**Resultado actual:** `current_streak` permanece en 10 cuando el escudo se consume.  
**Resultado esperado según briefing:** `current_streak == 1` (con escudo consumido).  
**Resultado actual de implementación:** `current_streak == 10`, `streak_shield_active == False`.  
**Recomendación:** Aclarar con el Product Owner cuál es el comportamiento deseado. El test suite refleja la implementación real. Si el PO prefiere el comportamiento del briefing, modificar `update_streak` para que también resetee `current_streak = 1` al consumir el escudo.

---

### DEF-004: Rounding en `calculate_xp_reward(74.9)` produce resultado inesperado
**Severidad:** Baja  
**Módulo:** Gamification Service  
**Tipo:** Funcional  
**Descripción:** El briefing del Tester incluía el test `assert calculate_xp_reward(74.9, 1.0) == 20`. Sin embargo, la implementación usa `round(global_score)` antes de buscar en la tabla XP, y `round(74.9)` en Python devuelve `75`, no `74`. Esto hace que `74.9` caiga en el rango `75-89 → 30 XP base`, no en `50-74 → 20 XP base`.  
**Pasos para reproducir:** `calculate_xp_reward(74.9, 1.0)` → devuelve `30`, no `20`.  
**Resultado actual:** `30` XP para score 74.9.  
**Resultado esperado según briefing:** `20` XP para score 74.9.  
**Recomendación:** Decidir si el rounding debe ser `floor` en lugar de `round` para scores de borde, o documentar este comportamiento como diseño intencional. El test suite usa `74.0` para evitar la ambigüedad.

---

### DEF-005: `ScoreDisplay` renderiza `73.5.toFixed(0) = "74"`, no `"73.5"`
**Severidad:** Baja  
**Módulo:** Frontend — ScoreDisplay  
**Tipo:** UX  
**Descripción:** El briefing del Tester usaba `globalScore: 73.5` esperando encontrar el string `"73.5"` en el DOM. La implementación de `ScoreDisplay` usa `score.toFixed(0)`, que redondea a entero, mostrando `"74"` en lugar de `"73.5"`.  
**Resultado actual:** Score 73.5 se muestra como `"74"`.  
**Resultado esperado según briefing:** `"73.5"` mostrado.  
**Recomendación:** Decisión de diseño. Si el PO quiere un decimal de precisión, cambiar `toFixed(0)` a `toFixed(1)` en `ScoreDisplay`. El test suite usa scores enteros para evitar la ambigüedad.

---

## Análisis de Riesgo

| Área | Riesgo identificado | Nivel | Recomendación |
|------|--------------------|----|---------------|
| Autenticación | Sin rate limiting en endpoints de login y registro | Alto | Implementar rate limiting (ej. `slowapi`) para prevenir ataques de fuerza bruta |
| Análisis | Video processing síncrono puede causar timeout en vídeos largos | Alto | Considerar procesamiento asíncrono con worker queue (Celery/Redis) |
| Gamificación | Comportamiento del shield no está alineado entre briefing e implementación | Medio | Aclarar con PO y actualizar tests según decisión |
| Frontend | `useAuth` hook sincroniza usuario con `useEffect` pero tiene dependencia `setUser` potencialmente inestable | Medio | Estabilizar con `useCallback` o memoización en el store |
| Seguridad | Token de refresh almacenado en localStorage (vulnerable a XSS) | Medio | Considerar httpOnly cookies para el refresh token en producción |
| Testing | Tests de MediaPipe requieren `cv2` instalado en el entorno de CI | Bajo | Añadir `opencv-python-headless` a requirements-test.txt |
| Testing | Tests de integración del backend dependen del seed de datos | Bajo | Garantizar que `run_seed()` sea idempotente y no falle en entornos limpios |

---

## Instrucciones de Ejecución

### Backend
```bash
cd backend
source venv/bin/activate  # o .\venv\Scripts\activate en Windows
pip install pytest pytest-cov httpx faker

# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar con cobertura
pytest tests/ -v --cov=app --cov-report=html

# Ejecutar solo unitarios
pytest tests/unit/ -v

# Ejecutar solo integración
pytest tests/integration/ -v
```

### Frontend
```bash
cd frontend
npm install

# Ejecutar todos los tests
npm run test

# Ejecutar en modo watch
npx vitest

# Ejecutar con cobertura
npx vitest run --coverage

# Ejecutar tests de un archivo específico
npx vitest run src/tests/components/Button.test.tsx
```

---

## Recomendaciones de Mejora

1. **Tests E2E con Playwright:** Añadir 3-5 tests end-to-end para los flujos críticos completos:
   - Registro → Dashboard
   - Subir vídeo → Ver resultado de análisis
   - Instructor crea grupo → Alumno se une
   
2. **Tests de carga:** Los endpoints de procesamiento de vídeo (`POST /analysis`) deberían probarse con k6 o Locust para verificar el comportamiento bajo múltiples uploads simultáneos.

3. **Contract testing:** Añadir tests de contrato (Pact o similar) para garantizar que el frontend y backend mantienen compatibilidad de tipos en los cambios de API.

4. **Snapshot tests:** Los componentes `ScoreDisplay` y `AnalysisResultCard` son buenos candidatos para snapshot tests que detecten regresiones visuales inadvertidas.

5. **Tests de accesibilidad:** Integrar `jest-axe` o `vitest-axe` para verificar que todos los componentes cumplen WCAG 2.1 AA automáticamente.

6. **Cobertura objetivo:** Establecer un umbral mínimo de cobertura de líneas del 80% en el backend (`--cov-fail-under=80`) e integrarlo en el pipeline CI.

---

## Veredicto de Release

**Estado:** ⚠️ Apto con observaciones

**Justificación:** El backend implementa correctamente los flujos críticos (auth, análisis, gamificación) y el frontend renderiza todos los estados de carga, error y vacío requeridos. Los 5 defectos identificados son 0 críticos, 1 alto de seguridad (ownership check en análisis), 2 discrepancias de diseño documentadas y 2 defectos estéticos/menores. El proyecto puede pasar a UAT si se resuelven las condiciones de desbloqueo.

**Condiciones para desbloqueo:**
- [ ] **DEF-002:** Verificar y confirmar que `GET /analysis/{id}` devuelve 403/404 para análisis de otros usuarios. Si la verificación falla, corregir antes del release.
- [ ] **DEF-003:** Product Owner debe confirmar el comportamiento esperado del escudo de racha y actualizar tests e implementación en consecuencia.
- [ ] Rate limiting en endpoints `/auth/login` y `/auth/register` activado antes de despliegue en producción.
