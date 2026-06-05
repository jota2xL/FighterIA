"""
Integration tests for /analysis endpoints.
Tests analysis creation (upload), retrieval by ID, history pagination and comparison.
"""
import pytest
from app.models.analysis import Analysis
from app.models.discipline import Technique


def _make_analysis(user_id, technique_id, score=72.5, status="completed"):
    """Helper to create an Analysis ORM object without flushing."""
    return Analysis(
        user_id=user_id,
        technique_id=technique_id,
        video_original_path=f"tests/storage/{user_id}_{technique_id}.mp4",
        status=status,
        global_score=score if status == "completed" else None,
        power_score=score,
        balance_score=score,
        alignment_score=score,
        speed_score=score,
        xp_awarded=20 if status == "completed" else 0,
    )


class TestAnalysisCreation:
    """Tests for POST /analysis (multipart video upload)."""

    def test_create_analysis_without_token_returns_401(self, client, sample_video_bytes):
        # Act
        response = client.post(
            "/analysis",
            data={"technique_id": "1"},
            files={"video": ("test.mp4", sample_video_bytes, "video/mp4")},
        )

        # Assert
        assert response.status_code == 401

    def test_create_analysis_without_video_file_returns_422(self, client, auth_headers):
        # Act — missing the file part
        response = client.post(
            "/analysis",
            data={"technique_id": "1"},
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 422

    def test_create_analysis_without_technique_id_returns_422(self, client, auth_headers, sample_video_bytes):
        # Act — missing technique_id form field
        response = client.post(
            "/analysis",
            files={"video": ("test.mp4", sample_video_bytes, "video/mp4")},
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 422


class TestAnalysisRetrieval:
    """Tests for GET /analysis/{id} — retrieve a single analysis result."""

    def test_get_analysis_by_id_returns_200_for_owner(self, client, auth_headers, db, test_user):
        # Arrange
        technique = db.query(Technique).first()
        analysis = _make_analysis(test_user.id, technique.id)
        db.add(analysis)
        db.flush()

        # Act
        response = client.get(f"/analysis/{analysis.id}", headers=auth_headers)

        # Assert
        assert response.status_code == 200

    def test_get_analysis_response_contains_required_fields(self, client, auth_headers, db, test_user):
        # Arrange
        technique = db.query(Technique).first()
        analysis = _make_analysis(test_user.id, technique.id)
        db.add(analysis)
        db.flush()

        # Act
        response = client.get(f"/analysis/{analysis.id}", headers=auth_headers)

        # Assert
        data = response.json()
        required = {"id", "status", "technique", "global_score", "xp_awarded"}
        assert required.issubset(set(data.keys()))

    def test_get_analysis_by_nonexistent_id_returns_404(self, client, auth_headers):
        # Act
        response = client.get("/analysis/999999", headers=auth_headers)

        # Assert
        assert response.status_code == 404

    def test_get_analysis_owned_by_other_user_returns_403_or_404(self, client, auth_headers, db, second_user):
        # Arrange — analysis belongs to second_user, not test_user (auth_headers owner)
        technique = db.query(Technique).first()
        other_analysis = _make_analysis(second_user.id, technique.id)
        db.add(other_analysis)
        db.flush()

        # Act
        response = client.get(f"/analysis/{other_analysis.id}", headers=auth_headers)

        # Assert — must be either 403 or 404, never 200
        assert response.status_code in (403, 404)

    def test_get_analysis_requires_authentication(self, client, db, test_user):
        # Arrange
        technique = db.query(Technique).first()
        analysis = _make_analysis(test_user.id, technique.id)
        db.add(analysis)
        db.flush()

        # Act
        response = client.get(f"/analysis/{analysis.id}")

        # Assert
        assert response.status_code == 401


class TestAnalysisHistory:
    """Tests for GET /analysis/me — paginated history."""

    def test_get_history_returns_200(self, client, auth_headers):
        # Act
        response = client.get("/analysis/me", headers=auth_headers)

        # Assert
        assert response.status_code == 200

    def test_get_history_returns_empty_list_for_new_user(self, client, auth_headers):
        # Act
        response = client.get("/analysis/me", headers=auth_headers)

        # Assert
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_get_history_response_has_pagination_fields(self, client, auth_headers):
        # Act
        response = client.get("/analysis/me", headers=auth_headers)

        # Assert
        data = response.json()
        pagination_fields = {"items", "total", "page", "limit", "pages"}
        assert pagination_fields.issubset(set(data.keys()))

    def test_get_history_shows_analyses_belonging_to_current_user_only(
        self, client, auth_headers, db, test_user, second_user
    ):
        # Arrange — one analysis per user
        technique = db.query(Technique).first()
        my_analysis = _make_analysis(test_user.id, technique.id, score=85.0)
        other_analysis = _make_analysis(second_user.id, technique.id, score=55.0)
        db.add_all([my_analysis, other_analysis])
        db.flush()

        # Act
        response = client.get("/analysis/me", headers=auth_headers)

        # Assert — only test_user's analysis is returned
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["global_score"] == 85.0

    def test_get_history_requires_authentication(self, client):
        # Act
        response = client.get("/analysis/me")

        # Assert
        assert response.status_code == 401
