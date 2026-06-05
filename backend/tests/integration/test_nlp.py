"""
Integration tests for /nlp endpoints.
The NLP feedback endpoint is stateless and requires no authentication.
"""
import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _scores_payload(**overrides):
    """Return a valid FeedbackRequest payload, optionally overridden."""
    base = {
        "potencia":   65.0,
        "equilibrio": 70.0,
        "alineacion": 55.0,
        "velocidad":  60.0,
    }
    base.update(overrides)
    return base


# ══════════════════════════════════════════════════════════════════════════════
#  NLP FEEDBACK ENDPOINT
# ══════════════════════════════════════════════════════════════════════════════

class TestNlpFeedbackEndpoint:
    """Tests for POST /nlp/feedback."""

    def test_feedback_with_valid_scores_returns_200(self, client):
        # Arrange
        payload = _scores_payload()

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert
        assert response.status_code == 200

    def test_feedback_response_contains_feedback_field(self, client):
        # Arrange
        payload = _scores_payload()

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert
        data = response.json()
        assert "feedback" in data

    def test_feedback_returns_non_empty_string(self, client):
        # Arrange
        payload = _scores_payload()

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert
        feedback = response.json()["feedback"]
        assert isinstance(feedback, str)
        assert len(feedback) > 0

    def test_feedback_with_all_zero_scores_returns_200(self, client):
        # Arrange — boundary values: all zeros
        payload = _scores_payload(potencia=0.0, equilibrio=0.0, alineacion=0.0, velocidad=0.0)

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert
        assert response.status_code == 200
        assert len(response.json()["feedback"]) > 0

    def test_feedback_with_all_hundred_scores_returns_200(self, client):
        # Arrange — boundary values: all 100
        payload = _scores_payload(potencia=100.0, equilibrio=100.0, alineacion=100.0, velocidad=100.0)

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert
        assert response.status_code == 200
        assert len(response.json()["feedback"]) > 0

    def test_feedback_high_scores_mentions_positive_terms(self, client):
        # Arrange — high scores should produce congratulatory text
        payload = _scores_payload(potencia=92.0, equilibrio=95.0, alineacion=88.0, velocidad=91.0)

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert — the opening for high avg (>=75) contains "excelente"
        feedback = response.json()["feedback"].lower()
        assert "excelente" in feedback or "excepcional" in feedback or "sobresaliente" in feedback

    def test_feedback_low_scores_mentions_improvement_terms(self, client):
        # Arrange — low scores trigger improvement-focused language
        payload = _scores_payload(potencia=15.0, equilibrio=20.0, alineacion=10.0, velocidad=18.0)

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert — the opening for low avg (<50) contains improvement language
        feedback = response.json()["feedback"].lower()
        assert "mejora" in feedback or "trabajo" in feedback or "necesita" in feedback

    def test_feedback_no_auth_required(self, client):
        # Arrange — NLP endpoint is public; no auth header sent
        payload = _scores_payload()

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert — should succeed without authentication
        assert response.status_code == 200


class TestNlpFeedbackValidation:
    """Tests for input validation — scores outside [0, 100] must be rejected."""

    def test_potencia_above_100_returns_422(self, client):
        # Arrange
        payload = _scores_payload(potencia=101.0)

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert
        assert response.status_code == 422

    def test_potencia_below_zero_returns_422(self, client):
        # Arrange
        payload = _scores_payload(potencia=-1.0)

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert
        assert response.status_code == 422

    def test_equilibrio_above_100_returns_422(self, client):
        # Arrange
        payload = _scores_payload(equilibrio=150.0)

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert
        assert response.status_code == 422

    def test_velocidad_negative_returns_422(self, client):
        # Arrange
        payload = _scores_payload(velocidad=-0.1)

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert
        assert response.status_code == 422

    def test_alineacion_above_100_returns_422(self, client):
        # Arrange
        payload = _scores_payload(alineacion=200.0)

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert
        assert response.status_code == 422

    def test_missing_required_field_returns_422(self, client):
        # Arrange — potencia is missing
        payload = {
            "equilibrio": 60.0,
            "alineacion": 55.0,
            "velocidad":  65.0,
        }

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert
        assert response.status_code == 422

    def test_empty_body_returns_422(self, client):
        # Act
        response = client.post("/nlp/feedback", json={})

        # Assert
        assert response.status_code == 422

    def test_string_value_instead_of_float_returns_422(self, client):
        # Arrange — potencia is a string instead of a number
        payload = {
            "potencia":   "alto",
            "equilibrio": 60.0,
            "alineacion": 55.0,
            "velocidad":  65.0,
        }

        # Act
        response = client.post("/nlp/feedback", json=payload)

        # Assert
        assert response.status_code == 422
