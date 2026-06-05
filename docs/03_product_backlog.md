# Documento 3: Product Backlog — FighterIA

> **Proyecto:** FighterIA | **Versión:** 1.0 | **Fecha:** 2026-05-28 | **PO:** Agente Product Owner Senior
> **Priorización:** MoSCoW | **Estimación:** Puntos de historia (1=trivial, 3=pequeño, 5=medio, 8=grande, 13=muy grande)

---

## ÉPICA 1 — Autenticación y Gestión de Usuarios

### US-001: Registro de usuario
**Como** visitante de FighterIA
**Quiero** crear una cuenta con mi email, contraseña y tipo de cuenta (Alumno/Instructor)
**Para** acceder a todas las funcionalidades de la plataforma

**Prioridad:** Must Have | **Puntos:** 5

**Criterios de Aceptación:**
- **Dado** que estoy en la página de registro
  **Cuando** introduzco email válido, contraseña (mín. 8 caracteres), nombre de usuario único, nombre completo y selecciono tipo de cuenta
  **Entonces** se crea la cuenta y se me redirige al dashboard con sesión iniciada
- **Dado** que introduzco un email ya registrado
  **Cuando** envío el formulario
  **Entonces** recibo el mensaje "Este email ya está registrado"
- **Dado** que el nombre de usuario ya existe
  **Cuando** envío el formulario
  **Entonces** recibo el mensaje "Este nombre de usuario ya está en uso"
- **Dado** que la contraseña tiene menos de 8 caracteres
  **Cuando** envío el formulario
  **Entonces** veo validación de error antes de enviar

**Definition of Done:**
- [ ] Endpoint POST /auth/register funcional y testeado
- [ ] Contraseña almacenada con hash bcrypt
- [ ] Formulario frontend con validación Zod
- [ ] Token JWT retornado y almacenado en localStorage

---

### US-002: Login de usuario
**Como** usuario registrado
**Quiero** iniciar sesión con mi email y contraseña
**Para** acceder a mi cuenta y mis análisis

**Prioridad:** Must Have | **Puntos:** 3

**Criterios de Aceptación:**
- **Dado** que introduzco credenciales correctas
  **Cuando** envío el formulario de login
  **Entonces** recibo access token + refresh token y se me redirige al dashboard
- **Dado** que introduzco contraseña incorrecta
  **Cuando** envío el formulario
  **Entonces** recibo el mensaje "Email o contraseña incorrectos" (sin especificar cuál)
- **Dado** que mi access token ha expirado
  **Cuando** hago una petición autenticada
  **Entonces** el sistema usa el refresh token para obtener un nuevo access token automáticamente

**Definition of Done:**
- [ ] Endpoint POST /auth/login funcional
- [ ] Endpoint POST /auth/refresh funcional
- [ ] Interceptor de Axios que renueva token automáticamente
- [ ] Redirección a /login si el refresh token también expira

---

### US-003: Edición de perfil
**Como** usuario registrado
**Quiero** editar mi información de perfil
**Para** mantener mis datos actualizados y personalizar mi experiencia

**Prioridad:** Must Have | **Puntos:** 3

**Criterios de Aceptación:**
- **Dado** que accedo a "Mi Perfil"
  **Cuando** edito nombre, bio, gimnasio, ciudad, disciplinas practicadas y guardo
  **Entonces** los cambios se reflejan inmediatamente en el perfil
- **Dado** que subo una foto de perfil
  **Cuando** selecciono un archivo de imagen (JPG/PNG ≤ 2MB)
  **Entonces** la foto se actualiza en el navbar y en el perfil

**Definition of Done:**
- [ ] Endpoint PUT /users/me funcional
- [ ] Subida de imagen con validación de tipo y tamaño
- [ ] Formulario de edición en frontend con previsualización de foto

---

### US-004: Recuperación de contraseña (simulada)
**Como** usuario que olvidó su contraseña
**Quiero** solicitar un enlace de recuperación
**Para** poder recuperar el acceso a mi cuenta

**Prioridad:** Must Have | **Puntos:** 1

**Criterios de Aceptación:**
- **Dado** que introduzco mi email registrado
  **Cuando** solicito recuperación
  **Entonces** veo el mensaje "Si este email está registrado, recibirás instrucciones" (sin enviar email real)

