# Documento 4: Mapa de Dependencias — FighterIA

> **Proyecto:** FighterIA | **Versión:** 1.0 | **Fecha:** 2026-05-28 | **PO:** Agente Product Owner Senior

---

## 1. Árbol de Dependencias por Módulo

```
ANÁLISIS DE VÍDEO (núcleo del sistema)
├── DEPENDE DE: Autenticación (usuario debe estar logueado)
├── DEPENDE DE: Catálogo de Técnicas (user selecciona técnica antes de subir)
├── DEPENDE DE: Base de Datos Biomecánica (referencias para comparar ángulos)
├── ACTIVA: Sistema de XP (otorga XP tras completar análisis)
│   └── ACTIVA: Sistema de Cinturones (recalcula nivel según XP acumulado)
├── ACTIVA: Sistema de Badges (evalúa condiciones de logros)
├── ACTIVA: Sistema de Rachas (actualiza racha del día)
├── ALIMENTA: Historial de Análisis (guarda el resultado)
├── ALIMENTA: Dashboard (contribuye a estadísticas y gráficas)
└── PERMITE: Modo Instructor (instructor puede ver análisis del alumno)

AUTENTICACIÓN
├── BASE DE TODO: todos los módulos protegidos dependen de ella
└── DEFINE: tipo de cuenta (Alumno vs Instructor) → habilita módulos diferentes

CATÁLOGO (Disciplinas + Técnicas + Referencias Biomecánicas)
├── PRERREQUISITO: debe existir en base de datos antes de cualquier análisis
└── SEED: poblado automáticamente al iniciar el backend por primera vez

GAMIFICACIÓN (XP + Cinturones + Badges + Rachas)
├── DEPENDE DE: Análisis completados (fuente de XP)
├── ALIMENTA: Dashboard (muestra nivel, racha, logros)
└── DEPENDE DE: Escudo de Racha (comprado con XP del propio usuario)

MODO INSTRUCTOR
├── DEPENDE DE: Autenticación con tipo=Instructor
├── DEPENDE DE: Sistema de grupos (alumno debe haber aceptado invitación)
└── DEPENDE DE: Análisis del alumno (debe existir para poder comentar)

DASHBOARD
├── DEPENDE DE: Análisis (datos de progreso)
├── DEPENDE DE: Gamificación (XP, cinturón, racha, badges)
└── REQUIERE: al menos 1 análisis para mostrar datos significativos
```

---

## 2. Matriz de Dependencias entre Módulos

| Módulo | Requiere | Es requerido por |
|--------|---------|------------------|
| **Auth** | — | Análisis, Historial, Dashboard, Gamificación, Instructor |
| **Catálogo** | Seed en BD | Análisis (selección de técnica) |
| **Análisis** | Auth, Catálogo, Refs biomecánicas | Historial, Dashboard, Gamificación, Instructor |
| **Historial** | Auth, Análisis | Dashboard (datos de gráfica) |
| **Dashboard** | Auth, Análisis, Gamificación | — |
| **Gamificación** | Auth, Análisis | Dashboard, Perfil |
| **Instructor** | Auth (tipo Instructor), Grupos, Análisis alumnos | — |

---

## 3. Dependencias Técnicas Críticas

### 3.1 MediaPipe en Windows
- **Riesgo:** MediaPipe puede tener incompatibilidades con versiones específicas de Python/OpenCV en Windows
- **Mitigación:** Dev1 debe validar la instalación en el primer día. Versiones probadas: `mediapipe==0.10.14`, `opencv-python-headless==4.9.0.80`, `Python 3.11`
- **Plan B:** Si MediaPipe falla en Windows, usar `mediapipe-silicon` o downgrade a `0.10.9`

