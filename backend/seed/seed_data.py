"""
Module: seed.seed_data
Description: Idempotent database seed — populates disciplines, techniques,
             biomechanical references and badges on first startup.
             Safe to call on every application start; exits early if already seeded.

Run standalone:
    cd backend
    python -m seed.seed_data
"""
from __future__ import annotations

# ── Discipline catalog ────────────────────────────────────────────────────
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
        "description": "Jiu-Jitsu Brasileño — arte marcial de lucha en suelo enfocado "
                       "en control posicional y sumisiones.",
        "icon_name": "bjj",
    },
    {
        "name": "boxing",
        "display_name": "Boxeo",
        "description": "Arte del boxeo occidental, centrado en golpes de puño con "
                       "posicionamiento y defensa precisos.",
        "icon_name": "boxing",
    },
]

# ── Technique catalog (keyed by discipline name) ──────────────────────────
TECHNIQUES: dict[str, list[dict]] = {
    "boxing": [
        {"name": "jab",      "display_name": "Jab",      "description": "Golpe recto rápido con el brazo delantero.",                         "difficulty": "easy",   "xp_multiplier": 1.0},
        {"name": "cross",    "display_name": "Cross",    "description": "Golpe recto potente con el brazo trasero y rotación de cadera.",      "difficulty": "medium", "xp_multiplier": 1.5},
        {"name": "hook",     "display_name": "Hook",     "description": "Golpe circular con el brazo delantero o trasero.",                    "difficulty": "medium", "xp_multiplier": 1.5},
        {"name": "uppercut", "display_name": "Uppercut", "description": "Golpe ascendente hacia el mentón, cargado desde las piernas.",        "difficulty": "hard",   "xp_multiplier": 2.0},
    ],
    "muay_thai": [
        {"name": "jab_mt",          "display_name": "Jab MT",          "description": "Jab de Muay Thai con guardia alta.",                                    "difficulty": "easy",   "xp_multiplier": 1.0},
        {"name": "roundkick_medio", "display_name": "Roundkick Medio", "description": "Patada circular al cuerpo con la espinilla.",                           "difficulty": "hard",   "xp_multiplier": 2.0},
        {"name": "teep",            "display_name": "Teep",            "description": "Patada frontal de empuje con la planta del pie.",                       "difficulty": "medium", "xp_multiplier": 1.5},
        {"name": "cross_mt",        "display_name": "Cross MT",        "description": "Cross de Muay Thai con rotación de cadera más pronunciada.",            "difficulty": "medium", "xp_multiplier": 1.5},
    ],
    "bjj": [
        {"name": "armbar",       "display_name": "Armbar desde Guardia", "description": "Palanca de codo ejecutada desde guardia cerrada.",                  "difficulty": "hard",   "xp_multiplier": 2.0},
        {"name": "closed_guard", "display_name": "Guardia Cerrada",      "description": "Posición de control desde abajo con piernas cruzadas.",              "difficulty": "easy",   "xp_multiplier": 1.0},
        {"name": "mount",        "display_name": "Montada",              "description": "Posición de control superior montando sobre el oponente.",            "difficulty": "medium", "xp_multiplier": 1.5},
        {"name": "triangle",     "display_name": "Triángulo",            "description": "Estrangulamiento con las piernas formando un triángulo.",             "difficulty": "hard",   "xp_multiplier": 2.0},
    ],
}