**Definition of Done:**
- [ ] Endpoint POST /auth/forgot-password que responde OK sin lógica de email
- [ ] Formulario en frontend funcional

---

## ÉPICA 2 — Análisis de Vídeo con IA

### US-005: Subida de vídeo y selección de técnica
**Como** usuario autenticado
**Quiero** subir un vídeo y seleccionar la disciplina y técnica que estoy ejecutando
**Para** obtener un análisis biomecánico de mi ejecución

**Prioridad:** Must Have | **Puntos:** 5

**Criterios de Aceptación:**
- **Dado** que accedo a "Nuevo Análisis"
  **Cuando** selecciono disciplina, técnica, y subo un vídeo válido (MP4/MOV/AVI ≤ 60s)
  **Entonces** el vídeo se carga y se inicia el procesamiento con un loader y mensajes motivacionales
- **Dado** que subo un vídeo de más de 60 segundos
  **Cuando** intento enviarlo
  **Entonces** recibo el error "El vídeo no puede superar los 60 segundos"
- **Dado** que subo un formato no soportado
  **Cuando** intento enviarlo
  **Entonces** recibo el error "Formato no soportado. Usa MP4, MOV o AVI"

**Definition of Done:**
- [ ] Endpoint POST /analysis con validación de formato y duración
- [ ] Vídeo original guardado en storage/videos/user_{id}/original/
- [ ] Frontend con selector de disciplina → técnica en cascada
- [ ] Loader con mensajes motivacionales aleatorios durante el procesamiento

---

### US-006: Procesamiento con MediaPipe y generación de overlay
**Como** sistema de análisis
**Quiero** procesar cada frame del vídeo con MediaPipe Pose y generar un vídeo con overlay
**Para** proporcionar retroalimentación visual sobre la técnica del usuario

**Prioridad:** Must Have | **Puntos:** 13

**Criterios de Aceptación:**
- **Dado** que se inicia el procesamiento
  **Cuando** MediaPipe detecta landmarks en los frames
  **Entonces** se calcula el ángulo de las 8 articulaciones principales en cada frame
- **Dado** que se calculan los ángulos
  **Cuando** se comparan con las referencias biomecánicas de la técnica
  **Entonces** cada articulación se marca en verde (dentro del rango) o rojo (fuera del rango)
- **Dado** que se genera el overlay
  **Cuando** se renderiza el vídeo procesado
  **Entonces** el esqueleto se dibuja sobre el vídeo con el valor numérico del ángulo junto a cada articulación
- **Dado** que MediaPipe no detecta ninguna persona en el vídeo
  **Cuando** finaliza el procesamiento
  **Entonces** el análisis se marca como fallido con mensaje "No se detectó ninguna persona en el vídeo"

**Definition of Done:**
- [ ] PoseAnalyzer procesa vídeo frame a frame con OpenCV + MediaPipe
- [ ] Overlay generado con colores semánticos y valores numéricos
- [ ] Vídeo con overlay guardado en storage/videos/user_{id}/overlay/
- [ ] Registro de análisis actualizado con status="completed"

---

### US-007: Puntuación y feedback textual priorizado
**Como** usuario que ha subido un vídeo
**Quiero** recibir una puntuación numérica y una lista de correcciones ordenadas por importancia
**Para** saber exactamente qué debo mejorar y en qué orden

**Prioridad:** Must Have | **Puntos:** 8

**Criterios de Aceptación:**
- **Dado** que el procesamiento se ha completado
  **Cuando** accedo al resultado del análisis
  **Entonces** veo una puntuación global del 0 al 100 y cuatro sub-puntuaciones (potencia, equilibrio, alineación, velocidad)
- **Dado** que hay articulaciones fuera del rango correcto
  **Cuando** se genera el feedback
  **Entonces** cada error tiene: título, descripción biomecánica, ejercicio sugerido para corregirlo
- **Dado** que hay múltiples errores
  **Cuando** se muestra el feedback
  **Entonces** están ordenados de mayor a menor impacto en la técnica

**Definition of Done:**
- [ ] ScoringService calcula las 4 sub-puntuaciones y la global
- [ ] FeedbackService genera texto de corrección por cada articulación fuera de rango
- [ ] Feedback almacenado en tabla analysis_feedback con priority_order
- [ ] Frontend muestra puntuaciones con visualización gráfica y feedback en lista

