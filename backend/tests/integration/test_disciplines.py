"""
Integration tests for /disciplines endpoints.
Requires the test database to be seeded with 3 disciplines and their techniques.
"""
import pytest


class TestDisciplines:
    """Tests for GET /disciplines and GET /disciplines/{id}/techniques."""

    def test_get_disciplines_returns_200(self, client, auth_headers):
        # Act
        response = client.get("/disciplines", headers=auth_headers)

        # Assert
        assert response.status_code == 200

    def test_get_disciplines_returns_exactly_three_disciplines(self, client, auth_headers):
        # Act
        response = client.get("/disciplines", headers=auth_headers)

        # Assert
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_get_disciplines_contains_expected_discipline_names(self, client, auth_headers):
        # Act
        response = client.get("/disciplines", headers=auth_headers)

        # Assert
        names = {d["name"] for d in response.json()}
        assert names == {"muay_thai", "bjj", "boxing"}

    def test_get_disciplines_each_item_has_required_fields(self, client, auth_headers):
        # Act
        response = client.get("/disciplines", headers=auth_headers)

        # Assert
        for discipline in response.json():
            assert "id" in discipline
            assert "name" in discipline
            assert "display_name" in discipline

    def test_get_techniques_for_boxing_returns_200(self, client, auth_headers, db):
        # Arrange
        from app.models.discipline import Discipline
        boxing = db.query(Discipline).filter(Discipline.name == "boxing").first()
        assert boxing is not None, "Boxing discipline must be seeded"

        # Act
        response = client.get(f"/disciplines/{boxing.id}/techniques", headers=auth_headers)

        # Assert
        assert response.status_code == 200

    def test_get_techniques_for_boxing_returns_four_techniques(self, client, auth_headers, db):
        # Arrange
        from app.models.discipline import Discipline
        boxing = db.query(Discipline).filter(Discipline.name == "boxing").first()

        # Act
        response = client.get(f"/disciplines/{boxing.id}/techniques", headers=auth_headers)

        # Assert
        techniques = response.json()
        assert len(techniques) == 4

    def test_get_techniques_for_boxing_includes_jab_and_cross(self, client, auth_headers, db):
        # Arrange
        from app.models.discipline import Discipline
        boxing = db.query(Discipline).filter(Discipline.name == "boxing").first()

        # Act
        response = client.get(f"/disciplines/{boxing.id}/techniques", headers=auth_headers)

        # Assert
        names = {t["name"] for t in response.json()}
        assert "jab" in names
        assert "cross" in names

    def test_get_techniques_for_nonexistent_discipline_returns_404(self, client, auth_headers):
        # Act
        response = client.get("/disciplines/99999/techniques", headers=auth_headers)

        # Assert
        assert response.status_code == 404

    def test_disciplines_endpoint_requires_authentication(self, client):
        # Act — no auth headers
        response = client.get("/disciplines")

        # Assert
        assert response.status_code == 401

    def test_techniques_endpoint_requires_authentication(self, client):
        # Act — no auth headers
        response = client.get("/disciplines/1/techniques")

        # Assert
        assert response.status_code == 401
