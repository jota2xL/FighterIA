"""
Module: services.feedback_service
Description: Generates prioritized textual feedback from joint measurement results.
             Only produces feedback for joints outside the correct biomechanical range.
"""
from typing import List, Dict

# ── Feedback templates per joint_name ─────────────────────────────────────
# Each entry: {title, text (with {angle}, {min}, {max} placeholders), biomechanical, exercise}
TEMPLATES: dict[str, dict] = {
    "right_elbow": {
        "title": "Extensión de codo derecho insuficiente",
        "text": "Tu codo derecho alcanza {angle:.0f}° en el momento de impacto, cuando el rango correcto es {min:.0f}°-{max:.0f}°. Esto reduce tu alcance efectivo y la transferencia de fuerza.",
        "biomechanical": "La extensión completa del codo en los golpes maximiza el alcance y la transferencia de energía cinética desde el hombro hasta el puño.",
        "exercise": "Practica golpes al saco lento enfocándote en extender completamente el brazo. Usa un espejo para verificar la extensión final.",
    },
    "left_elbow": {
        "title": "Posición del codo de guardia izquierdo incorrecta",
        "text": "El ángulo de tu codo izquierdo ({angle:.0f}°) está fuera del rango correcto de guardia ({min:.0f}°-{max:.0f}°). Esto expone tu mentón.",
        "biomechanical": "Mantener el codo de guardia en el ángulo correcto protege el mentón y permite reaccionar ante contraataques rápidamente.",
        "exercise": "Shadowboxing frente al espejo con foco en mantener el codo de guardia cerrado. Pide a un compañero que te avise cuando lo bajes.",
    },
    "right_shoulder": {
        "title": "Elevación de hombro derecho fuera de rango",
        "text": "Tu hombro derecho se encuentra a {angle:.0f}° cuando debería estar entre {min:.0f}° y {max:.0f}° para este movimiento.",
        "biomechanical": "La proyección y altura del hombro al golpear determina la trayectoria del impacto y protege la articulación.",
        "exercise": "Trabaja la trayectoria del golpe frente a un espejo a cámara lenta corrigiendo la posición del hombro.",
    },
    "left_shoulder": {
        "title": "Posición del hombro izquierdo incorrecta",
        "text": "Tu hombro izquierdo está a {angle:.0f}°, fuera del rango correcto ({min:.0f}°-{max:.0f}°).",
        "biomechanical": "La posición del hombro de guardia afecta la protección de la barbilla y la capacidad de contraatacar.",
        "exercise": "Drill de guardia frente al espejo: comprueba que el hombro izquierdo esté ligeramente elevado y el mentón protegido.",
    },
    "left_knee": {
        "title": "Flexión de rodilla delantera fuera de rango",
        "text": "La rodilla delantera muestra {angle:.0f}° cuando el rango correcto es {min:.0f}°-{max:.0f}°. Esto afecta tu base y estabilidad.",
        "biomechanical": "La flexión correcta de la rodilla delantera determina la estabilidad, la base de apoyo y la capacidad de generar potencia desde el suelo.",
        "exercise": "Trabaja la postura básica con sentadillas parciales para ganar conciencia propioceptiva de la posición de rodilla.",
    },
    "right_knee": {
        "title": "Flexión de rodilla trasera incorrecta",
        "text": "La rodilla trasera muestra {angle:.0f}° cuando debería estar entre {min:.0f}° y {max:.0f}°.",
        "biomechanical": "La rodilla trasera es el punto de transferencia de la cadena cinética desde el suelo hasta el golpe.",
        "exercise": "Drill de pivote de pie trasero prestando atención a la flexión de rodilla correcta.",
    },
    "front_knee": {
        "title": "Posición de rodilla delantera incorrecta",
        "text": "Tu rodilla delantera alcanza {angle:.0f}°, fuera del rango correcto ({min:.0f}°-{max:.0f}°).",
        "biomechanical": "La rodilla delantera en el ángulo correcto proporciona la base necesaria para una técnica estable y potente.",
        "exercise": "Trabaja la estancia básica frente al espejo corrigiendo la flexión de la rodilla delantera.",
    },
    "rear_knee": {
        "title": "Extensión de rodilla trasera fuera de rango",
        "text": "La rodilla trasera está a {angle:.0f}°, fuera del rango óptimo ({min:.0f}°-{max:.0f}°).",
        "biomechanical": "La rodilla trasera impulsa la rotación de cadera — su posición determina cuánta potencia llega al golpe.",
        "exercise": "Practica el pivote del pie trasero con foco en la extensión de rodilla sincronizada con el giro de cadera.",
    },
    "hip_rotation_proxy": {
        "title": "Rotación de cadera insuficiente",
        "text": "La rotación de cadera estimada es de {angle:.0f}° cuando debería estar entre {min:.0f}° y {max:.0f}°. Esto reduce significativamente la potencia.",
        "biomechanical": "La rotación de cadera es responsable del 60-70% de la potencia en golpes de boxeo y Muay Thai.",
        "exercise": "Drill de rotación de caderas con un palo de madera. Práctica de golpes al saco enfocándote en sentir el giro de cadera antes del impacto.",
    },
    "kicking_hip": {
        "title": "Flexión de cadera en el kick fuera de rango",
        "text": "La cadera de la pierna de patada alcanza {angle:.0f}° cuando el rango correcto es {min:.0f}°-{max:.0f}°.",
        "biomechanical": "La flexión correcta de cadera determina la altura, trayectoria y potencia del kick.",
        "exercise": "Ejercicios de movilidad de cadera. Practica la cámara lenta del kick frente al espejo.",
    },
    "kicking_knee": {
        "title": "Extensión de rodilla en el kick incompleta",
        "text": "Tu rodilla de la pierna de patada alcanza {angle:.0f}° al impacto, cuando debería estar entre {min:.0f}°-{max:.0f}°.",
        "biomechanical": "La extensión de rodilla en el momento del impacto maximiza el daño y la penetración del golpe con la espinilla.",
        "exercise": "Practica el snap de rodilla contra un pad fijo. Usa una banda elástica para trabajar la extensión explosiva.",
    },
    "support_knee": {
        "title": "Posición de la rodilla de apoyo incorrecta",
        "text": "La rodilla de apoyo está a {angle:.0f}°, fuera del rango correcto ({min:.0f}°-{max:.0f}°).",
        "biomechanical": "La ligera flexión de la rodilla de apoyo permite la rotación de cadera y absorbe el impulso del kick.",
        "exercise": "Trabaja el equilibrio en una pierna con leve flexión. Practica el kick a cámara lenta prestando atención a la pierna de apoyo.",
    },
    "hip_flexion": {
        "title": "Flexión de cadera fuera de rango",
        "text": "La flexión de cadera es {angle:.0f}°, cuando el rango correcto es {min:.0f}°-{max:.0f}°.",
        "biomechanical": "En BJJ, la posición de caderas activa determina el control posicional y la eficacia de las sumisiones.",
        "exercise": "Trabaja la movilidad de cadera con ejercicios de hip flexor. Practica la posición con un compañero.",
    },
    "hip_extension": {
        "title": "Extensión de cadera insuficiente",
        "text": "La extensión de cadera muestra {angle:.0f}°, fuera del rango correcto ({min:.0f}°-{max:.0f}°).",
        "biomechanical": "En posiciones de control como la montada, las caderas bajas y extendidas aumentan el peso y dificultan el escape.",
        "exercise": "Drill de montada con foco en bajar y mantener las caderas hacia adelante.",
    },
    "target_arm_extension": {
        "title": "Extensión del brazo objetivo insuficiente",
        "text": "El brazo objetivo está a {angle:.0f}° cuando debería estar entre {min:.0f}°-{max:.0f}° para completar la sumisión.",
        "biomechanical": "En el armbar, el brazo necesita estar extendido para que la palanca actúe sobre el codo correctamente.",
        "exercise": "Practica la posición de armbar con un compañero trabajando el control del brazo y la elevación de caderas.",
    },
    "target_arm_lock": {
        "title": "Posición del brazo objetivo en el triángulo incorrecta",
        "text": "El brazo objetivo está a {angle:.0f}°, fuera del rango correcto ({min:.0f}°-{max:.0f}°).",
        "biomechanical": "El brazo debe estar hacia afuera y extendido para que el triángulo bloquee el flujo de sangre correctamente.",
        "exercise": "Practica el control del brazo en el triángulo con un compañero, asegurándote de aislarlo antes de cerrar.",
    },
    "knee_pinch": {
        "title": "Pinzamiento de rodillas insuficiente",
        "text": "El ángulo de pinzamiento de rodillas es {angle:.0f}°, fuera del rango correcto ({min:.0f}°-{max:.0f}°).",
        "biomechanical": "El pinzamiento de rodillas en el armbar controla la rotación del brazo y evita el escape del oponente.",
        "exercise": "Drill de armbar con foco en mantener las rodillas cerradas alrededor del brazo.",
    },
    "knee_bend": {
        "title": "Flexión de rodilla en guardia incorrecta",
        "text": "La flexión de rodilla es {angle:.0f}°, fuera del rango ({min:.0f}°-{max:.0f}°).",
        "biomechanical": "La posición de rodillas en guardia cerrada forma el 'candado' que controla la distancia con el oponente.",
        "exercise": "Practica la guardia cerrada con un compañero trabajando la tensión activa de las piernas.",
    },
    "knee_flexion": {
        "title": "Flexión de rodilla en montada fuera de rango",
        "text": "La flexión de rodilla es {angle:.0f}°, el rango correcto es {min:.0f}°-{max:.0f}°.",
        "biomechanical": "Las rodillas en tierra y la correcta flexión en la montada dan base estable y control lateral.",
        "exercise": "Drill de montada con foco en mantener las rodillas en tierra y el peso centrado.",
    },
    "ankle_behind_knee": {
        "title": "Posición del tobillo en el triángulo incorrecta",
        "text": "El ángulo del tobillo detrás de la rodilla es {angle:.0f}°, fuera del rango ({min:.0f}°-{max:.0f}°).",
        "biomechanical": "El tobillo debe estar correctamente posicionado detrás de la rodilla contraria para cerrar el triángulo.",
        "exercise": "Practica el cierre del triángulo prestando atención a enganchar el tobillo correctamente.",
    },
}

