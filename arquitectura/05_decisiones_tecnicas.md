# Arquitectura FighterIA — Entregable 5: Decisiones Técnicas Justificadas

> **Autor:** Agente Arquitecto de Software Senior | **Fecha:** 2026-05-28

---

## DT-01: Procesamiento de vídeo síncrono (sin cola de tareas)

**Decisión:** El endpoint `POST /analysis` procesa el vídeo de forma síncrona. El cliente HTTP espera hasta que el análisis completa y recibe el resultado en la misma respuesta.

**Contexto:** Analizar un vídeo de 60 segundos con MediaPipe puede tardar entre 30 y 120 segundos en un CPU local. Este tiempo supera el timeout por defecto de la mayoría de clientes HTTP.

**Alternativas consideradas:**
- Cola de tareas asíncrona (Celery + Redis) → descartada: requiere infraestructura adicional (Redis broker) y polling desde el frontend. Incrementa la complejidad en ~2 días de desarrollo extra.
- ARQ (AsyncIO + Redis) → descartada: misma dependencia en Redis.
- Background tasks de FastAPI → descartada: el cliente no recibe el resultado y necesitaría polling igualmente.

**Justificación:** El plazo de 6 días y el entorno de demo académica (localhost, un usuario concurrente) hacen que la solución síncrona sea completamente adecuada. El riesgo de timeout se mitiga configurando explícitamente el timeout de Axios en el frontend a 300 segundos.

**Consecuencias:**
- El cliente Axios debe configurar `timeout: 300000` (ms)
- El endpoint bloquea el worker de uvicorn durante el procesamiento
- No implementar más de 1 análisis concurrente en demo (no es un requisito)
- Status inicial del análisis = 'pending', se actualiza a 'processing' y 'completed' dentro del mismo request

---

## DT-02: SQLite con SQLAlchemy ORM

**Decisión:** Motor de base de datos SQLite. Archivo de base de datos en `backend/fighterai.db`. ORM SQLAlchemy 2.0 con patrón `sessionmaker` + `Depends(get_db)`.

**Contexto:** El proyecto requiere persistencia de usuarios, análisis, referencias biomecánicas y datos de gamificación.

**Alternativas consideradas:**
- PostgreSQL → descartado: requiere proceso de servidor separado. Innecesariamente complejo para localhost con un usuario.
- MySQL → descartado: mismos inconvenientes que PostgreSQL.
- SQLite con acceso directo (sin ORM) → descartado: el ORM aporta type safety, validación de relaciones y facilita los tests.

**Justificación:** SQLite es un motor embebido que no requiere ningún proceso de servidor externo. Se crea automáticamente al primer arranque. Para una demo local con volumen de datos bajo es más que suficiente.

**Consecuencias:**
- `connect_args={"check_same_thread": False}` obligatorio en el engine para compatibilidad con el servidor async de FastAPI
- Las migraciones se manejan mediante `Base.metadata.create_all()` al arrancar (no se usa Alembic en el MVP)
- El archivo `fighterai.db` debe estar en `.gitignore`
- Si se escala a producción, la migración a PostgreSQL es directa cambiando solo `DATABASE_URL`

---

## DT-03: Codec de vídeo `mp4v` para el overlay generado por OpenCV

**Decisión:** OpenCV `VideoWriter` usará el codec `mp4v` (MPEG-4 Part 2) con extensión `.mp4`. No se usa `H264` ni `avc1`.

**Contexto:** Windows no incluye el codec H264 por defecto en OpenCV headless. Si el codec no está disponible, `VideoWriter.isOpened()` retorna `False` y el vídeo de salida se genera vacío.

**Alternativas consideradas:**
- `H264` → descartado: requiere `openh264` dll o compilar OpenCV con soporte H264. Dependencia frágil en Windows.
- `XVID` → segunda opción viable pero requiere instalación de codec externo en algunos sistemas.
- `mp4v` → seleccionado: disponible nativamente en `opencv-python-headless` sin dependencias externas.

**Justificación:** `mp4v` garantiza que el vídeo se genera correctamente en cualquier Windows sin configuración adicional. El tamaño de archivo es ligeramente mayor que H264 pero irrelevante para vídeos de hasta 60 segundos.

