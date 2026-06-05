# Documento 1: Product Vision Document — FighterIA

> **Proyecto:** FighterIA | **Versión:** 1.0 | **Fecha:** 2026-05-28 | **PO:** Agente Product Owner Senior

---

## 1. Declaración de Visión

**Para** fighters, alumnos de artes marciales e instructores de todos los niveles,
**que** necesitan análisis técnico preciso de su ejecución y seguimiento de progreso,
**FighterIA** es una plataforma web de entrenamiento inteligente,
**que** analiza vídeos de técnicas marciales con visión por computadora e inteligencia artificial, proporcionando feedback biomecánico detallado, puntuación técnica y un sistema de progresión gamificado,
**a diferencia de** los métodos tradicionales de autoevaluación o la dependencia exclusiva de un instructor presencial,
**nuestra solución** democratiza el acceso a análisis técnico profesional sin importar dónde ni cuándo se entrene.

---

## 2. Objetivos de Negocio

| Objetivo | Indicador de Éxito (KPI) |
|---------|--------------------------|
| Proporcionar análisis biomecánico automatizado y preciso | ≥ 80% de los usuarios considera útil el feedback recibido |
| Motivar la constancia en el entrenamiento | ≥ 60% de usuarios activos realizan ≥ 3 análisis por semana |
| Demostrar el uso de IA agéntica en un contexto académico real | Cobertura completa de todos los módulos del Assignment Brief |
| Entregar una aplicación funcional en 6 días | 100% de los módulos Must Have operativos en la fecha límite |

---

## 3. Usuarios y Personas

### Persona 1 — El Alumno Autónomo
- **Nombre ficticio:** Carlos, 24 años
- **Perfil:** Entrena Muay Thai y Boxeo 4 veces por semana. No siempre tiene instructor disponible.
- **Necesidad principal:** Saber qué está haciendo mal en su técnica sin depender de que alguien le grabe y revise.
- **Frustración actual:** El vídeo que se graba no le dice nada específico. Solo ve que "algo no está bien".
- **Uso esperado de FighterIA:** Sube un vídeo de su roundkick, recibe un análisis con overlay, aprende qué ángulos mejorar y comprueba su progreso semana a semana.

### Persona 2 — El Instructor Digital
- **Nombre ficticio:** Marta, 34 años
- **Perfil:** Profesora de BJJ con 20 alumnos. Imparte clases presenciales y online.
- **Necesidad principal:** Hacer seguimiento del progreso técnico de cada alumno de forma objetiva y documentada.
- **Frustración actual:** No tiene herramientas para mostrar a sus alumnos datos concretos de su evolución.
- **Uso esperado de FighterIA:** Crea grupos, asigna técnicas a practicar, revisa los análisis de sus alumnos y deja comentarios.

### Persona 3 — El Fighter Amater de Competición
- **Nombre ficticio:** Ahmed, 29 años
- **Perfil:** Compite en torneos de Boxeo amateur. Entrena en un gimnasio con pocos recursos.
- **Necesidad principal:** Optimizar técnicas específicas para la competición con datos objetivos.
- **Frustración actual:** Su entrenador no puede prestarle atención individual suficiente durante los sparrings.
- **Uso esperado de FighterIA:** Analiza combinaciones específicas, compara con análisis anteriores y compite en el ranking.

---

## 4. Stakeholders

| Stakeholder | Rol | Interés Principal |
|------------|-----|------------------|
| Cliente / Estudiante universitario | Promotor del proyecto | Entrega académica exitosa en Unit 47 |
| Alumnos de artes marciales | Usuario final primario | Mejorar técnica de forma autónoma |
| Instructores | Usuario final secundario | Gestionar progreso de alumnos |
| Tribunal académico PEARSON HND | Evaluador | Demostración de IA agéntica aplicada |

---

## 5. Propuesta de Valor Única

FighterIA combina tres elementos que no existen juntos en ninguna solución actual del mercado:

1. **Análisis biomecánico milimétrico** con MediaPipe Pose (33 puntos del cuerpo, ángulos articulares en tiempo real)
2. **Overlay visual sobre el propio vídeo** del usuario (verde = correcto, rojo = incorrecto, valores numéricos)
3. **Gamificación orientada a artes marciales** (sistema de cinturones, logros, rachas, duelos)

---

## 6. Restricciones y Supuestos Clave

| Tipo | Descripción |
|------|-------------|
| **Plazo** | 6 días naturales desde la fecha de este documento |
| **Entorno** | Local en Windows (localhost:8000 backend, localhost:3000 frontend) |
| **Stack fijo** | Python + FastAPI + SQLite + MediaPipe + React + Tailwind CSS |
| **Referencias biomecánicas** | Definidas manualmente con criterio razonable para demo académica |
| **Email** | Funcionalidad mockeada (no se envían emails reales) |
| **Almacenamiento** | Sistema de archivos local, sin límite por usuario |
| **Autenticación** | JWT con validación por firma, refresh token sin persistencia en BD |

---

## 7. Módulos del Producto

### Must Have (entrega obligatoria)
- Análisis de vídeo con MediaPipe y overlay visual
- Puntuación técnica y feedback textual priorizado
- Registro y login de usuarios (JWT)
- Historial de análisis del usuario
- Dashboard de progreso personal
- Selección manual de disciplina y técnica

### Should Have (alta prioridad si el tiempo lo permite)
- Sistema de XP y cinturones
- Sistema de badges/logros
- Sistema de rachas diarias
- Modo Instructor básico (grupos, comentarios)
- Modo comparación de dos análisis

### Could Have (baja prioridad)
- Sistema de duelos asíncrono
- Feed de comunidad con likes/comentarios
- Ranking global y por disciplina
- Resumen semanal automático
- Exportación de tarjeta de luchador

---

## 8. Hoja de Ruta de 6 Días

| Día | Foco |
|-----|------|
| **1** | Setup del proyecto, modelos de base de datos, endpoints de autenticación |
| **2** | Procesamiento de vídeo con MediaPipe, generación de overlay, endpoints de análisis |
| **3** | Frontend: auth (login/registro), estructura base, diseño |
| **4** | Frontend: carga de vídeo, visualización de análisis con overlay |
| **5** | Dashboard, historial, gamificación (XP, cinturones, badges) |
| **6** | Integración completa, modo instructor básico, tests, pulido |

✅ DOCUMENTO COMPLETADO
