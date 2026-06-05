"""
Unit tests for feedback_service.
Tests feedback generation from joint measurement results in isolation.
"""
from app.services.feedback_service import generate_feedback


def _joint(joint_name, measured, ref_min, ref_max, optimal):
    """Helper to build a joint result dict."""
    is_correct = ref_min <= measured <= ref_max
    return {
        "joint_name": joint_name,
        "measured_angle": measured,
        "ref_min": ref_min,
        "ref_max": ref_max,
        "optimal_angle": optimal,
        "is_correct": is_correct,
        "deviation": measured - optimal,
        "weight": 1.0,
    }


class TestGenerateFeedback:
    """Tests for generate_feedback — feedback generation and prioritization logic."""

    def test_all_correct_joints_produces_empty_feedback_list(self):
        # Arrange — all joints inside their correct range
        joints = [
            _joint("right_elbow",    172, 165, 180, 175),
            _joint("right_shoulder",  88,  80, 100,  90),
        ]

        # Act
        feedback = generate_feedback(joints)

        # Assert
        assert feedback == []

    def test_generates_one_feedback_item_per_incorrect_joint(self):
        # Arrange — two incorrect joints out of three
        joints = [
            _joint("right_elbow",         140, 165, 180, 175),  # incorrect
            _joint("right_shoulder",        88,  80, 100,  90),  # correct
            _joint("hip_rotation_proxy",     5,  35,  55,  45),  # incorrect
        ]

        # Act
        feedback = generate_feedback(joints)

        # Assert
        assert len(feedback) == 2

    def test_feedback_ordered_by_largest_absolute_deviation_first(self):
        # Arrange — right_elbow has deviation=75, hip has deviation=15
        joints = [
            _joint("right_elbow",       100, 165, 180, 175),   # |deviation| = 75
            _joint("hip_rotation_proxy",  30,  35,  55,  45),  # |deviation| = 15
        ]

        # Act
        feedback = generate_feedback(joints)

        # Assert — largest deviation gets priority_order=1
        assert feedback[0]["priority_order"] == 1
        assert feedback[0]["impact_score"] > feedback[1]["impact_score"]

    def test_feedback_items_contain_all_required_fields(self):
        # Arrange
        joints = [_joint("right_elbow", 100, 165, 180, 175)]

        # Act
        feedback = generate_feedback(joints)

        # Assert
        assert len(feedback) == 1
        item = feedback[0]
        required_fields = {
            "correction_title",
            "correction_text",
            "biomechanical_explanation",
            "exercise_suggestion",
            "priority_order",
            "impact_score",
        }
        assert required_fields.issubset(set(item.keys()))

    def test_impact_score_is_normalised_between_0_and_1(self):
        # Arrange — extreme deviation
        joints = [_joint("right_elbow", 0, 165, 180, 175)]  # deviation = -175

        # Act
        feedback = generate_feedback(joints)

        # Assert — impact_score must be clamped at 1.0
        assert 0.0 <= feedback[0]["impact_score"] <= 1.0
        assert feedback[0]["impact_score"] == 1.0

    def test_unknown_joint_uses_default_template(self):
        # Arrange — joint not in TEMPLATES dict
        joints = [_joint("unknown_exotic_joint", 30, 80, 120, 100)]

        # Act
        feedback = generate_feedback(joints)

        # Assert — still produces feedback using the default template
        assert len(feedback) == 1
        assert feedback[0]["correction_title"] == "Ángulo articular fuera de rango"

    def test_priority_order_is_sequential_starting_from_1(self):
        # Arrange — three incorrect joints
        joints = [
            _joint("right_elbow",       100, 165, 180, 175),
            _joint("right_shoulder",    150,  80, 100,  90),
            _joint("hip_rotation_proxy",  5,  35,  55,  45),
        ]

        # Act
        feedback = generate_feedback(joints)

        # Assert — priority_order is 1, 2, 3 in ascending order
        orders = [f["priority_order"] for f in feedback]
        assert orders == [1, 2, 3]

    def test_empty_joint_list_returns_empty_feedback(self):
        # Act
        feedback = generate_feedback([])

        # Assert
        assert feedback == []
