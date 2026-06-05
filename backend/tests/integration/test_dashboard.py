"""
Integration tests for /dashboard/me endpoints.
Tests stats aggregation, progress data and heatmap with various user states.
"""
import pytest
from datetime import datetime, timezone
from app.models.analysis import Analysis
from app.models.discipline import Technique


class TestDashboardStats:
    """Tests for GET /dashboard/me."""

    def test_dashboard_me_returns_200_for_authenticated_user(self, client, auth_headers):
        # Act
        response = client.get("/dashboard/me", headers=auth_headers)

        # Assert
        assert response.status_code == 200

    def test_dashboard_me_requires_authentication(self, client):
        # Act
        response = client.get("/dashboard/me")

        # Assert
        assert response.status_code == 401

    def test_dashboard_me_returns_required_fields(self, client, auth_headers):
        # Act
        response = client.get("/dashboard/me", headers=auth_headers)

        # Assert
        data = response.json()
        required_fields = {"total_analyses", "xp", "belt_level"}
        assert required_fields.issubset(set(data.keys()))

    def test_dashboard_me_shows_zero_analyses_for_new_user(self, client, auth_headers):
        # Act — test_user has no analyses
        response = client.get("/dashboard/me", headers=auth_headers)

        # Assert
        assert response.json()["total_analyses"] == 0

    def test_dashboard_me_stats_reflect_completed_analysis(self, client, auth_headers, db, test_user):
        # Arrange — create a completed analysis directly in the database
        technique = db.query(Technique).first()
        analysis = Analysis(
            user_id=test_user.id,
            technique_id=technique.id,
            video_original_path="tests/fixtures/sample_jab.mp4",
            status="completed",
            global_score=75.0,
            power_score=80.0,
            balance_score=70.0,
            alignment_score=75.0,
            speed_score=65.0,
            xp_awarded=30,
        )
        db.add(analysis)
        db.flush()

        # Act
        response = client.get("/dashboard/me", headers=auth_headers)

        # Assert
        data = response.json()
        assert data["total_analyses"] == 1
        assert data["best_score"] == 75.0

    def test_dashboard_me_best_score_ignores_failed_analyses(self, client, auth_headers, db, test_user):
        # Arrange — one completed and one failed analysis
        technique = db.query(Technique).first()
        completed = Analysis(
            user_id=test_user.id,
            technique_id=technique.id,
            video_original_path="tests/fixtures/ok.mp4",
            status="completed",
            global_score=60.0,
            xp_awarded=20,
        )
        failed = Analysis(
            user_id=test_user.id,
            technique_id=technique.id,
            video_original_path="tests/fixtures/bad.mp4",
            status="failed",
            global_score=None,
            xp_awarded=0,
        )
        db.add_all([completed, failed])
        db.flush()

        # Act
        response = client.get("/dashboard/me", headers=auth_headers)

        # Assert — best_score should reflect only completed analyses
        data = response.json()
        assert data["total_analyses"] == 1  # only completed
        assert data["best_score"] == 60.0


class TestDashboardProgress:
    """Tests for GET /dashboard/me/progress."""

    def test_progress_returns_200(self, client, auth_headers):
        # Act
        response = client.get("/dashboard/me/progress", headers=auth_headers)

        # Assert
        assert response.status_code == 200

    def test_progress_requires_authentication(self, client):
        # Act
        response = client.get("/dashboard/me/progress")

        # Assert
        assert response.status_code == 401

    def test_progress_accepts_period_days_query_param(self, client, auth_headers):
        # Act
        response = client.get("/dashboard/me/progress?period_days=60", headers=auth_headers)

        # Assert
        assert response.status_code == 200


class TestDashboardHeatmap:
    """Tests for GET /dashboard/me/heatmap."""

    def test_heatmap_returns_200(self, client, auth_headers):
        # Act
        response = client.get("/dashboard/me/heatmap", headers=auth_headers)

        # Assert
        assert response.status_code == 200

    def test_heatmap_requires_authentication(self, client):
        # Act
        response = client.get("/dashboard/me/heatmap")

        # Assert
        assert response.status_code == 401

    def test_heatmap_returns_data_with_date_and_count_fields(self, client, auth_headers):
        # Act
        response = client.get("/dashboard/me/heatmap", headers=auth_headers)

        # Assert
        data = response.json()
        assert "data" in data
        for entry in data["data"]:
            assert "date" in entry
            assert "count" in entry
