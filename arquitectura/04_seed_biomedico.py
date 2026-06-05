"""
FighterIA — Seed de Base de Datos Biomecánica
Arquitecto: Agente Arquitecto de Software Senior
Fecha: 2026-05-28

Archivo ejecutable como script independiente o llamado desde startup de FastAPI.
Popula: disciplines, techniques, biomechanical_references, badges.
Idempotente: solo ejecuta si disciplines está vacía.

Uso standalone:
    cd backend
    python -m seed.seed_data

Uso desde FastAPI (app/main.py on_event startup):
    from seed.seed_data import run_seed
    run_seed()
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# DATOS DE REFERENCIA BIOMECÁNICA
# Fuente: criterio biomecánico razonable para demo académica.
# Formato: (joint_name, min_angle, max_angle, optimal_angle, weight, description)
# Weight: importancia relativa en el cálculo de puntuación (1.0 = normal, >1 = más importante)
# ---------------------------------------------------------------------------

DISCIPLINES = [
    {
        "name": "muay_thai",
        "display_name": "Muay Thai",
        "description": "Arte marcial tailandés conocido como el Arte de las Ocho Extremidades. "
                       "Usa puños, codos, rodillas y piernas.",
        "icon_name": "muay-thai",
    },
    {
        "name": "bjj",
        "display_name": "BJJ",
        "description": "Jiu-Jitsu Brasileño — arte marcial de lucha en suelo enfocado en "
                       "control posicional y sumisiones.",
        "icon_name": "bjj",
    },
    {
        "name": "boxing",
        "display_name": "Boxeo",
        "description": "Arte del boxeo occidental. Centrado en golpes de puño con posicionamiento "
                       "y defensa precisos.",
        "icon_name": "boxing",
    },
]

# Técnicas por disciplina
# Formato: {name, display_name, description, difficulty, xp_multiplier}
TECHNIQUES_BY_DISCIPLINE = {
    "boxing": [
        {
            "name": "jab",
            "display_name": "Jab",
            "description": "Golpe recto rápido con el brazo delantero. "
                           "Principal herramienta de distancia y setup de combinaciones.",
            "difficulty": "easy",
            "xp_multiplier": 1.0,
        },
        {
            "name": "cross",
            "display_name": "Cross",
            "description": "Golpe recto potente con el brazo trasero acompañado de rotación "
                           "de cadera. Principal generador de potencia.",
            "difficulty": "medium",
            "xp_multiplier": 1.5,
        },
        {
            "name": "hook",
            "display_name": "Hook",
            "description": "Golpe circular con el brazo delantero o trasero a la cabeza o cuerpo. "
                           "Requiere rotación pronunciada de cadera y hombro.",
            "difficulty": "medium",
            "xp_multiplier": 1.5,
        },
        {
            "name": "uppercut",
            "display_name": "Uppercut",
            "description": "Golpe ascendente hacia el mentón. Requiere flexión de rodilla y "
                           "explosión hacia arriba desde las piernas.",
            "difficulty": "hard",
            "xp_multiplier": 2.0,
        },
    ],
    "muay_thai": [
        {
            "name": "jab_mt",
            "display_name": "Jab MT",
            "description": "Jab de Muay Thai con guardia alta. Similar al boxeo pero con "
                           "mayor distancia de guardia.",
            "difficulty": "easy",
            "xp_multiplier": 1.0,
        },
        {
            "name": "roundkick_medio",
            "display_name": "Roundkick Medio",
            "description": "Patada circular al cuerpo (costillas, hígado) con la espinilla. "
                           "Técnica más potente del Muay Thai. Requiere rotación total de cadera.",
            "difficulty": "hard",
            "xp_multiplier": 2.0,
        },
        {
            "name": "teep",
            "display_name": "Teep",
            "description": "Patada frontal de empuje con la planta del pie. "
                           "Herramienta de control de distancia y desequilibrio.",
            "difficulty": "medium",
            "xp_multiplier": 1.5,
        },
        {
            "name": "cross_mt",
            "display_name": "Cross MT",
            "description": "Cross de Muay Thai con rotación de cadera más pronunciada que el "
                           "boxeo. Acompaña con avance del pie trasero.",
            "difficulty": "medium",
            "xp_multiplier": 1.5,
        },
    ],
    "bjj": [
        {
            "name": "armbar",
            "display_name": "Armbar desde Guardia",
            "description": "Palanca de codo ejecutada desde posición de guardia cerrada. "
                           "Requiere control de las caderas y pinzamiento de rodillas.",
            "difficulty": "hard",
            "xp_multiplier": 2.0,
        },
        {
            "name": "closed_guard",
            "display_name": "Guardia Cerrada",
            "description": "Posición de control desde abajo con las piernas cruzadas alrededor "
                           "del torso del oponente. Base del juego de guardia.",
            "difficulty": "easy",
            "xp_multiplier": 1.0,
        },
        {
            "name": "mount",
            "display_name": "Montada",
            "description": "Posición de control superior montando sobre el oponente. "
                           "Dominio posicional con caderas bajas y rodillas en tierra.",
            "difficulty": "medium",
            "xp_multiplier": 1.5,
        },
        {
            "name": "triangle",
            "display_name": "Triángulo",
            "description": "Estrangulamiento con las piernas formando un triángulo alrededor "
                           "del cuello y brazo del oponente.",
            "difficulty": "hard",
            "xp_multiplier": 2.0,
        },
    ],
}

# ---------------------------------------------------------------------------
# REFERENCIAS BIOMECÁNICAS
# Formato: (joint_name, min_angle, max_angle, optimal_angle, weight, description)
# ---------------------------------------------------------------------------
BIOMECHANICAL_REFS: dict[str, list[tuple]] = {

    # -------------------------------------------------------------------------
    # BOXEO
    # -------------------------------------------------------------------------

    "jab": [
        # Extensión completa del brazo delantero (derecho en ortodoxa)
        ("right_elbow", 165.0, 180.0, 175.0, 1.8,
         "Extensión del codo derecho al impacto. Rango corto reduce alcance y potencia."),
        # Hombro delantero elevado para proteger el mentón y proyectar el golpe
        ("right_shoulder", 78.0, 100.0, 88.0, 1.2,
         "Elevación del hombro derecho al extenderse. Debe proyectarse hacia adelante."),
        # Codo de guardia (brazo izquierdo) cerrado protegiendo el mentón
        ("left_elbow", 82.0, 102.0, 90.0, 1.0,
         "Posición del codo de guardia izquierdo. Mantener cerrado protege el mentón."),
        # Rotación mínima de cadera en el jab
        ("hip_rotation_proxy", 8.0, 32.0, 18.0, 0.8,
         "Rotación de cadera en el jab. Leve pero presente para dar dirección al golpe."),
        # Rodilla delantera ligeramente flexionada para base estable
        ("front_knee", 142.0, 168.0, 155.0, 0.7,
         "Flexión de rodilla delantera. Demasiado recta reduce la base de apoyo."),
    ],

    "cross": [
        # Extensión máxima del brazo trasero
        ("right_elbow", 163.0, 180.0, 175.0, 1.8,
         "Extensión del codo trasero al impacto. La extensión completa maximiza el alcance."),
        # Hombro trasero proyectado al frente
        ("right_shoulder", 78.0, 102.0, 90.0, 1.2,
         "El hombro trasero debe proyectarse hacia adelante acompañando el golpe."),
        # Rotación de cadera es la clave del cross — muy importante
        ("hip_rotation_proxy", 33.0, 57.0, 45.0, 2.0,
         "Rotación de cadera en el cross. Es el principal generador de potencia — >60% de la fuerza."),
        # Rodilla trasera extendida con pivote del pie
        ("rear_knee", 152.0, 178.0, 165.0, 1.0,
         "Extensión de rodilla trasera con pivote del pie. La rodilla sigue al pie que pivota."),
    ],

    "hook": [
        # Codo a 90° — fundamental para que el golpe sea circular
        ("right_elbow", 78.0, 102.0, 90.0, 2.0,
         "Ángulo del codo en el hook. 90° es el ángulo biomecánico correcto para la trayectoria circular."),
        # Hombro elevado para que el golpe viaje horizontalmente
        ("right_shoulder", 72.0, 96.0, 84.0, 1.5,
         "Altura del hombro en el hook. Debe estar paralelo al suelo para golpe horizontal."),
        # Rotación de cadera potente
        ("hip_rotation_proxy", 38.0, 62.0, 50.0, 1.8,
         "Rotación de cadera en el hook. Genera la trayectoria circular y la potencia."),
    ],

    "uppercut": [
        # Codo flexionado — NO extendido, el uppercut es un golpe ascendente corto
        ("right_elbow", 68.0, 92.0, 78.0, 2.0,
         "Ángulo de codo en el uppercut. Debe mantenerse flexionado para trayectoria ascendente."),
        # Rodilla delantera flexionada para cargar el golpe desde abajo
        ("front_knee", 118.0, 148.0, 132.0, 1.5,
         "Flexión de rodilla delantera al cargar. La energía sube desde las piernas."),
        # Cadera derecha extendida al subir
        ("right_hip", 148.0, 172.0, 160.0, 1.2,
         "Extensión de cadera derecha al ejecutar. El movimiento de cadera hacia arriba genera potencia."),
    ],

    # -------------------------------------------------------------------------
    # MUAY THAI
    # -------------------------------------------------------------------------

    "jab_mt": [
        ("right_elbow", 163.0, 180.0, 175.0, 1.8,
         "Extensión del codo en el jab MT. Similar al boxeo."),
        ("right_shoulder", 78.0, 102.0, 90.0, 1.2,
         "Proyección del hombro delantero."),
        ("hip_rotation_proxy", 8.0, 30.0, 18.0, 0.8,
         "Rotación de cadera mínima en el jab MT."),
    ],

    "roundkick_medio": [
        # La cadera de la pierna de patada debe elevarse y rotar
        ("kicking_hip", 78.0, 112.0, 95.0, 2.0,
         "Flexión de cadera de la pierna que patea. Determina la altura y trayectoria del kick."),
        # La rodilla se extiende al impacto — espinilla como arma
        ("kicking_knee", 148.0, 178.0, 163.0, 2.0,
         "Extensión de rodilla al impacto. La extensión en el momento correcto maximiza el daño."),
        # Pierna de apoyo ligeramente flexionada para absorber y rotar
        ("support_knee", 132.0, 158.0, 144.0, 1.2,
         "Rodilla de apoyo. Ligera flexión permite la rotación de cadera y absorbe el impacto."),
        # Rotación de cadera es la fuente de potencia del roundkick
        ("hip_rotation_proxy", 43.0, 68.0, 55.0, 1.8,
         "Rotación de cadera. Es la clave de la potencia — la cadera debe 'pasar' al frente."),
    ],

    "teep": [
        # Cadera se flexiona para elevar la rodilla
        ("kicking_hip", 78.0, 102.0, 90.0, 1.8,
         "Flexión de cadera al elevar la rodilla en el teep."),
        # La pierna se extiende completamente al impacto
        ("kicking_knee", 158.0, 180.0, 170.0, 2.0,
         "Extensión completa de rodilla al empujar. La extensión genera el empuje penetrante."),
        # Pierna de apoyo estable
        ("support_knee", 143.0, 168.0, 155.0, 1.0,
         "Rodilla de apoyo en el teep. Mayor extensión que en el roundkick."),
    ],

    "cross_mt": [
        ("right_elbow", 163.0, 180.0, 175.0, 1.8,
         "Extensión del codo en el cross MT."),
        # Rotación más pronunciada que en boxeo
        ("hip_rotation_proxy", 33.0, 57.0, 46.0, 2.0,
         "Rotación de cadera en el cross MT. Más pronunciada que en boxeo estándar."),
    ],

    # -------------------------------------------------------------------------
    # BJJ
    # -------------------------------------------------------------------------

    "armbar": [
        # Las caderas deben elevarse y estar perpendiculares al brazo
        ("hip_flexion", 83.0, 107.0, 95.0, 2.0,
         "Flexión de caderas en el armbar. Las caderas elevadas y perpendiculares maximizan la palanca."),
        # El brazo objetivo debe estar extendido — ahí ocurre la sumisión
        ("target_arm_extension", 163.0, 180.0, 175.0, 2.5,
         "Extensión del brazo objetivo. >170° indica que la articulación está bajo presión máxima."),
        # Las rodillas juntas aprietan el brazo y controlan al oponente
        ("knee_pinch", 78.0, 102.0, 88.0, 1.5,
         "Pinzamiento de rodillas alrededor del brazo objetivo. Controla la rotación y el escape."),
    ],

    "closed_guard": [
        # Caderas elevadas para crear ángulo y dificultar el paso
        ("hip_flexion", 83.0, 112.0, 98.0, 1.5,
         "Flexión de caderas en guardia cerrada. Caderas activas dificultan el paso del oponente."),
        # Rodillas flexionadas con los tobillos cruzados
        ("knee_bend", 98.0, 132.0, 113.0, 1.5,
         "Flexión de rodillas en guardia cerrada. Las piernas forman el 'candado' sobre el oponente."),
    ],

    "mount": [
        # Caderas bajas y extendidas — peso hacia adelante
        ("hip_extension", 153.0, 177.0, 163.0, 1.8,
         "Extensión de caderas en la montada. Caderas bajas aumentan el peso y dificultan el escape."),
        # Rodillas en tierra — base estable
        ("knee_flexion", 83.0, 112.0, 95.0, 1.5,
         "Flexión de rodillas en la montada. Rodillas en tierra dan base y control lateral."),
    ],

    "triangle": [
        # Caderas elevadas para crear el ángulo del estrangulamiento
        ("hip_flexion", 88.0, 118.0, 103.0, 2.0,
         "Flexión de caderas en el triángulo. Las caderas elevadas aplican presión sobre el cuello."),
        # Tobillo de la pierna superior debe estar detrás de la rodilla contraria
        ("ankle_behind_knee", 78.0, 102.0, 88.0, 1.5,
         "Posición del tobillo detrás de la rodilla contraria. Cierra el triángulo correctamente."),
        # El brazo del oponente debe quedar hacia afuera y extendido
        ("target_arm_lock", 158.0, 180.0, 170.0, 2.0,
         "Brazo del oponente en el triángulo. Debe estar hacia afuera y extendido para el triangle correcto."),
    ],
}

# ---------------------------------------------------------------------------
# BADGES
# ---------------------------------------------------------------------------
BADGES = [
    {
        "name": "first_analysis",
        "display_name": "Primer Golpe",
        "description": "Realiza tu primer análisis de técnica",
        "level": "bronze",
        "icon_name": "fist",
        "condition_type": "first_analysis",
        "condition_value": 1,
        "xp_reward": 50,
    },
    {
        "name": "streak_7",
        "display_name": "En Racha",
        "description": "Mantén 7 días consecutivos de entrenamiento",
        "level": "silver",
        "icon_name": "fire",
        "condition_type": "streak_7",
        "condition_value": 7,
        "xp_reward": 150,
    },
    {
        "name": "score_100",
        "display_name": "Perfeccionista",
        "description": "Obtén una puntuación de 100 en cualquier técnica",
        "level": "gold",
        "icon_name": "star",
        "condition_type": "score_100",
        "condition_value": 100,
        "xp_reward": 300,
    },
    {
        "name": "muay_thai_50",
        "display_name": "Maestro del Muay Thai",
        "description": "Analiza 50 técnicas de Muay Thai",
        "level": "gold",
        "icon_name": "shin",
        "condition_type": "muay_thai_50",
        "condition_value": 50,
        "xp_reward": 400,
    },
    {
        "name": "bjj_50",
        "display_name": "Guardián del Suelo",
        "description": "Analiza 50 técnicas de BJJ",
        "level": "gold",
        "icon_name": "mat",
        "condition_type": "bjj_50",
        "condition_value": 50,
        "xp_reward": 400,
    },
    {
        "name": "boxing_50",
        "display_name": "El Cuadrado",
        "description": "Analiza 50 técnicas de Boxeo",
        "level": "gold",
        "icon_name": "glove",
        "condition_type": "boxing_50",
        "condition_value": 50,
        "xp_reward": 400,
    },
    {
        "name": "belt_negro",
        "display_name": "Leyenda",
        "description": "Alcanza el cinturón negro",
        "level": "gold",
        "icon_name": "belt",
        "condition_type": "belt_negro",
        "condition_value": 1,
        "xp_reward": 1000,
    },
]


# ---------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ---------------------------------------------------------------------------

def run_seed() -> None:
    """
    Seed idempotente: solo ejecuta si la tabla disciplines está vacía.
    Crea disciplinas, técnicas, referencias biomecánicas y badges.
    """
    from app.database import SessionLocal
    from app.models.discipline import Discipline, Technique
    from app.models.biomechanical import BiomechanicalReference
    from app.models.gamification import Badge
    from sqlalchemy.orm import Session

    db: Session = SessionLocal()
    try:
        # Guard: idempotent check
        if db.query(Discipline).count() > 0:
            print("[seed] Database already seeded. Skipping.")
            return

        print("[seed] Seeding database...")

        # 1. Disciplines
        discipline_map: dict[str, int] = {}
        for d_data in DISCIPLINES:
            discipline = Discipline(**d_data)
            db.add(discipline)
            db.flush()
            discipline_map[d_data["name"]] = discipline.id
            print(f"[seed]   + Discipline: {d_data['display_name']} (id={discipline.id})")

        # 2. Techniques
        technique_map: dict[str, int] = {}
        for discipline_name, techniques in TECHNIQUES_BY_DISCIPLINE.items():
            disc_id = discipline_map[discipline_name]
            for t_data in techniques:
                technique = Technique(discipline_id=disc_id, **t_data)
                db.add(technique)
                db.flush()
                technique_map[t_data["name"]] = technique.id
                print(f"[seed]     + Technique: {t_data['display_name']} (id={technique.id})")

        # 3. Biomechanical references
        for technique_name, refs in BIOMECHANICAL_REFS.items():
            if technique_name not in technique_map:
                print(f"[seed]   WARNING: technique '{technique_name}' not found in map, skipping refs.")
                continue
            tech_id = technique_map[technique_name]
            for joint_name, min_a, max_a, opt_a, weight, description in refs:
                ref = BiomechanicalReference(
                    technique_id=tech_id,
                    joint_name=joint_name,
                    min_angle=min_a,
                    max_angle=max_a,
                    optimal_angle=opt_a,
                    weight=weight,
                    description=description,
                )
                db.add(ref)
            print(f"[seed]       + {len(refs)} biomechanical refs for '{technique_name}'")

        # 4. Badges
        for b_data in BADGES:
            db.add(Badge(**b_data))
            print(f"[seed]   + Badge: {b_data['display_name']}")

        db.commit()
        print("[seed] Seed completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"[seed] ERROR during seed: {e}")
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# SCRIPT STANDALONE
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import os

    # Add backend root to sys.path if running as script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from app.database import engine, Base
    from app.models import user, discipline, biomechanical, analysis, gamification, instructor  # noqa: F401

    Base.metadata.create_all(bind=engine)
    run_seed()
