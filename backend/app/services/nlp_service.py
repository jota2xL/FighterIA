"""
Module: services.nlp_service
Description: Local NLP feedback generation from score dict.
             No external API — pure template composition logic.
             Input:  {"potencia": 0-100, "equilibrio": 0-100,
                      "alineacion": 0-100, "velocidad": 0-100}
             Output: Personalized feedback paragraph (str)
"""
from typing import Dict


# ── Score classification ───────────────────────────────────────────────────────

def _classify(score: float) -> str:
    """Map a numeric score 0-100 to one of 5 performance levels."""
    if score >= 90:
        return "sobresaliente"
    elif score >= 75:
        return "avanzado"
    elif score >= 60:
        return "intermedio"
    elif score >= 40:
        return "basico"
    else:
        return "deficiente"


# ── Dimension display names ────────────────────────────────────────────────────

_DIM_NAMES: Dict[str, str] = {
    "potencia":   "potencia",
    "equilibrio": "equilibrio",
    "alineacion": "alineación corporal",
    "velocidad":  "velocidad de ejecución",
}


# ── Per-dimension level descriptions ──────────────────────────────────────────

_LEVEL_DESC: Dict[str, Dict[str, str]] = {
    "potencia": {
        "sobresaliente": "Tu potencia es excepcional — estás generando la máxima transferencia de energía cinética posible.",
        "avanzado":      "Tu potencia muestra un nivel avanzado, con una cadena cinética bien desarrollada.",
        "intermedio":    "Tu potencia es funcional, aunque hay margen para incrementar la fuerza explosiva.",
        "basico":        "Tu potencia es limitada — la cadena cinética no está completamente conectada.",
        "deficiente":    "Tu potencia necesita trabajo urgente — la generación de fuerza es insuficiente para la técnica.",
    },
    "equilibrio": {
        "sobresaliente": "Tu equilibrio es sobresaliente — mantienes una base sólida en todas las fases del movimiento.",
        "avanzado":      "Tu equilibrio es sólido y te da una base confiable para ejecutar técnicas con consistencia.",
        "intermedio":    "Tu equilibrio es aceptable, pero muestra algunas inestabilidades que conviene corregir.",
        "basico":        "Tu equilibrio requiere atención — la inestabilidad de la base compromete la eficacia de tus técnicas.",
        "deficiente":    "Tu equilibrio es crítico — la inestabilidad severa pone en riesgo la técnica y puede causar lesiones.",
    },
    "alineacion": {
        "sobresaliente": "Tu alineación corporal es impecable — los ángulos articulares están perfectamente calibrados.",
        "avanzado":      "Tu alineación corporal ya se encuentra en un nivel sólido con muy pocas desviaciones.",
        "intermedio":    "Tu alineación es correcta en la mayoría de articulaciones, con algunos ajustes pendientes.",
        "basico":        "Tu alineación muestra desviaciones significativas que reducen la eficiencia del movimiento.",
        "deficiente":    "Tu alineación corporal necesita corrección fundamental — los ángulos articulares están muy fuera de rango.",
    },
    "velocidad": {
        "sobresaliente": "Tu velocidad de ejecución es sobresaliente — el timing y la explosividad son excelentes.",
        "avanzado":      "Tu velocidad es avanzada, con una ejecución fluida y reacciones rápidas.",
        "intermedio":    "Tu velocidad es funcional, aunque desarrollar más explosividad mejoraría el impacto.",
        "basico":        "Tu velocidad es lenta para el nivel de la técnica — la ejecución carece de explosividad.",
        "deficiente":    "Tu velocidad es muy baja — la técnica se ejecuta de forma demasiado pausada para ser efectiva.",
    },
}


# ── Recommendations by dimension and level ────────────────────────────────────

_RECOMMENDATIONS: Dict[str, Dict[str, str]] = {
    "potencia": {
        "sobresaliente": "Mantén tu trabajo de potencia con sesiones de pliometría y trabajo de saco pesado.",
        "avanzado":      "Añade drills de potencia explosiva (clean & press, saltos pliométricos) para superar el siguiente umbral.",
        "intermedio":    "Incorpora trabajo de rotación de cadera con banda elástica y golpes al saco 3 veces por semana.",
        "basico":        "Prioriza ejercicios de cadena cinética completa: sentadillas con rotación, drills de hip drive y trabajo de saco.",
        "deficiente":    "Comienza con ejercicios básicos de fuerza (sentadillas, peso muerto) y drills de coordinación antes de trabajar técnica.",
    },
    "equilibrio": {
        "sobresaliente": "Mantén tu base con trabajo de propiocepción avanzada — tabla de equilibrio y kicks con ojos cerrados.",
        "avanzado":      "Refuerza con ejercicios de equilibrio dinámico en superficies inestables para elevar al siguiente nivel.",
        "intermedio":    "Trabaja el equilibrio estático y dinámico 3 veces por semana con drills en una pierna y sentadillas unilaterales.",
        "basico":        "Incorpora de forma prioritaria trabajo de equilibrio estático (posición de árbol) y dinámico (kicks lentos).",
        "deficiente":    "Enfócate exclusivamente en estabilización de base antes de practicar técnicas completas — consulta a un fisioterapeuta si hay dolor.",
    },
    "alineacion": {
        "sobresaliente": "Mantén los ejercicios de postura y movilidad articular que ya realizas — están funcionando.",
        "avanzado":      "Mantén los ejercicios de postura y usa grabaciones periódicas para detectar pequeñas desviaciones.",
        "intermedio":    "Practica la técnica frente al espejo enfocándote en los ángulos articulares clave y pide feedback al instructor.",
        "basico":        "Dedica sesiones específicas a corrección técnica con el instructor, usando repeticiones lentas y espejo.",
        "deficiente":    "Es necesario trabajo de corrección técnica intensivo — reduce la velocidad, usa pesos ligeros y trabaja con un instructor.",
    },
    "velocidad": {
        "sobresaliente": "Mantén el trabajo de velocidad con sparring técnico y drills de reacción.",
        "avanzado":      "Incorpora drills de velocidad máxima y trabajo de reacción ante estímulos visuales.",
        "intermedio":    "Añade shadowboxing rápido, drills con doble fin y trabajo de explosividad muscular.",
        "basico":        "Trabaja la explosividad con sprints cortos, drills de respuesta rápida y golpes al saco a máxima velocidad.",
        "deficiente":    "Enfócate en mejorar la coordinación y el tiempo de reacción con drills de velocidad progresiva antes de aplicar en técnica.",
    },
}