---

### US-008: Visualización del vídeo con overlay y descarga
**Como** usuario que ha recibido un análisis
**Quiero** ver el vídeo con el overlay de mi técnica y poder descargarlo
**Para** estudiar mi ejecución visualmente y compartirlo con mi instructor

**Prioridad:** Must Have | **Puntos:** 5

**Criterios de Aceptación:**
- **Dado** que accedo al resultado de un análisis completado
  **Cuando** se carga la página
  **Entonces** el vídeo con overlay se reproduce automáticamente en el player del frontend
- **Dado** que quiero conservar el vídeo
  **Cuando** hago clic en "Descargar vídeo analizado"
  **Entonces** se descarga el archivo MP4 con overlay en mi dispositivo
- **Dado** que quiero ver el vídeo original
  **Cuando** hago clic en "Ver vídeo original"
  **Entonces** se reproduce el vídeo sin overlay

**Definition of Done:**
- [ ] Endpoint GET /analysis/{id}/download/overlay retorna el archivo de vídeo
- [ ] Endpoint GET /analysis/{id}/download/original retorna el vídeo original
- [ ] Player de vídeo en frontend (HTML5 video element con controles)

---

## ÉPICA 3 — Historial y Dashboard

### US-009: Historial de análisis
**Como** usuario autenticado
**Quiero** ver una lista de todos mis análisis anteriores
**Para** revisar mi progreso y acceder a análisis específicos

**Prioridad:** Must Have | **Puntos:** 3

**Criterios de Aceptación:**
- **Dado** que accedo a "Mi Historial"
  **Cuando** se carga la página
  **Entonces** veo todos mis análisis ordenados del más reciente al más antiguo, con: miniatura, disciplina, técnica, puntuación global, fecha
- **Dado** que tengo muchos análisis
  **Cuando** llego al final de la página
  **Entonces** se cargan más análisis (paginación o scroll infinito)
- **Dado** que hago clic en un análisis
  **Cuando** se abre el detalle
  **Entonces** veo el resultado completo con overlay y feedback

**Definition of Done:**
- [ ] Endpoint GET /analysis/me con paginación (page, limit)
- [ ] Página de historial en frontend con cards de análisis
- [ ] Navegación al detalle desde cada card

---

### US-010: Modo comparación de análisis
**Como** usuario que ha realizado varios análisis de la misma técnica
**Quiero** comparar dos análisis lado a lado
**Para** ver objetivamente cuánto ha mejorado mi ejecución

**Prioridad:** Should Have | **Puntos:** 5

**Criterios de Aceptación:**
- **Dado** que estoy en el historial
  **Cuando** selecciono dos análisis de la misma técnica y hago clic en "Comparar"
  **Entonces** veo ambos resultados en pantalla dividida con puntuaciones y feedback
- **Dado** que intento comparar análisis de técnicas distintas
  **Cuando** selecciono la segunda técnica
  **Entonces** el sistema me avisa "Solo puedes comparar análisis de la misma técnica"

**Definition of Done:**
- [ ] Endpoint GET /analysis/compare?id1=X&id2=Y
- [ ] Vista de comparación en frontend con layout de dos columnas

---

### US-011: Dashboard personal de progreso
**Como** usuario autenticado
**Quiero** ver un resumen visual de mi actividad y progreso
**Para** tener una visión global de mi evolución como fighter

**Prioridad:** Must Have | **Puntos:** 8

**Criterios de Aceptación:**
- **Dado** que accedo al dashboard
  **Cuando** se carga la página
  **Entonces** veo: total de análisis, mejor puntuación histórica, puntuación media, disciplina favorita, XP actual, cinturón actual, racha actual
- **Dado** que tengo análisis de las últimas semanas
  **Cuando** veo la sección de evolución
  **Entonces** hay una gráfica de líneas que muestra la puntuación media por semana, filtrable por disciplina
- **Dado** que quiero ver mis días de entrenamiento
  **Cuando** veo el calendario heatmap
  **Entonces** los días con análisis están marcados con color intenso según el número de análisis ese día

**Definition of Done:**
- [ ] Endpoint GET /dashboard/me con todos los datos del resumen
- [ ] Endpoint GET /dashboard/me/progress con datos de gráfica
- [ ] Endpoint GET /dashboard/me/heatmap con datos del calendario
- [ ] Dashboard en frontend con componentes de gráfica (Chart.js o Recharts)