**Consecuencias:**
- Dev1 debe usar `cv2.VideoWriter_fourcc(*'mp4v')` sin excepciones
- Validar con `writer.isOpened()` inmediatamente después de crear el `VideoWriter` y lanzar excepción descriptiva si falla
- El archivo de salida debe tener extensión `.mp4`

---

## DT-04: Rutas de sistema de archivos con `pathlib.Path`

**Decisión:** Todas las operaciones de sistema de archivos (lectura, escritura, construcción de rutas, creación de directorios) usarán exclusivamente `pathlib.Path`.

**Contexto:** Python en Windows usa `\` como separador de rutas mientras que el estándar de Python (y la mayoría de librerías) usa `/`. Mezclar separadores genera bugs sutiles.

**Alternativas consideradas:**
- `os.path` → descartado: API antigua, verbosa y menos robusta ante separadores.
- f-strings con separadores hardcodeados → descartado: causa bugs en Windows.
- `str` con separadores → descartado: idéntico problema.

**Justificación:** `pathlib.Path` abstrae completamente el separador del sistema operativo. `Path("storage") / "videos" / f"user_{id}"` funciona correctamente en Windows y Linux sin cambios.

**Consecuencias:**
- `utils/storage.py` expone solo funciones que retornan `pathlib.Path`
- MediaPipe y OpenCV reciben las rutas como `str(path)` cuando es necesario
- `path.mkdir(parents=True, exist_ok=True)` para crear directorios sin fallar si ya existen

---

## DT-05: JWT sin persistencia de refresh tokens en base de datos

**Decisión:** Los refresh tokens se validan exclusivamente por firma criptográfica (HMAC-SHA256). No se almacena ningún token en base de datos ni hay mecanismo de revocación individual.

**Contexto:** La revocación individual de tokens requiere una tabla de tokens revocados (blacklist) o una tabla de tokens activos, ambas requieren una consulta a BD en cada request.

**Alternativas consideradas:**
- Blacklist en base de datos → descartado: una consulta extra en cada request protegido es innecesaria para demo académica.
- Redis para blacklist → descartado: introduce dependencia en Redis.
- Refresh tokens de un solo uso (rotating tokens) → descartado: complejidad de implementación no justificada para MVP.

**Justificación:** Para un entorno de demo local sin requisitos de seguridad de producción, la validación por firma es suficiente. La expiración corta del access token (60 minutos) mitiga el riesgo.

**Consecuencias:**
- No es posible cerrar sesión de forma definitiva sin cambiar `SECRET_KEY` (se limpia el token en cliente)
- El refresh token es válido hasta su expiración (7 días) salvo que el `SECRET_KEY` cambie
- Documentado como limitación conocida en el README

---

## DT-06: Seed automático en evento `startup` de FastAPI

**Decisión:** La función `run_seed()` se invoca en el evento `@app.on_event("startup")`. La función es idempotente: solo ejecuta si la tabla `disciplines` está vacía.

**Contexto:** Las disciplinas, técnicas y referencias biomecánicas son datos maestros necesarios desde el primer arranque. Sin ellos, el sistema no puede recibir análisis.

**Alternativas consideradas:**
- Script de seed manual → descartado: requiere un paso extra de configuración post-instalación que el equipo puede olvidar.
- Migración Alembic con seed → descartado: Alembic añade complejidad de gestión de versiones no necesaria para MVP.
- Endpoint de admin para crear datos → descartado: innecesariamente complejo.

**Justificación:** El seed automático garantiza que la aplicación funciona desde el primer `uvicorn app.main:app`. La idempotencia (`if count > 0: return`) hace que sea seguro ejecutarlo en cada arranque.

**Consecuencias:**
- El primer arranque es ligeramente más lento (~200ms adicionales)
- Si se modifican los datos del seed, hay que borrar el archivo `fighterai.db` y reiniciar

---

## DT-07: CORS exclusivamente para `localhost:3000`

**Decisión:** `CORSMiddleware` configurado con `allow_origins=["http://localhost:3000"]`. No se usa `allow_origins=["*"]`.

**Contexto:** El frontend corre en puerto 3000. El backend en 8000. Sin CORS, el navegador bloquea las peticiones cross-origin.

**Justificación:** `"*"` está permitido en desarrollo pero es una mala práctica incluirlo en código de demo académica. La configuración explícita demuestra comprensión del mecanismo CORS y es más segura.

**Consecuencias:**
- Si Dev2 cambia el puerto del frontend, debe actualizar `ALLOWED_ORIGINS` en `.env`
- En producción se reemplazaría por el dominio real

---

## DT-08: MediaPipe ejecutado en el backend (no en el frontend)

**Decisión:** Todo el procesamiento de MediaPipe Pose se ejecuta en el backend Python. El frontend solo envía el archivo de vídeo y recibe el resultado procesado.

**Contexto:** MediaPipe puede ejecutarse tanto en navegador (JavaScript) como en servidor (Python). El stack del proyecto especifica MediaPipe en backend.

**Alternativas consideradas:**
- MediaPipe en frontend (JavaScript) → descartado: el briefing del PO especifica explícitamente el stack backend.
- Procesamiento híbrido (landmarks en frontend, scoring en backend) → descartado: añade complejidad de integración.

**Justificación:** El procesamiento en backend Python ofrece mayor control sobre el análisis, mejor acceso a NumPy para cálculos de ángulos, y permite generar el overlay de vídeo con OpenCV. No hay latencia adicional significativa en localhost.

**Consecuencias:**
- El vídeo completo se envía al servidor (hasta 200MB)
- El procesamiento bloquea el worker (DT-01)
- El vídeo con overlay generado se almacena en el servidor y se descarga explícitamente

---

## DT-09: Almacenamiento local de vídeos en estructura `user_{id}/original|overlay/`

**Decisión:** Los vídeos se almacenan en el sistema de archivos local bajo `backend/storage/videos/user_{user_id}/original/` y `backend/storage/videos/user_{user_id}/overlay/`. Sin límite por usuario.

**Contexto:** No hay servicios de almacenamiento en la nube disponibles. El briefing del PO confirma almacenamiento local sin límite para la demo.

**Alternativas consideradas:**
- Base de datos (BLOB) → descartado: SQLite con archivos grandes de vídeo es extremadamente ineficiente.
- Directorio plano (todos en un directorio) → descartado: difícil de gestionar y limpiar por usuario.
- AWS S3 / similar → descartado: dependencia externa de pago, fuera del requisito.

**Justificación:** La estructura por usuario facilita la administración, la limpieza y el acceso. Es la práctica estándar para almacenamiento local de archivos de usuario.

**Consecuencias:**
- La carpeta `storage/` debe estar en `.gitignore`
- Los vídeos no persisten entre instalaciones (comportamiento esperado en demo)
- `utils/storage.py` encapsula toda la lógica de rutas

---

## DT-10: Selección manual de técnica por el usuario (sin detección automática)

**Decisión:** El usuario selecciona la disciplina y la técnica manualmente antes de subir el vídeo. No hay modelo de clasificación automática.

**Contexto:** La detección automática de la técnica ejecutada requeriría entrenar un clasificador sobre landmarks de MediaPipe, lo que implica dataset, entrenamiento y evaluación — mínimo 2-3 semanas de trabajo adicional.

**Alternativas consideradas:**
- Clasificador por reglas (heurísticas de landmarks) → descartado: frágil, requiere mucho tuning y falla ante variaciones de ejecución.
- Modelo preentrenado de clasificación de acciones → descartado: no existen modelos preentrenados específicos para artes marciales con la granularidad requerida.

**Justificación:** El cliente (PO) confirmó explícitamente que la selección manual es aceptable para la entrega académica. Esta decisión reduce significativamente el riesgo del proyecto sin comprometer la funcionalidad de análisis.

**Consecuencias:**
- El usuario debe conocer qué técnica está ejecutando (se asume conocimiento básico de MMAA)
- El selector en cascada (disciplina → técnica) en el frontend debe ser intuitivo
- Se documenta como limitación y trabajo futuro

✅ ENTREGABLE 5 COMPLETADO