_DEFAULT_TEMPLATE = {
    "title": "Ángulo articular fuera de rango",
    "text": "El ángulo medido en {joint} es {angle:.0f}°. El rango correcto para esta técnica es {min:.0f}°-{max:.0f}°.",
    "biomechanical": "Los ángulos articulares correctos son fundamentales para la eficiencia biomecánica y la prevención de lesiones.",
    "exercise": "Practica la técnica a cámara lenta frente a un espejo, prestando atención específica a esta articulación.",
}


def generate_feedback(joint_results: List[Dict]) -> List[Dict]:
    """
    Produce a prioritized list of feedback items for joints outside the correct range.
    Items are sorted by absolute deviation (largest deviation = highest priority = priority_order 1).

    Args:
        joint_results: list of dicts (same structure as used in scoring_service)

    Returns:
        list of feedback dicts ordered by priority_order ascending
    """
    incorrect = [r for r in joint_results if not r["is_correct"]]
    if not incorrect:
        return []

    # Sort by absolute deviation descending → largest error = priority 1
    incorrect.sort(key=lambda r: abs(r["deviation"]), reverse=True)

    feedback: List[Dict] = []
    for priority, r in enumerate(incorrect, start=1):
        joint_name = r["joint_name"]
        tmpl = TEMPLATES.get(joint_name, _DEFAULT_TEMPLATE)

        # Normalise impact score to [0, 1] using 90° as the maximum expected deviation
        impact = min(abs(r["deviation"]) / 90.0, 1.0)

        feedback.append(
            {
                "correction_title": tmpl["title"],
                "correction_text": tmpl["text"].format(
                    angle=r["measured_angle"],
                    min=r["ref_min"],
                    max=r["ref_max"],
                    joint=joint_name.replace("_", " "),
                ),
                "biomechanical_explanation": tmpl["biomechanical"],
                "exercise_suggestion": tmpl["exercise"],
                "priority_order": priority,
                "impact_score": round(impact, 3),
            }
        )

    return feedback
