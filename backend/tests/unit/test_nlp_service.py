"""
Unit tests for nlp_service.generate_nlp_feedback.
Tests feedback composition logic in complete isolation — no HTTP, no database.
"""
from app.services.nlp_service import generate_nlp_feedback


class TestGenerateNlpFeedback:
    """Tests for generate_nlp_feedback — the core NLP composition function."""

    def test_feedback_all_low_scores_contains_improvement_language(self):
        # Arrange — all dimensions at 20 → "deficiente" classification
        scores = {"potencia": 20, "equilibrio": 20, "alineacion": 20, "velocidad": 20}

        # Act
        result = generate_nlp_feedback(scores)

        # Assert — low average triggers the improvement-focused opening
        assert "mejora" in result.lower() or "trabajo" in result.lower() or "necesita" in result.lower()

    def test_feedback_all_low_scores_has_low_average_opening(self):
        # Arrange — avg=20, triggers _OPENING_LOW
        scores = {"potencia": 20, "equilibrio": 20, "alineacion": 20, "velocidad": 20}

        # Act
        result = generate_nlp_feedback(scores)

        # Assert — the exact opening text for low performers
        assert "áreas de mejora" in result.lower()

    def test_feedback_all_high_scores_contains_positive_language(self):
        # Arrange — all dimensions at 90 → "sobresaliente" classification
        scores = {"potencia": 90, "equilibrio": 90, "alineacion": 90, "velocidad": 90}

        # Act
        result = generate_nlp_feedback(scores)

        # Assert — high average triggers the congratulatory opening
        assert "excelente" in result.lower() or "excepcional" in result.lower() or "sobresaliente" in result.lower()

    def test_feedback_all_high_scores_has_high_average_opening(self):
        # Arrange — avg=90, triggers _OPENING_HIGH
        scores = {"potencia": 90, "equilibrio": 90, "alineacion": 90, "velocidad": 90}

        # Act
        result = generate_nlp_feedback(scores)

        # Assert — the exact opening text for high performers
        assert "excelente sesión" in result.lower()

    def test_feedback_mixed_scores_mentions_strong_dimensions(self):
        # Arrange — potencia and velocidad high (90), equilibrio and alineacion low (20)
        scores = {"potencia": 90, "equilibrio": 20, "alineacion": 20, "velocidad": 90}

        # Act
        result = generate_nlp_feedback(scores)

        # Assert — strong dimensions (potencia, velocidad) appear as strengths
        assert "potencia" in result.lower() or "velocidad" in result.lower()

    def test_feedback_mixed_scores_mentions_weak_dimensions(self):
        # Arrange — equilibrio and alineacion are deficient
        scores = {"potencia": 90, "equilibrio": 20, "alineacion": 20, "velocidad": 90}

        # Act
        result = generate_nlp_feedback(scores)

        # Assert — weak dimensions (equilibrio, alineacion) appear in feedback
        assert "equilibrio" in result.lower() or "alineación" in result.lower()

    def test_feedback_returns_non_empty_string(self):
        # Arrange — typical mid-range session scores
        scores = {"potencia": 55, "equilibrio": 60, "alineacion": 50, "velocidad": 65}

        # Act
        result = generate_nlp_feedback(scores)

        # Assert — must always return a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0

    def test_feedback_returns_string_type_for_any_input(self):
        # Arrange — minimal valid input
        scores = {"potencia": 50, "equilibrio": 50, "alineacion": 50, "velocidad": 50}

        # Act
        result = generate_nlp_feedback(scores)

        # Assert
        assert isinstance(result, str)

    def test_feedback_boundary_zero_scores_does_not_raise(self):
        # Arrange — extreme lower boundary
        scores = {"potencia": 0, "equilibrio": 0, "alineacion": 0, "velocidad": 0}

        # Act / Assert — must not raise any exception
        result = generate_nlp_feedback(scores)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_feedback_boundary_hundred_scores_does_not_raise(self):
        # Arrange — extreme upper boundary
        scores = {"potencia": 100, "equilibrio": 100, "alineacion": 100, "velocidad": 100}

        # Act / Assert — must not raise any exception
        result = generate_nlp_feedback(scores)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_feedback_boundary_mixed_zero_and_hundred(self):
        # Arrange — one dim at 0, another at 100 (maximally polarised)
        scores = {"potencia": 0, "equilibrio": 100, "alineacion": 0, "velocidad": 100}

        # Act / Assert — no exception, returns valid string
        result = generate_nlp_feedback(scores)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_feedback_perfect_session_has_no_weakness_message(self):
        # Arrange — all sobresaliente, so no weak dims
        scores = {"potencia": 95, "equilibrio": 95, "alineacion": 95, "velocidad": 95}

        # Act
        result = generate_nlp_feedback(scores)

        # Assert — _NO_WEAKNESS text appears
        assert "no se detectan áreas críticas" in result.lower()

    def test_feedback_all_deficient_has_no_strength_message(self):
        # Arrange — all scores below 40 (deficiente) → no strengths
        scores = {"potencia": 10, "equilibrio": 15, "alineacion": 5, "velocidad": 20}

        # Act
        result = generate_nlp_feedback(scores)

        # Assert — _NO_STRENGTH text appears
        assert "margen de mejora" in result.lower()

    def test_feedback_missing_keys_default_to_zero(self):
        # Arrange — missing keys should default to 0 without raising
        scores = {}

        # Act / Assert
        result = generate_nlp_feedback(scores)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_feedback_contains_motivational_closing(self):
        # Arrange
        scores = {"potencia": 55, "equilibrio": 60, "alineacion": 58, "velocidad": 50}

        # Act
        result = generate_nlp_feedback(scores)

        # Assert — one of the _CLOSINGS is present (medium avg → index 1)
        assert "constancia" in result.lower() or "entrenando" in result.lower() or "análisis" in result.lower()

    def test_feedback_includes_per_dimension_description(self):
        # Arrange — score at 80 → "avanzado" for all dims
        scores = {"potencia": 80, "equilibrio": 80, "alineacion": 80, "velocidad": 80}

        # Act
        result = generate_nlp_feedback(scores)

        # Assert — avanzado description for potencia should appear
        assert "avanzado" in result.lower() or "cadena cinética bien desarrollada" in result.lower()