---

## ÉPICA 4 — Gamificación

### US-012: Sistema de XP por análisis
**Como** usuario que realiza un análisis
**Quiero** recibir puntos de experiencia (XP) al completarlo
**Para** sentir que mi entrenamiento tiene recompensa y progresar en el sistema de niveles

**Prioridad:** Should Have | **Puntos:** 3

**Criterios de Aceptación:**
- **Dado** que completo un análisis con puntuación 0-49
  **Cuando** finaliza el procesamiento
  **Entonces** recibo 10 XP × multiplicador de dificultad de la técnica
- **Dado** que completo un análisis con puntuación 50-74
  **Cuando** finaliza el procesamiento
  **Entonces** recibo 20 XP × multiplicador
- **Dado** que completo un análisis con puntuación 75-89: recibo 30 XP × multiplicador
- **Dado** que completo un análisis con puntuación 90-99: recibo 45 XP × multiplicador
- **Dado** que obtengo puntuación 100: recibo 60 XP × multiplicador
- **Multiplicadores de dificultad:** easy=1.0, medium=1.5, hard=2.0

**Definition of Done:**
- [ ] GamificationService calcula y otorga XP tras cada análisis
- [ ] XP mostrado en la pantalla de resultados con animación
- [ ] XP total actualizado en el perfil del usuario

---

### US-013: Sistema de cinturones
**Como** usuario que acumula XP
**Quiero** progresar por un sistema de cinturones a medida que mejoro
**Para** tener un indicador visual claro de mi nivel global en la plataforma

**Prioridad:** Should Have | **Puntos:** 3

**Criterios de Aceptación:**
- **Dado** que acumulo suficiente XP para el siguiente cinturón
  **Cuando** el sistema calcula el nivel
  **Entonces** mi cinturón se actualiza automáticamente
- **Dado** que subo de cinturón
  **Cuando** se muestra la pantalla de resultados
  **Entonces** aparece una animación o mensaje especial de felicitación
- **Niveles:** Blanco (0-500) → Amarillo (501-1500) → Naranja (1501-3000) → Verde (3001-5000) → Azul (5001-8000) → Marrón (8001-12000) → Negro (12001+)

**Definition of Done:**
- [ ] Lógica de cálculo de cinturón en GamificationService
- [ ] Cinturón visible en navbar, perfil y dashboard
- [ ] Barra de progreso hacia el siguiente cinturón

---

### US-014: Sistema de badges
**Como** usuario de FighterIA
**Quiero** desbloquear badges al cumplir ciertos hitos
**Para** obtener reconocimiento por mis logros y motivarme a entrenar más

**Prioridad:** Should Have | **Puntos:** 5

**Criterios de Aceptación:**
- **Dado** que realizo mi primer análisis
  **Cuando** se completa
  **Entonces** desbloqueo el badge "Primer Golpe" y recibo notificación visual
- **Badges del MVP:** Primer Golpe, En Racha (7 días), Perfeccionista (100 puntos), Maestro del Muay Thai (50 análisis MT), Guardián del Suelo (50 análisis BJJ), El Cuadrado (50 análisis Boxeo), Polivalente (3 disciplinas en una semana), Sensei (instructor con 5+ alumnos activos), Leyenda (cinturón negro)
- **Dado** que desbloqueo un badge
  **Cuando** aparece la notificación
  **Entonces** veo el nombre del badge, su icono y los XP ganados

**Definition of Done:**
- [ ] Tabla badges con los 9 badges definidos y sus condiciones
- [ ] GamificationService evalúa condiciones de badges tras cada análisis
- [ ] Notificación toast en frontend al desbloquear badge
- [ ] Página de galería de badges con progreso

---

### US-015: Sistema de rachas
**Como** usuario que entrena regularmente
**Quiero** mantener una racha de días consecutivos de entrenamiento
**Para** motivarme a entrenar todos los días

**Prioridad:** Should Have | **Puntos:** 3

**Criterios de Aceptación:**
- **Dado** que realizo al menos un análisis hoy
  **Cuando** es el día siguiente al de mi último análisis
  **Entonces** mi racha aumenta en 1
