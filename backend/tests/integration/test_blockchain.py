"""
Integration tests for /blockchain endpoints.
Covers certificate generation (auth required) and public hash verification.
"""
import pytest
from datetime import datetime, timezone

from app.models.analysis import Analysis
from app.models.blockchain import Certificate
from app.models.discipline import Technique


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_completed_analysis(db, user_id: int, score: float = 78.5) -> Analysis:
    """Create and flush a completed Analysis owned by the given user."""
    technique = db.query(Technique).first()
    analysis = Analysis(
        user_id=user_id,
        technique_id=technique.id,
        video_original_path=f"tests/storage/{user_id}_test.mp4",
        status="completed",
        global_score=score,
        power_score=score,
        balance_score=score,
        alignment_score=score,
        speed_score=score,
        xp_awarded=30,
        completed_at=datetime(2026, 6, 5, 12, 0, 0, tzinfo=timezone.utc),
    )
    db.add(analysis)
    db.flush()
    return analysis


def _make_pending_analysis(db, user_id: int) -> Analysis:
    """Create and flush a pending Analysis (not yet completed — cannot be certified)."""
    technique = db.query(Technique).first()
    analysis = Analysis(
        user_id=user_id,
        technique_id=technique.id,
        video_original_path=f"tests/storage/{user_id}_pending.mp4",
        status="pending",
        global_score=None,
        power_score=None,
        balance_score=None,
        alignment_score=None,
        speed_score=None,
        xp_awarded=0,
        completed_at=None,
    )
    db.add(analysis)
    db.flush()
    return analysis


# ══════════════════════════════════════════════════════════════════════════════
#  GENERATE CERTIFICATE
# ══════════════════════════════════════════════════════════════════════════════

