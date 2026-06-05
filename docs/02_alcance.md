# Documento 2: Documento de Alcance — FighterIA

> **Proyecto:** FighterIA | **Versión:** 1.0 | **Fecha:** 2026-05-28 | **PO:** Agente Product Owner Senior

---

## 1. In Scope — Entrega Obligatoria (Must Have)

### 1.1 Módulo de Autenticación
- Registro de usuario con: email, contraseña, nombre de usuario único, nombre completo, tipo de cuenta (Alumno / Instructor)
- Login con email y contraseña, retorna access token JWT + refresh token JWT
- Renovación de token con refresh token (validación por firma JWT, sin persistencia en base de datos)
- Recuperación de contraseña: endpoint que simula el envío de email (responde OK sin enviar nada real)
- Edición de perfil: nombre, bio, gimnasio, ciudad, país, años de experiencia, disciplinas practicadas
- Subida de foto de perfil (archivo de imagen, almacenado en sistema de archivos local)

### 1.2 Módulo de Análisis de Vídeo
- Subida de vídeo: formatos MP4, MOV, AVI, hasta 60 segundos
- El usuario selecciona manualmente la disciplina (Muay Thai / BJJ / Boxeo) y la técnica antes de subir el vídeo
- Procesamiento síncrono: el usuario espera en pantalla con loader y mensajes motivacionales
- Procesamiento frame a frame con MediaPipe Pose (33 landmarks)
- Cálculo de ángulos articulares: codo izquierdo, codo derecho, hombro izquierdo, hombro derecho, cadera izquierda, cadera derecha, rodilla izquierda, rodilla derecha
- Identificación del frame clave de la técnica (frame con mayor extensión del miembro de acción)
- Comparación con base de datos de referencias biomecánicas (datos hardcodeados)
- Generación de overlay: esqueleto completo, articulaciones en verde (correctas) o rojo (incorrectas), valor numérico del ángulo, valor de referencia
- Puntuación global 0-100 y sub-puntuaciones: potencia, equilibrio, alineación, velocidad
- Lista priorizada de correcciones con explicación biomecánica y ejercicio sugerido
- Almacenamiento del vídeo original y del vídeo con overlay en sistema de archivos local
- Descarga del vídeo con overlay por el usuario

### 1.3 Módulo de Historial
- Listado paginado de todos los análisis del usuario ordenados por fecha (más reciente primero)
- Vista de detalle de cada análisis: puntuaciones, feedback, vídeo con overlay, joint results
- Modo comparación: seleccionar dos análisis de la misma técnica y visualizar puntuaciones lado a lado

### 1.4 Dashboard de Progreso
- Resumen de actividad: total de análisis realizados, mejor puntuación, puntuación media, disciplina favorita
- Gráfica de evolución de puntuación por disciplina en el tiempo (últimos 30 días)
- Calendario heatmap de días de entrenamiento (últimos 90 días)
- XP actual y progreso hacia el siguiente cinturón
- Logros recientes desbloqueados (últimos 5)

### 1.5 Sistema de Gamificación
- XP por análisis según puntuación y dificultad de la técnica
- Sistema de cinturones: Blanco → Amarillo → Naranja → Verde → Azul → Marrón → Negro
- Sistema de rachas: contador de días consecutivos de entrenamiento
- Escudo de racha (se gana con XP, protege la racha un día)
- 11 badges definidos con tres niveles (bronce, plata, oro)

### 1.6 Catálogo de Disciplinas y Técnicas
- 3 disciplinas: Muay Thai, BJJ, Boxeo
- 12 técnicas totales (4 por disciplina) con datos biomecánicos de referencia
- Base de datos biomecánica hardcodeada en el seed del proyecto

### 1.7 Modo Instructor
- Panel de instructor para cuentas de tipo Instructor
- Crear grupos de alumnos con código de invitación único
- Ver lista de alumnos del grupo y sus estadísticas
- Ver todos los análisis de un alumno específico
- Dejar comentarios en los análisis de los alumnos
- Ver dashboard de progreso de cada alumno individual

---

## 2. Out of Scope — No se entrega en esta versión

| Funcionalidad | Motivo de exclusión |
|--------------|---------------------|
| Detección automática de disciplina/técnica | Complejidad de clasificación ML, fuera del plazo |
| Sistema de duelos asíncrono | Could Have, plazo insuficiente |
| Feed de comunidad con likes/comentarios | Could Have, plazo insuficiente |
| Ranking global con filtro por país/ciudad | Could Have, derivado de duelos/comunidad |
| Exportación de tarjeta de luchador como imagen | No crítico para MVP |
| Generación de informes PDF | Sustituido por pantalla de resumen |
| Resumen semanal automático por email | Email mockeado, no hay scheduler |
| Notificaciones de racha por email | Email mockeado |
| Sonidos y vibración en móvil | Mejora de experiencia post-MVP |
| Tutorial interactivo de onboarding | Guía textual básica es suficiente |
| Envío real de emails | Funcionalidad simulada |
| Despliegue en servidor | Solo localhost |
| Variación biomecánica por estatura/envergadura | Un único set de referencias por técnica |
| Más de 12 técnicas en la versión inicial | Escalable en futura versión |

---

## 3. Supuestos

| # | Supuesto |
|---|---------|
| S1 | El equipo de desarrollo dispone de Python 3.11+ y Node.js 18+ instalados en Windows |
| S2 | MediaPipe funciona correctamente en Windows con el entorno virtual configurado |
| S3 | Los vídeos de prueba disponibles para testing tienen una sola persona visible |
| S4 | El usuario graba los vídeos desde un ángulo lateral o frontal con suficiente iluminación |
| S5 | SQLite es suficiente para el volumen de datos de una demo académica |
| S6 | Los valores biomecánicos de referencia definidos por el equipo son suficientes para la demo |
| S7 | No hay requisitos de internacionalización ni multiidioma (solo español) |
| S8 | No hay requisitos de accesibilidad WCAG más allá de buenas prácticas semánticas |

---

## 4. Restricciones

| # | Restricción |
|---|------------|
| R1 | Plazo máximo de entrega: 6 días desde el 2026-05-28 |
| R2 | Stack tecnológico fijo: no se puede sustituir ninguna tecnología del stack |
| R3 | Solo funciona en local: localhost:8000 (backend) y localhost:3000 (frontend) |
| R4 | Sin servicios de terceros de pago (no AWS S3, no Sendgrid, no Firebase) |
| R5 | Procesamiento de vídeo síncrono: no se implementa cola de tareas asíncronas |
| R6 | Sin sistema operativo diferente a Windows para el entorno de desarrollo |

---

## 5. Criterios de Aceptación Globales del Producto

El producto se considera entregado satisfactoriamente cuando:

- [ ] Un usuario puede registrarse, iniciar sesión y cerrar sesión
- [ ] Un usuario puede subir un vídeo, seleccionar disciplina y técnica, y recibir un análisis completo
- [ ] El vídeo analizado puede visualizarse con overlay de esqueleto y colores en el frontend
- [ ] El usuario recibe una puntuación numérica y una lista de correcciones priorizadas
- [ ] El historial de análisis es accesible y filtrable
- [ ] El dashboard muestra evolución de puntuación y actividad del usuario
- [ ] El sistema de XP y cinturones se actualiza tras cada análisis
- [ ] Un instructor puede crear un grupo, añadir alumnos y ver sus análisis
- [ ] La aplicación funciona correctamente en Chrome en localhost sin errores de consola críticos
- [ ] El diseño es responsive en móvil (375px) y escritorio (1280px)

✅ DOCUMENTO COMPLETADO