# ── Biomechanical references ──────────────────────────────────────────────
# Format: (joint_name, min_angle, max_angle, optimal_angle, weight, description)
# weight > 1.0 = more influential in the global score
BIOMECHANICAL_REFS: dict[str, list[tuple]] = {
    # ── Boxeo ──────────────────────────────────────────────────────────────
    "jab": [
        ("right_elbow",         165.0, 180.0, 175.0, 1.8, "Full extension of the punching elbow at impact."),
        ("right_shoulder",       78.0, 100.0,  88.0, 1.2, "Forward projection of the punching shoulder."),
        ("left_elbow",           82.0, 102.0,  90.0, 1.0, "Guard elbow position — protects the chin."),
        ("hip_rotation_proxy",    8.0,  32.0,  18.0, 0.8, "Slight hip rotation to give direction to the jab."),
        ("front_knee",          142.0, 168.0, 155.0, 0.7, "Front knee slight bend for stable base."),
    ],
    "cross": [
        ("right_elbow",         163.0, 180.0, 175.0, 1.8, "Full extension of the rear arm at impact."),
        ("right_shoulder",       78.0, 102.0,  90.0, 1.2, "Rear shoulder projected forward."),
        ("hip_rotation_proxy",   33.0,  57.0,  45.0, 2.0, "Hip rotation — generates 60-70% of punch power."),
        ("rear_knee",           152.0, 178.0, 165.0, 1.0, "Rear knee extension with foot pivot."),
    ],
    "hook": [
        ("right_elbow",          78.0, 102.0,  90.0, 2.0, "Elbow at 90° — creates the circular path of the hook."),
        ("right_shoulder",       72.0,  96.0,  84.0, 1.5, "Shoulder parallel to floor for horizontal trajectory."),
        ("hip_rotation_proxy",   38.0,  62.0,  50.0, 1.8, "Hip rotation drives circular path and power."),
    ],
    "uppercut": [
        ("right_elbow",          68.0,  92.0,  78.0, 2.0, "Elbow flexed — not extended; ascending trajectory."),
        ("front_knee",          118.0, 148.0, 132.0, 1.5, "Front knee loaded to charge upward drive."),
        ("right_hip",           148.0, 172.0, 160.0, 1.2, "Hip extension drives the upward punch motion."),
    ],

    # ── Muay Thai ───────────────────────────────────────────────────────────
    "jab_mt": [
        ("right_elbow",         163.0, 180.0, 175.0, 1.8, "Extension of the punching elbow in MT jab."),
        ("right_shoulder",       78.0, 102.0,  90.0, 1.2, "Forward shoulder projection."),
        ("hip_rotation_proxy",    8.0,  30.0,  18.0, 0.8, "Minimal hip rotation in the jab MT."),
    ],
    "roundkick_medio": [
        ("kicking_hip",          78.0, 112.0,  95.0, 2.0, "Hip flexion of kicking leg — determines kick height."),
        ("kicking_knee",        148.0, 178.0, 163.0, 2.0, "Knee extension at impact — maximises shin contact damage."),
        ("support_knee",        132.0, 158.0, 144.0, 1.2, "Support knee slight bend enables hip rotation."),
        ("hip_rotation_proxy",   43.0,  68.0,  55.0, 1.8, "Full hip rotation — key source of roundkick power."),
    ],
    "teep": [
        ("kicking_hip",          78.0, 102.0,  90.0, 1.8, "Hip flexion when raising the knee."),
        ("kicking_knee",        158.0, 180.0, 170.0, 2.0, "Full knee extension at push — generates the push force."),
        ("support_knee",        143.0, 168.0, 155.0, 1.0, "Support knee stable base."),
    ],
    "cross_mt": [
        ("right_elbow",         163.0, 180.0, 175.0, 1.8, "Rear arm extension in MT cross."),
        ("hip_rotation_proxy",   33.0,  57.0,  46.0, 2.0, "More pronounced hip rotation than boxing cross."),
    ],

    # ── BJJ ────────────────────────────────────────────────────────────────
    "armbar": [
        ("hip_flexion",          83.0, 107.0,  95.0, 2.0, "Hips elevated and perpendicular — maximises lever."),
        ("target_arm_extension", 163.0, 180.0, 175.0, 2.5, "Target arm extended — elbow joint under pressure."),
        ("knee_pinch",           78.0, 102.0,  88.0, 1.5, "Knee pinch controls arm rotation and prevents escape."),
    ],
    "closed_guard": [
        ("hip_flexion",          83.0, 112.0,  98.0, 1.5, "Active hips make passing difficult."),
        ("knee_bend",            98.0, 132.0, 113.0, 1.5, "Knee position forms the 'lock' around the opponent."),
    ],
    "mount": [
        ("hip_extension",       153.0, 177.0, 163.0, 1.8, "Low hips and forward — increases weight and control."),
        ("knee_flexion",         83.0, 112.0,  95.0, 1.5, "Knees on mat provide stable base and lateral control."),
    ],
    "triangle": [
        ("hip_flexion",          88.0, 118.0, 103.0, 2.0, "Elevated hips apply pressure to neck."),
        ("ankle_behind_knee",    78.0, 102.0,  88.0, 1.5, "Ankle behind opposite knee closes the triangle."),
        ("target_arm_lock",     158.0, 180.0, 170.0, 2.0, "Target arm out and extended for correct triangle."),
    ],
}