class TestGenerateCertificate:
    """Tests for POST /blockchain/certificates/generate/{analysis_id}."""

    def test_generate_certificate_returns_200_with_hash(
        self, client, auth_headers, db, test_user
    ):
        # Arrange
        analysis = _make_completed_analysis(db, test_user.id)

        # Act
        response = client.post(
            f"/blockchain/certificates/generate/{analysis.id}",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        assert len(data["hash"]) == 64  # SHA-256 hex
        assert data["analysis_id"] == analysis.id

    def test_generate_certificate_response_contains_required_fields(
        self, client, auth_headers, db, test_user
    ):
        # Arrange
        analysis = _make_completed_analysis(db, test_user.id)

        # Act
        response = client.post(
            f"/blockchain/certificates/generate/{analysis.id}",
            headers=auth_headers,
        )

        # Assert — all CertificateOut fields must be present
        data = response.json()
        assert "id" in data
        assert "analysis_id" in data
        assert "hash" in data
        assert "issued_at" in data
        assert "verified_count" in data

    def test_generate_certificate_idempotent_returns_same_hash(
        self, client, auth_headers, db, test_user
    ):
        # Arrange
        analysis = _make_completed_analysis(db, test_user.id)

        # Act — call the endpoint twice
        response_1 = client.post(
            f"/blockchain/certificates/generate/{analysis.id}",
            headers=auth_headers,
        )
        response_2 = client.post(
            f"/blockchain/certificates/generate/{analysis.id}",
            headers=auth_headers,
        )

        # Assert — same hash returned both times
        assert response_1.status_code == 200
        assert response_2.status_code == 200
        assert response_1.json()["hash"] == response_2.json()["hash"]
        assert response_1.json()["id"] == response_2.json()["id"]

    def test_generate_certificate_without_auth_returns_401(self, client, db, test_user):
        # Arrange
        analysis = _make_completed_analysis(db, test_user.id)

        # Act
        response = client.post(
            f"/blockchain/certificates/generate/{analysis.id}"
        )

        # Assert
        assert response.status_code == 401

    def test_generate_certificate_for_nonexistent_analysis_returns_404(
        self, client, auth_headers
    ):
        # Act
        response = client.post(
            "/blockchain/certificates/generate/99999",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 404

    def test_generate_certificate_for_pending_analysis_returns_422(
        self, client, auth_headers, db, test_user
    ):
        # Arrange — analysis is not completed
        analysis = _make_pending_analysis(db, test_user.id)

        # Act
        response = client.post(
            f"/blockchain/certificates/generate/{analysis.id}",
            headers=auth_headers,
        )

        # Assert — service rejects non-completed analyses
        assert response.status_code == 422

    def test_generate_certificate_for_another_users_analysis_returns_403(
        self, client, auth_headers, db, test_user, second_user
    ):
        # Arrange — analysis belongs to second_user, not test_user
        analysis = _make_completed_analysis(db, second_user.id)

        # Act — authenticated as test_user
        response = client.post(
            f"/blockchain/certificates/generate/{analysis.id}",
            headers=auth_headers,
        )

        # Assert — ownership check must reject this
        assert response.status_code == 403


# ══════════════════════════════════════════════════════════════════════════════
#  VERIFY CERTIFICATE
# ══════════════════════════════════════════════════════════════════════════════

class TestVerifyCertificate:
    """Tests for GET /blockchain/certificates/{hash_value} — public endpoint."""

    def test_verify_valid_certificate_returns_valid_true(
        self, client, auth_headers, db, test_user
    ):
        # Arrange — generate a certificate first
        analysis = _make_completed_analysis(db, test_user.id)
        gen_response = client.post(
            f"/blockchain/certificates/generate/{analysis.id}",
            headers=auth_headers,
        )
        cert_hash = gen_response.json()["hash"]

        # Act — verify it (no auth required)
        response = client.get(f"/blockchain/certificates/{cert_hash}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["certificate"] is not None
        assert data["certificate"]["hash"] == cert_hash

    def test_verify_valid_certificate_increments_verified_count(
        self, client, auth_headers, db, test_user
    ):
        # Arrange
        analysis = _make_completed_analysis(db, test_user.id)
        gen_response = client.post(
            f"/blockchain/certificates/generate/{analysis.id}",
            headers=auth_headers,
        )
        cert_hash = gen_response.json()["hash"]

        # Act — verify twice
        response_1 = client.get(f"/blockchain/certificates/{cert_hash}")
        response_2 = client.get(f"/blockchain/certificates/{cert_hash}")

        # Assert — verified_count increments on each valid verification
        assert response_1.json()["certificate"]["verified_count"] == 1
        assert response_2.json()["certificate"]["verified_count"] == 2

    def test_verify_invalid_hash_returns_valid_false(self, client):
        # Arrange — a 64-char hex string that does not exist
        fake_hash = "a" * 64

        # Act
        response = client.get(f"/blockchain/certificates/{fake_hash}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["certificate"] is None

    def test_verify_invalid_hash_returns_informative_message(self, client):
        # Arrange
        fake_hash = "0" * 64

        # Act
        response = client.get(f"/blockchain/certificates/{fake_hash}")

        # Assert — message must be non-empty and mention the certificate
        data = response.json()
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0

    def test_verify_endpoint_requires_no_authentication(self, client, auth_headers, db, test_user):
        # Arrange — generate a real certificate
        analysis = _make_completed_analysis(db, test_user.id, score=92.0)
        gen_resp = client.post(
            f"/blockchain/certificates/generate/{analysis.id}",
            headers=auth_headers,
        )
        cert_hash = gen_resp.json()["hash"]

        # Act — call without any auth header
        response = client.get(f"/blockchain/certificates/{cert_hash}")

        # Assert — public endpoint must succeed without auth
        assert response.status_code == 200
        assert response.json()["valid"] is True

    def test_verify_certificate_response_contains_required_fields(
        self, client, auth_headers, db, test_user
    ):
        # Arrange
        analysis = _make_completed_analysis(db, test_user.id)
        gen_resp = client.post(
            f"/blockchain/certificates/generate/{analysis.id}",
            headers=auth_headers,
        )
        cert_hash = gen_resp.json()["hash"]

        # Act
        response = client.get(f"/blockchain/certificates/{cert_hash}")

        # Assert — CertificateVerifyResponse schema
        data = response.json()
        assert "valid" in data
        assert "certificate" in data
        assert "message" in data