- **Dado** que no realizo ningún análisis en un día
  **Cuando** pasa ese día sin actividad (y no tengo escudo activo)
  **Entonces** mi racha se reinicia a 0
- **Dado** que tengo XP suficiente para comprar un escudo de racha
  **Cuando** no puedo entrenar ese día y activo el escudo antes de medianoche
  **Entonces** mi racha se mantiene y el escudo se consume
- **Escudo de racha:** cuesta 100 XP, se puede comprar desde el dashboard

**Definition of Done:**
- [ ] Lógica de racha en GamificationService (evaluada en cada análisis)
- [ ] Racha actual y máxima visibles en el dashboard y perfil
- [ ] Sistema de compra y activación de escudo

---

## ÉPICA 5 — Catálogo Biomecánico

### US-016: Catálogo de disciplinas y técnicas
**Como** usuario que va a subir un vídeo
**Quiero** ver las disciplinas y técnicas disponibles para análisis
**Para** seleccionar la correcta antes de subir mi vídeo

**Prioridad:** Must Have | **Puntos:** 1

**Criterios de Aceptación:**
- **Dado** que accedo al selector de "Nuevo Análisis"
  **Cuando** selecciono una disciplina
  **Entonces** el selector de técnica muestra solo las técnicas de esa disciplina
- **Dado** que selecciono una técnica
  **Cuando** veo su información
  **Entonces** veo nombre, descripción y nivel de dificultad

**Definition of Done:**
- [ ] Endpoint GET /disciplines
- [ ] Endpoint GET /disciplines/{id}/techniques
- [ ] Selector en cascada en frontend (disciplina → técnica)

---

## ÉPICA 6 — Modo Instructor

### US-017: Creación y gestión de grupos
**Como** instructor
**Quiero** crear grupos de alumnos con un código de invitación único
**Para** organizar a mis alumnos y hacer seguimiento de su progreso

**Prioridad:** Should Have | **Puntos:** 5

**Criterios de Aceptación:**
- **Dado** que tengo cuenta de tipo Instructor
  **Cuando** accedo al Panel de Instructor y creo un grupo
  **Entonces** se genera un código de invitación único de 8 caracteres
- **Dado** que comparto el código con un alumno
  **Cuando** el alumno introduce el código en "Unirse a grupo"
  **Entonces** el alumno aparece en mi lista del grupo
- **Dado** que accedo al detalle de un grupo
  **Cuando** veo la lista de miembros
  **Entonces** veo: nombre, cinturón, total de análisis, última actividad, puntuación media

**Definition of Done:**
- [ ] Endpoints de gestión de grupos (crear, listar, detalle, unirse con código)
- [ ] Panel de instructor en frontend accesible solo para cuentas Instructor
- [ ] Código de invitación generado con UUID parcial o random alfanumérico

---

### US-018: Seguimiento de alumnos por el instructor
**Como** instructor
**Quiero** ver los análisis y el progreso de cada alumno individualmente
**Para** identificar áreas de mejora y personalizar mi enseñanza

**Prioridad:** Should Have | **Puntos:** 5

**Criterios de Aceptación:**
- **Dado** que hago clic en un alumno de mi grupo
  **Cuando** se carga su perfil de progreso
  **Entonces** veo su dashboard individual: estadísticas, gráfica de evolución, historial de análisis
- **Dado** que veo el análisis de un alumno
  **Cuando** quiero dejar retroalimentación
  **Entonces** puedo añadir un comentario de texto que queda visible para el alumno

**Definition of Done:**
- [ ] Endpoint GET /instructor/students/{id}/stats
- [ ] Endpoint GET /instructor/students/{id}/analyses
- [ ] Endpoint POST /instructor/analyses/{id}/comment
- [ ] Vista de alumno en panel de instructor

---

## Resumen del Backlog por Prioridad

| Prioridad | US | Puntos totales |
|-----------|-----|---------------|
| **Must Have** | US-001 a US-009, US-011, US-016 | 57 puntos |
| **Should Have** | US-010, US-012 a US-015, US-017, US-018 | 29 puntos |
| **Could Have** | Duelos, feed, ranking, exportaciones | — (fuera de sprint) |

**Total MVP Must Have: 57 puntos** | **Total Sprint completo: 86 puntos**

✅ DOCUMENTO COMPLETADO