### 3.2 Procesamiento síncrono de vídeo
- **Riesgo:** Un vídeo de 60 segundos puede tardar 2-5 minutos en procesarse. El timeout de HTTP por defecto (30s en muchos proxies) puede cortar la conexión
- **Mitigación:** Configurar timeout explícito en el cliente Axios (300 segundos). El backend no tiene proxy intermedio en localhost, por lo que no debería ser problema
- **Riesgo secundario:** El navegador puede mostrar la página como "no responde" en procesamiento largo
- **Mitigación:** Implementar SSE (Server-Sent Events) o polling del estado del análisis como alternativa si el timeout es un problema en pruebas

### 3.3 Generación de vídeo con overlay (OpenCV VideoWriter)
- **Riesgo:** En Windows, OpenCV VideoWriter puede requerir codecs específicos (H264, XVID). Si el codec no está disponible, el vídeo se genera sin imagen
- **Mitigación:** Dev1 debe usar el codec `mp4v` (MPEG-4) como fallback si H264 no está disponible. Código:
  ```python
  fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # fallback seguro en Windows
  ```

### 3.4 Almacenamiento de vídeos
- **Riesgo:** Las rutas de archivo en Windows usan `\` mientras que Python prefiere `/`
- **Mitigación:** Dev1 debe usar `pathlib.Path` para todas las rutas de archivo, que abstrae el separador del sistema operativo

### 3.5 CORS entre puerto 8000 y 3000
- **Dependencia:** El frontend en localhost:3000 hace peticiones al backend en localhost:8000
- **Configuración requerida:** El backend debe tener CORS configurado para `http://localhost:3000`

---

## 4. Orden de Implementación Recomendado

### Fase 1 — Fundamentos (Día 1)
```
1. Seed de base de datos (disciplinas, técnicas, refs biomecánicas)
2. Modelos SQLAlchemy
3. Auth endpoints (register, login, refresh)
4. CORS + health check
```
**Desbloqueado tras la Fase 1:** Frontend puede implementar login/registro. Dev2 puede trabajar en paralelo con mocks.

### Fase 2 — Core de Negocio (Día 2)
```
1. Servicio de MediaPipe (PoseAnalyzer)
2. Servicio de procesamiento de vídeo (VideoProcessor)
3. Servicio de scoring (ScoringService)
4. Servicio de feedback (FeedbackService)
5. Endpoint POST /analysis
6. Endpoint GET /analysis/{id}
```
**Desbloqueado tras la Fase 2:** El módulo más crítico del sistema está operativo.

### Fase 3 — Historial y Dashboard (Día 3)
```
1. Endpoints de historial (GET /analysis/me)
2. Endpoints de dashboard (GET /dashboard/me y subendpoints)
3. Endpoints de descarga de vídeo
```

### Fase 4 — Gamificación (Día 4)
```
1. GamificationService (XP, cinturones, badges, rachas)
2. Endpoints de gamificación (GET /gamification/*)
3. Integración de gamificación en el flujo de análisis
```

### Fase 5 — Instructor y Pulido (Día 5-6)
```
1. Endpoints de instructor (grupos, comentarios, dashboard alumno)
2. Integración frontend completa
3. Tests
```

---

## 5. Riesgos Identificados y Plan de Contingencia

| ID | Riesgo | Probabilidad | Impacto | Contingencia |
|----|--------|-------------|---------|-------------|
| R1 | MediaPipe no funciona en Windows | Media | Crítico | Downgrade de versión, test en Día 1 |
| R2 | Timeout HTTP en procesamiento largo | Media | Alto | Aumentar timeout en Axios (300s) |
| R3 | Codec de vídeo no disponible en Windows | Alta | Alto | Usar `mp4v` como codec primario |
| R4 | Plazo insuficiente para Should Have | Alta | Medio | Must Have es autosuficiente sin Should Have |
| R5 | Landmarks de MediaPipe con baja visibilidad | Media | Medio | Umbral de visibilidad configurable (0.5 por defecto) |
| R6 | SQLite con acceso concurrente | Baja | Bajo | `check_same_thread=False` en engine |

✅ DOCUMENTO COMPLETADO