# ── Composite sentence templates ──────────────────────────────────────────────

_STRENGTH_INTROS = [
    "Tus mayores fortalezas son {strengths}.",
    "{strengths} destacan como tus puntos más fuertes en esta sesión.",
    "En cuanto a fortalezas, {strengths} muestran un rendimiento notable.",
]

_WEAKNESS_INTROS = [
    "Sin embargo, {weaknesses} {verb} atención prioritaria.",
    "El área que requiere trabajo inmediato es {weaknesses}.",
    "Para mejorar, debes enfocarte en {weaknesses}, que {verb} por debajo del nivel esperado.",
]

_NO_WEAKNESS = (
    "No se detectan áreas críticas — tu rendimiento general es muy equilibrado."
)

_NO_STRENGTH = (
    "Esta sesión refleja margen de mejora en todas las dimensiones evaluadas."
)

_OPENING_HIGH   = "Excelente sesión — tu rendimiento general supera el nivel esperado."
_OPENING_MEDIUM = "Buena sesión con resultados sólidos en varias dimensiones."
_OPENING_LOW    = "Tu análisis muestra áreas de mejora claras que, trabajadas con constancia, producirán resultados rápidos."

_CLOSINGS = [
    "Sigue entrenando con consistencia — cada sesión te acerca al siguiente nivel.",
    "La constancia es la clave: mantén el ritmo de entrenamiento y los resultados llegarán.",
    "Recuerda que cada análisis es una oportunidad de aprendizaje — usa este feedback para tu próxima sesión.",
]


# ── Main function ─────────────────────────────────────────────────────────────

def generate_nlp_feedback(scores: Dict[str, float]) -> str:
    """
    Compose a personalized feedback paragraph from score dict.
    Keys expected: potencia, equilibrio, alineacion, velocidad (0-100 each).
    Missing keys default to 0.

    Returns a single string composed of multiple sentences covering:
    1. Opening sentence based on average score
    2. Per-dimension level descriptions
    3. Strengths summary sentence
    4. Weaknesses summary sentence (or positive note if none)
    5. Up to 3 targeted recommendations (weaknesses first)
    6. Motivational closing
    """
    dimensions = ["potencia", "equilibrio", "alineacion", "velocidad"]

    # Normalise scores — clamp to [0, 100]
    normalised = {dim: max(0.0, min(100.0, float(scores.get(dim, 0.0)))) for dim in dimensions}

    classified = {dim: _classify(normalised[dim]) for dim in dimensions}

    avg_score = sum(normalised.values()) / len(dimensions)

    # Categorise dimensions
    strong_dims = [d for d in dimensions if classified[d] in ("avanzado", "sobresaliente")]
    weak_dims   = [d for d in dimensions if classified[d] in ("basico", "deficiente")]
    middle_dims = [d for d in dimensions if d not in strong_dims and d not in weak_dims]

    sentences: list[str] = []

    # 1. Opening sentence based on average
    if avg_score >= 75:
        sentences.append(_OPENING_HIGH)
    elif avg_score >= 50:
        sentences.append(_OPENING_MEDIUM)
    else:
        sentences.append(_OPENING_LOW)

    # 2. Per-dimension level descriptions
    for dim in dimensions:
        sentences.append(_LEVEL_DESC[dim][classified[dim]])

    # 3. Strengths summary
    if strong_dims:
        names = " y ".join(_DIM_NAMES[d] for d in strong_dims)
        idx   = len(strong_dims) % len(_STRENGTH_INTROS)
        sentences.append(_STRENGTH_INTROS[idx].format(strengths=names))
    else:
        sentences.append(_NO_STRENGTH)

    # 4. Weaknesses summary
    if weak_dims:
        names = " y ".join(_DIM_NAMES[d] for d in weak_dims)
        verb  = "requieren" if len(weak_dims) > 1 else "requiere"
        idx   = len(weak_dims) % len(_WEAKNESS_INTROS)
        sentences.append(_WEAKNESS_INTROS[idx].format(weaknesses=names, verb=verb))
    else:
        sentences.append(_NO_WEAKNESS)

    # 5. Recommendations (weaknesses first, then middle, then strong — cap at 3)
    priority_order = weak_dims + middle_dims + strong_dims
    for dim in priority_order[:3]:
        sentences.append(_RECOMMENDATIONS[dim][classified[dim]])

    # 6. Motivational closing (cycle through options based on avg score)
    closing_idx = 0 if avg_score >= 75 else (1 if avg_score >= 50 else 2)
    sentences.append(_CLOSINGS[closing_idx])

    return " ".join(sentences)
