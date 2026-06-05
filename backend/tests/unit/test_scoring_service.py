"""
Unit tests for scoring_service.
Tests score calculation logic in complete isolation from HTTP and database layers.
"""
from app.services.scoring_service import calculate_scores


def _joint(joint_name, measured, ref_min, ref_max, optimal, weight=1.0):
    """Helper to build a joint result dict matching the service contract."""
    is_correct = ref_min <= measured <= ref_max
    return {
        "joint_name": joint_name,
        "measured_angle": measured,
        "ref_min": ref_min,
        "ref_max": ref_max,
        "optimal_angle": optimal,
        "is_correct": is_correct,
        "deviation": measured - optimal,
        "weight": weight,
    }


class TestCalculateScores:
    """Tests for calculate_scores — the core biomechanical scoring function."""

    def test_all_correct_joints_produces_perfect_alignment_score(self):
        # Arrange
        joints = [
            _joint("right_elbow",    170, 165, 180, 175),
            _joint("right_shoulder",  88,  80, 100,  90),
            _joint("left_elbow",      92,  85, 100,  90),
        ]

        # Act
        scores = calculate_scores(joints, speed_proxy=0.02, frame_count=60)

        # Assert
        assert scores["alignment_score"] == 100.0
        assert scores["global_score"] > 70.0

    def test_all_incorrect_joints_produces_low_global_score(self):
        # Arrange — all joints far outside their ranges
        joints = [
            _joint("right_elbow",    90, 165, 180, 175),
            _joint("right_shoulder", 150,  80, 100,  90),
        ]

        # Act
        scores = calculate_scores(joints, speed_proxy=0.0, frame_count=30)

        # Assert
        assert scores["global_score"] < 50.0

    def test_empty_joint_results_returns_all_zero_scores(self):
        # Arrange — no joints detected
        joints = []

        # Act
        scores = calculate_scores(joints, speed_proxy=0.0, frame_count=0)

        # Assert
        assert scores["global_score"] == 0.0
        assert scores["alignment_score"] == 0.0
        assert scores["power_score"] == 0.0
        assert scores["balance_score"] == 0.0
        assert scores["speed_score"] == 0.0

    def test_all_scores_are_clamped_between_0_and_100(self):
        # Arrange — extreme speed proxy that would overflow without clamping
        joints = [_joint("right_elbow", 175, 165, 180, 175)]

        # Act
        scores = calculate_scores(joints, speed_proxy=999.0, frame_count=60)

        # Assert
        for key, value in scores.items():
            assert 0.0 <= value <= 100.0, f"{key} = {value} is outside [0, 100]"

    def test_joint_within_10_degrees_of_boundary_receives_partial_credit(self):
        # Arrange — measured=160, ref_min=165 → deviation_from_boundary=5 ≤ 10 → 50% credit
        joints = [_joint("right_elbow", 160, 165, 180, 175)]

        # Act
        scores = calculate_scores(joints, speed_proxy=0.0, frame_count=30)

        # Assert — partial credit: not 0 and not 100
        assert 0.0 < scores["alignment_score"] < 100.0
        assert scores["alignment_score"] == 50.0

    def test_joint_more_than_10_degrees_outside_boundary_receives_no_credit(self):
        # Arrange — measured=100, ref_min=165 → deviation_from_boundary=65 > 10 → 0 credit
        joints = [_joint("right_elbow", 100, 165, 180, 175)]

        # Act
        scores = calculate_scores(joints, speed_proxy=0.0, frame_count=30)

        # Assert
        assert scores["alignment_score"] == 0.0

    def test_speed_score_scales_with_speed_proxy(self):
        # Arrange — speed_proxy=0.025 should produce score ≈ 80
        joints = [_joint("right_shoulder", 88, 80, 100, 90)]

        # Act
        scores = calculate_scores(joints, speed_proxy=0.025, frame_count=30)

        # Assert — 0.025 * 3200 = 80
        assert scores["speed_score"] == 80.0

    def test_weighted_joints_affect_alignment_proportionally(self):
        # Arrange — one correct heavy joint, one incorrect light joint
        joints = [
            _joint("right_elbow",    170, 165, 180, 175, weight=3.0),  # correct, heavy
            _joint("right_shoulder", 150,  80, 100,  90, weight=1.0),  # incorrect, light
        ]

        # Act
        scores = calculate_scores(joints, speed_proxy=0.0, frame_count=30)

        # Assert — alignment > 50% because correct joint has 3x weight
        assert scores["alignment_score"] > 50.0

    def test_scores_dict_contains_all_required_keys(self):
        # Arrange
        joints = [_joint("right_elbow", 170, 165, 180, 175)]

        # Act
        scores = calculate_scores(joints, speed_proxy=0.01, frame_count=30)

        # Assert
        required_keys = {"alignment_score", "power_score", "balance_score", "speed_score", "global_score"}
        assert required_keys == set(scores.keys())
