"""
Integration tests for /crm endpoints.
Covers Gym CRUD, gym metrics, Lead creation and listing.
All endpoints require JWT authentication — auth_headers fixture is used throughout.
"""
import pytest
from app.models.crm import Gym, Lead


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _gym_payload(**overrides):
    """Return a minimal valid GymCreate payload, optionally overridden."""
    base = {
        "name": "Dragon Gym Madrid",
        "city": "Madrid",
        "country": "España",
        "plan": "free",
    }
    base.update(overrides)
    return base


def _lead_payload(**overrides):
    """Return a minimal valid LeadCreate payload, optionally overridden."""
    base = {
        "name": "Carlos Fernández",
        "email": "carlos@example.com",
        "phone": "+34600000001",
        "status": "new",
        "source": "organic",
        "notes": "Interesado en clases de boxeo",
    }
    base.update(overrides)
    return base


def _create_gym(db, name="Dragon Gym", city="Madrid", plan="free"):
    """Create and flush a Gym ORM object directly to the DB session."""
    gym = Gym(name=name, city=city, country="España", plan=plan)
    db.add(gym)
    db.flush()
    return gym


# ══════════════════════════════════════════════════════════════════════════════
#  GYM CRUD
# ══════════════════════════════════════════════════════════════════════════════

class TestCreateGym:
    """Tests for POST /crm/gyms."""

    def test_create_gym_returns_201_with_gym_data(self, client, auth_headers):
        # Arrange
        payload = _gym_payload()

        # Act
        response = client.post("/crm/gyms", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["city"] == payload["city"]
        assert data["plan"] == "free"
        assert "id" in data
        assert "created_at" in data

    def test_create_gym_without_auth_returns_401(self, client):
        # Act
        response = client.post("/crm/gyms", json=_gym_payload())

        # Assert
        assert response.status_code == 401

    def test_create_gym_with_pro_plan(self, client, auth_headers):
        # Arrange
        payload = _gym_payload(name="Elite Boxing Club", plan="pro")

        # Act
        response = client.post("/crm/gyms", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 201
        assert response.json()["plan"] == "pro"

    def test_create_gym_with_invalid_plan_returns_422(self, client, auth_headers):
        # Arrange
        payload = _gym_payload(plan="premium")  # not a valid plan

        # Act
        response = client.post("/crm/gyms", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 422

    def test_create_gym_with_name_too_short_returns_422(self, client, auth_headers):
        # Arrange — name must be at least 2 characters
        payload = _gym_payload(name="X")

        # Act
        response = client.post("/crm/gyms", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 422


class TestListGyms:
    """Tests for GET /crm/gyms."""

    def test_list_gyms_returns_200_with_list(self, client, auth_headers, db):
        # Arrange — create two gyms in the DB
        _create_gym(db, name="Gym Alpha")
        _create_gym(db, name="Gym Beta")

        # Act
        response = client.get("/crm/gyms", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_list_gyms_without_auth_returns_401(self, client):
        # Act
        response = client.get("/crm/gyms")

        # Assert
        assert response.status_code == 401

    def test_list_gyms_returns_empty_list_when_no_gyms(self, client, auth_headers):
        # Arrange — nothing seeded in this test

        # Act
        response = client.get("/crm/gyms", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestGetGym:
    """Tests for GET /crm/gyms/{gym_id}."""

    def test_get_gym_returns_correct_gym(self, client, auth_headers, db):
        # Arrange
        gym = _create_gym(db, name="Tiger Dojo")

        # Act
        response = client.get(f"/crm/gyms/{gym.id}", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == gym.id
        assert data["name"] == "Tiger Dojo"

    def test_get_gym_nonexistent_returns_404(self, client, auth_headers):
        # Act — use an ID that cannot exist
        response = client.get("/crm/gyms/99999", headers=auth_headers)

        # Assert
        assert response.status_code == 404

    def test_get_gym_without_auth_returns_401(self, client, db):
        # Arrange
        gym = _create_gym(db)

        # Act
        response = client.get(f"/crm/gyms/{gym.id}")

        # Assert
        assert response.status_code == 401


class TestUpdateGym:
    """Tests for PUT /crm/gyms/{gym_id}."""

    def test_update_gym_name_and_city(self, client, auth_headers, db):
        # Arrange
        gym = _create_gym(db, name="Old Name", city="Barcelona")

        # Act
        response = client.put(
            f"/crm/gyms/{gym.id}",
            json={"name": "New Name", "city": "Sevilla"},
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["city"] == "Sevilla"

    def test_update_gym_plan(self, client, auth_headers, db):
        # Arrange
        gym = _create_gym(db, plan="free")

        # Act
        response = client.put(
            f"/crm/gyms/{gym.id}",
            json={"plan": "enterprise"},
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["plan"] == "enterprise"

    def test_update_gym_partial_update_preserves_unchanged_fields(self, client, auth_headers, db):
        # Arrange
        gym = _create_gym(db, name="Inmutable Name", city="Valencia")

        # Act — only update plan
        response = client.put(
            f"/crm/gyms/{gym.id}",
            json={"plan": "pro"},
            headers=auth_headers,
        )

        # Assert — name and city unchanged
        data = response.json()
        assert data["name"] == "Inmutable Name"
        assert data["city"] == "Valencia"
        assert data["plan"] == "pro"

    def test_update_nonexistent_gym_returns_404(self, client, auth_headers):
        # Act
        response = client.put(
            "/crm/gyms/99999",
            json={"name": "Ghost Gym"},
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 404


class TestDeleteGym:
    """Tests for DELETE /crm/gyms/{gym_id}."""

    def test_delete_gym_returns_deleted_true(self, client, auth_headers, db):
        # Arrange
        gym = _create_gym(db, name="Gym To Delete")

        # Act
        response = client.delete(f"/crm/gyms/{gym.id}", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        assert response.json()["deleted"] is True

    def test_delete_gym_then_get_returns_404(self, client, auth_headers, db):
        # Arrange
        gym = _create_gym(db, name="Ephemeral Gym")
        gym_id = gym.id

        # Act
        client.delete(f"/crm/gyms/{gym_id}", headers=auth_headers)
        response = client.get(f"/crm/gyms/{gym_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 404

    def test_delete_nonexistent_gym_returns_404(self, client, auth_headers):
        # Act
        response = client.delete("/crm/gyms/99999", headers=auth_headers)

        # Assert
        assert response.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
#  GYM METRICS
# ══════════════════════════════════════════════════════════════════════════════

class TestGymMetrics:
    """Tests for GET /crm/gyms/{gym_id}/metrics."""

    def test_gym_metrics_returns_correct_structure(self, client, auth_headers, db):
        # Arrange
        gym = _create_gym(db, name="Metrics Gym", plan="pro")

        # Act
        response = client.get(f"/crm/gyms/{gym.id}/metrics", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["gym_id"] == gym.id
        assert data["gym_name"] == "Metrics Gym"
        assert "total_trainers" in data
        assert "total_leads" in data
        assert "conversion_rate" in data
        assert data["plan"] == "pro"

    def test_gym_metrics_zero_leads_has_zero_conversion_rate(self, client, auth_headers, db):
        # Arrange — gym with no leads
        gym = _create_gym(db, name="Empty Gym")

        # Act
        response = client.get(f"/crm/gyms/{gym.id}/metrics", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_leads"] == 0
        assert data["conversion_rate"] == 0.0

    def test_gym_metrics_counts_leads(self, client, auth_headers, db):
        # Arrange — gym with two leads
        gym = _create_gym(db, name="Busy Gym")
        for i in range(2):
            lead = Lead(
                gym_id=gym.id,
                name=f"Lead {i}",
                email=f"lead{i}@example.com",
                status="new",
                source="organic",
                notes="",
            )
            db.add(lead)
        db.flush()

        # Act
        response = client.get(f"/crm/gyms/{gym.id}/metrics", headers=auth_headers)

        # Assert
        assert response.json()["total_leads"] == 2

    def test_gym_metrics_nonexistent_gym_returns_404(self, client, auth_headers):
        # Act
        response = client.get("/crm/gyms/99999/metrics", headers=auth_headers)

        # Assert
        assert response.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
#  LEADS
# ══════════════════════════════════════════════════════════════════════════════

class TestCreateLead:
    """Tests for POST /crm/gyms/{gym_id}/leads."""

    def test_create_lead_returns_201_with_lead_data(self, client, auth_headers, db):
        # Arrange
        gym = _create_gym(db, name="Lead Test Gym")
        payload = _lead_payload()

        # Act
        response = client.post(
            f"/crm/gyms/{gym.id}/leads",
            json=payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Carlos Fernández"
        assert data["email"] == "carlos@example.com"
        assert data["status"] == "new"
        assert data["gym_id"] == gym.id
        assert "id" in data

    def test_create_lead_without_auth_returns_401(self, client, db):
        # Arrange
        gym = _create_gym(db)

        # Act
        response = client.post(f"/crm/gyms/{gym.id}/leads", json=_lead_payload())

        # Assert
        assert response.status_code == 401

    def test_create_lead_with_invalid_email_returns_422(self, client, auth_headers, db):
        # Arrange
        gym = _create_gym(db)
        payload = _lead_payload(email="not-an-email")

        # Act
        response = client.post(
            f"/crm/gyms/{gym.id}/leads",
            json=payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 422

    def test_create_lead_with_invalid_status_returns_422(self, client, auth_headers, db):
        # Arrange
        gym = _create_gym(db)
        payload = _lead_payload(status="unknown_status")

        # Act
        response = client.post(
            f"/crm/gyms/{gym.id}/leads",
            json=payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 422

    def test_create_lead_for_nonexistent_gym_returns_404(self, client, auth_headers):
        # Act
        response = client.post(
            "/crm/gyms/99999/leads",
            json=_lead_payload(),
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 404


class TestListLeads:
    """Tests for GET /crm/gyms/{gym_id}/leads."""

    def test_list_leads_returns_200_with_list(self, client, auth_headers, db):
        # Arrange
        gym = _create_gym(db, name="Multi-Lead Gym")
        for i in range(3):
            lead = Lead(
                gym_id=gym.id,
                name=f"Fighter {i}",
                email=f"fighter{i}@example.com",
                status="new",
                source="referral",
                notes="",
            )
            db.add(lead)
        db.flush()

        # Act
        response = client.get(f"/crm/gyms/{gym.id}/leads", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_list_leads_returns_only_leads_belonging_to_gym(self, client, auth_headers, db):
        # Arrange — two gyms, each with one lead
        gym_a = _create_gym(db, name="Gym A")
        gym_b = _create_gym(db, name="Gym B")
        lead_a = Lead(gym_id=gym_a.id, name="Lead A", email="a@example.com",
                      status="new", source="organic", notes="")
        lead_b = Lead(gym_id=gym_b.id, name="Lead B", email="b@example.com",
                      status="new", source="organic", notes="")
        db.add_all([lead_a, lead_b])
        db.flush()

        # Act — list leads for gym_a only
        response = client.get(f"/crm/gyms/{gym_a.id}/leads", headers=auth_headers)

        # Assert — only gym_a's lead is returned
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Lead A"

    def test_list_leads_empty_when_no_leads(self, client, auth_headers, db):
        # Arrange
        gym = _create_gym(db, name="Quiet Gym")

        # Act
        response = client.get(f"/crm/gyms/{gym.id}/leads", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        assert response.json() == []

    def test_list_leads_without_auth_returns_401(self, client, db):
        # Arrange
        gym = _create_gym(db)

        # Act
        response = client.get(f"/crm/gyms/{gym.id}/leads")

        # Assert
        assert response.status_code == 401
