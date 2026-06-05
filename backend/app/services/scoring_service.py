"""
Module: services.scoring_service
Description: Calculates technical sub-scores (alignment, power, balance, speed)
             and the global score from joint measurement results.
"""
from typing import List, Dict


def calculate_scores(
    joint_results: List[Dict],
    speed_proxy: float,
    frame_count: int,
) -> Dict[str, float]:
    """
    Compute the four sub-scores and the weighted global score.

    Args:
        joint_results: list of dicts with keys:
            joint_name, measured_angle, ref_min, ref_max, optimal_angle, is_correct, deviation, weight
        speed_proxy: mean wrist displacement per frame (from mediapipe_service)
        frame_count: total number of frames processed

    Returns:
        dict with alignment_score, power_score, balance_score, speed_score, global_score
        all in range [0.0, 100.0]
    """
    if not joint_results:
        return {
            "alignment_score": 0.0,
            "power_score": 0.0,
            "balance_score": 0.0,
            "speed_score": 0.0,
            "global_score": 0.0,
        }

    # ── Alignment score ─────────────────────────────────────────────────
    # Weighted percentage of joints within the correct range.
    # Partial credit (50 %) if the joint is within 10° of the boundary.
    total_weight = sum(r.get("weight", 1.0) for r in joint_results)
    alignment_raw = 0.0

    for r in joint_results:
        w = r.get("weight", 1.0)
        if r["is_correct"]:
            alignment_raw += w
        else:
            # Compute how far outside the [min, max] interval the angle is
            deviation_from_boundary = min(
                abs(r["measured_angle"] - r["ref_min"]),
                abs(r["measured_angle"] - r["ref_max"]),
            )
            if deviation_from_boundary <= 10.0:
                alignment_raw += w * 0.5  # partial credit

    alignment_score = (alignment_raw / total_weight) * 100.0 if total_weight > 0 else 0.0

    # ── Power score ──────────────────────────────────────────────────────
    # Derived from extension joints (elbows, knees, hip extension).
    extension_joints = [
        r for r in joint_results
        if any(k in r["joint_name"] for k in ("elbow", "knee", "extension", "target_arm"))
    ]
    if extension_joints:
        power_values = []
        for r in extension_joints:
            opt = r["optimal_angle"]
            if opt > 0:
                ratio = min(r["measured_angle"] / opt, 1.0)
                power_values.append(ratio * 100.0)
            else:
                power_values.append(100.0 if r["is_correct"] else 50.0)
        power_score = sum(power_values) / len(power_values)
    else:
        power_score = alignment_score  # fallback when no extension joints present

    # ── Balance score ────────────────────────────────────────────────────
    # Derived from hip and knee joints — positional stability.
    balance_joints = [
        r for r in joint_results
        if any(k in r["joint_name"] for k in ("hip", "knee", "support", "kicking_hip"))
    ]
    if balance_joints:
        balance_values = []
        for r in balance_joints:
            if r["is_correct"]:
                balance_values.append(100.0)
            else:
                # Penalise proportionally to the deviation from the optimal
                penalty = min(abs(r["deviation"]) * 1.5, 100.0)
                balance_values.append(max(0.0, 100.0 - penalty))
        balance_score = sum(balance_values) / len(balance_values)
    else:
        balance_score = alignment_score

    # ── Speed score ──────────────────────────────────────────────────────
    # speed_proxy is the mean wrist displacement per frame.
    # Typical range for a punch is 0.005–0.04 normalised units/frame.
    # We scale so that 0.025 normalised units/frame ≈ 80 points.
    speed_score = min(speed_proxy * 3200.0, 100.0)

    # ── Global score ─────────────────────────────────────────────────────
    global_score = (
        alignment_score * 0.40
        + power_score   * 0.25
        + balance_score * 0.20
        + speed_score   * 0.15
    )
    global_score = max(0.0, min(100.0, global_score))

    return {
        "alignment_score": round(alignment_score, 1),
        "power_score":     round(power_score,     1),
        "balance_score":   round(balance_score,   1),
        "speed_score":     round(speed_score,     1),
        "global_score":    round(global_score,    1),
    }
