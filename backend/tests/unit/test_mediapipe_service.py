"""
Unit tests for mediapipe_service — angle calculation and pose analysis logic.
These tests cover pure mathematical functions that do not require a camera or GPU.
The PoseAnalyzer instantiation is tested with a blank frame to verify graceful handling.
"""
import pytest
import numpy as np

from app.services.mediapipe_service import PoseAnalyzer


@pytest.fixture(scope="module")
def analyzer():
    """Provide a single PoseAnalyzer instance for the test module and release after."""
    a = PoseAnalyzer()
    yield a
    a.close()


class TestAngleCalculation:
    """Tests for the calculate_angle pure function — no MediaPipe model required."""

    def test_perpendicular_segments_produce_90_degrees(self, analyzer):
        # Arrange — A straight up, B at origin, C straight right
        a = [0.0, 1.0]
        b = [0.0, 0.0]
        c = [1.0, 0.0]

        # Act
        angle = analyzer.calculate_angle(a, b, c)

        # Assert — allow ±1° floating-point tolerance
        assert abs(angle - 90.0) < 1.0

    def test_collinear_points_produce_180_degrees(self, analyzer):
        # Arrange — three points on the same horizontal line
        a = [0.0, 0.0]
        b = [1.0, 0.0]
        c = [2.0, 0.0]

        # Act
        angle = analyzer.calculate_angle(a, b, c)

        # Assert
        assert abs(angle - 180.0) < 1.0

    def test_45_degree_angle_is_calculated_correctly(self, analyzer):
        # Arrange
        a = [1.0, 0.0]
        b = [0.0, 0.0]
        c = [1.0, 1.0]

        # Act
        angle = analyzer.calculate_angle(a, b, c)

        # Assert
        assert abs(angle - 45.0) < 1.0

    def test_angle_is_symmetric_regardless_of_point_order(self, analyzer):
        # Arrange — same physical angle, different point order
        a = [1.0, 0.0]
        b = [0.0, 0.0]
        c = [0.0, 1.0]

        # Act
        angle_forward = analyzer.calculate_angle(a, b, c)
        angle_backward = analyzer.calculate_angle(c, b, a)

        # Assert — angle should be the same in both directions
        assert abs(angle_forward - angle_backward) < 0.1

    def test_angle_result_is_always_non_negative(self, analyzer):
        # Arrange — various point combinations
        test_cases = [
            ([1, 0], [0, 0], [0, 1]),
            ([0, 1], [0, 0], [1, 0]),
            ([1, 1], [0, 0], [1, -1]),
        ]
        for a, b, c in test_cases:
            # Act
            angle = analyzer.calculate_angle(a, b, c)

            # Assert
            assert angle >= 0.0, f"Negative angle {angle} for a={a}, b={b}, c={c}"


class TestPoseAnalyzerBlankFrame:
    """Tests for analyze_frame with images that contain no human pose."""

    def test_analyze_blank_white_frame_returns_none(self, analyzer):
        """A white frame contains no pose landmarks — result must be None."""
        import cv2

        # Arrange — 480×640 white image encoded as JPEG bytes
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        # Act
        result = analyzer.analyze_frame(frame_bytes)

        # Assert
        assert result is None

    def test_analyze_invalid_bytes_does_not_raise(self, analyzer):
        """Invalid bytes should not crash the service — return None gracefully."""
        # Act / Assert — must not raise
        result = analyzer.analyze_frame(b"not_an_image_at_all")
        assert result is None