# ── Badge catalog ─────────────────────────────────────────────────────────
BADGES = [
    {"name": "first_analysis", "display_name": "Primer Golpe",        "description": "Realiza tu primer análisis",                                "level": "bronze", "icon_name": "fist",  "condition_type": "first_analysis", "condition_value": 1,   "xp_reward": 50},
    {"name": "streak_7",       "display_name": "En Racha",            "description": "Mantén 7 días consecutivos de entrenamiento",               "level": "silver", "icon_name": "fire",  "condition_type": "streak_7",       "condition_value": 7,   "xp_reward": 150},
    {"name": "score_100",      "display_name": "Perfeccionista",      "description": "Obtén una puntuación de 100 en cualquier técnica",          "level": "gold",   "icon_name": "star",  "condition_type": "score_100",      "condition_value": 100, "xp_reward": 300},
    {"name": "muay_thai_50",   "display_name": "Maestro del Muay Thai","description": "Analiza 50 técnicas de Muay Thai",                         "level": "gold",   "icon_name": "shin",  "condition_type": "muay_thai_50",   "condition_value": 50,  "xp_reward": 400},
    {"name": "bjj_50",         "display_name": "Guardián del Suelo",  "description": "Analiza 50 técnicas de BJJ",                               "level": "gold",   "icon_name": "mat",   "condition_type": "bjj_50",         "condition_value": 50,  "xp_reward": 400},
    {"name": "boxing_50",      "display_name": "El Cuadrado",         "description": "Analiza 50 técnicas de Boxeo",                             "level": "gold",   "icon_name": "glove", "condition_type": "boxing_50",      "condition_value": 50,  "xp_reward": 400},
    {"name": "belt_negro",     "display_name": "Leyenda",             "description": "Alcanza el cinturón negro",                                 "level": "gold",   "icon_name": "belt",  "condition_type": "belt_negro",     "condition_value": 1,   "xp_reward": 1000},
]


# ── Main seed function ────────────────────────────────────────────────────

def run_seed() -> None:
    """
    Populate the database with catalog data.
    Idempotent: exits immediately if any Discipline row already exists.
    """
    from app.database import SessionLocal
    from app.models.discipline import Discipline, Technique
    from app.models.biomechanical import BiomechanicalReference
    from app.models.gamification import Badge
    from sqlalchemy.orm import Session

    db: Session = SessionLocal()
    try:
        if db.query(Discipline).count() > 0:
            return  # already seeded

        print("[seed] Starting database seed...")

        # 1. Disciplines
        discipline_map: dict[str, int] = {}
        for d in DISCIPLINES:
            obj = Discipline(**d)
            db.add(obj)
            db.flush()
            discipline_map[d["name"]] = obj.id
            print(f"[seed]   + Discipline: {d['display_name']} (id={obj.id})")

        # 2. Techniques
        technique_map: dict[str, int] = {}
        for disc_name, techniques in TECHNIQUES.items():
            disc_id = discipline_map[disc_name]
            for t in techniques:
                obj = Technique(discipline_id=disc_id, **t)
                db.add(obj)
                db.flush()
                technique_map[t["name"]] = obj.id

        # 3. Biomechanical references
        ref_count = 0
        for tech_name, refs in BIOMECHANICAL_REFS.items():
            if tech_name not in technique_map:
                print(f"[seed]   WARNING: technique '{tech_name}' not in map — skipping refs")
                continue
            tech_id = technique_map[tech_name]
            for joint_name, min_a, max_a, opt_a, weight, desc in refs:
                db.add(BiomechanicalReference(
                    technique_id=tech_id,
                    joint_name=joint_name,
                    min_angle=min_a,
                    max_angle=max_a,
                    optimal_angle=opt_a,
                    weight=weight,
                    description=desc,
                ))
                ref_count += 1
        print(f"[seed]   + {ref_count} biomechanical references added")

        # 4. Badges
        for b in BADGES:
            db.add(Badge(**b))
        print(f"[seed]   + {len(BADGES)} badges added")

        db.commit()
        print("[seed] Seed completed successfully.")

    except Exception as exc:
        db.rollback()
        print(f"[seed] ERROR during seed: {exc}")
        raise
    finally:
        db.close()


# ── Standalone execution ──────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Ensure all models are registered before create_all
    import app.models  # noqa: F401
    from app.database import engine, Base

    Base.metadata.create_all(bind=engine)
    run_seed()
