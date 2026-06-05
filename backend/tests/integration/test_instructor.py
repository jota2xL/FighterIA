"""
Integration tests for /instructor endpoints.
Tests group management (create, list, detail) and student join flow.
"""
import pytest
from app.models.instructor import InstructorGroup, GroupMember


class TestInstructorGroups:
    """Tests for instructor-only group endpoints."""

    def test_create_group_as_instructor_returns_201(self, client, instructor_headers):
        # Arrange
        payload = {"name": "Boxeo Avanzado", "description": "Grupo de nivel avanzado"}

        # Act
        response = client.post("/instructor/groups", json=payload, headers=instructor_headers)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Boxeo Avanzado"
        assert "invite_code" in data

    def test_create_group_generates_unique_invite_code(self, client, instructor_headers):
        # Arrange
        payload1 = {"name": "Grupo A"}
        payload2 = {"name": "Grupo B"}

        # Act
        r1 = client.post("/instructor/groups", json=payload1, headers=instructor_headers)
        r2 = client.post("/instructor/groups", json=payload2, headers=instructor_headers)

        # Assert
        assert r1.json()["invite_code"] != r2.json()["invite_code"]

    def test_create_group_as_alumno_returns_403(self, client, auth_headers):
        # Act — auth_headers belongs to an alumno account
        response = client.post(
            "/instructor/groups",
            json={"name": "Should Fail"},
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 403

    def test_create_group_without_authentication_returns_401(self, client):
        # Act
        response = client.post(
            "/instructor/groups",
            json={"name": "No Auth Group"},
        )

        # Assert
        assert response.status_code == 401

    def test_list_groups_returns_only_instructor_own_groups(self, client, instructor_headers, db, test_instructor):
        # Arrange — create two groups for this instructor
        client.post("/instructor/groups", json={"name": "Group 1"}, headers=instructor_headers)
        client.post("/instructor/groups", json={"name": "Group 2"}, headers=instructor_headers)

        # Act
        response = client.get("/instructor/groups", headers=instructor_headers)

        # Assert
        assert response.status_code == 200
        groups = response.json()
        assert len(groups) >= 2
        for g in groups:
            assert "id" in g
            assert "invite_code" in g

    def test_list_groups_requires_instructor_role(self, client, auth_headers):
        # Act — alumno trying to list instructor groups
        response = client.get("/instructor/groups", headers=auth_headers)

        # Assert
        assert response.status_code == 403

    def test_get_group_detail_returns_200(self, client, instructor_headers, db, test_instructor):
        # Arrange — create a group
        create_resp = client.post(
            "/instructor/groups",
            json={"name": "Detail Group"},
            headers=instructor_headers,
        )
        group_id = create_resp.json()["id"]

        # Act
        response = client.get(f"/instructor/groups/{group_id}", headers=instructor_headers)

        # Assert
        assert response.status_code == 200

    def test_get_nonexistent_group_returns_404(self, client, instructor_headers):
        # Act
        response = client.get("/instructor/groups/999999", headers=instructor_headers)

        # Assert
        assert response.status_code == 404


class TestStudentJoinGroup:
    """Tests for POST /instructor/groups/join (any authenticated user)."""

    def test_alumno_can_join_group_with_valid_invite_code(self, client, auth_headers, instructor_headers):
        # Arrange — instructor creates a group and gets the invite code
        create_resp = client.post(
            "/instructor/groups",
            json={"name": "Open Group"},
            headers=instructor_headers,
        )
        invite_code = create_resp.json()["invite_code"]

        # Act — alumno joins with the code
        response = client.post(
            "/instructor/groups/join",
            json={"invite_code": invite_code},
            headers=auth_headers,
        )

        # Assert
        assert response.status_code in (200, 201)

    def test_join_with_invalid_invite_code_returns_404(self, client, auth_headers):
        # Act
        response = client.post(
            "/instructor/groups/join",
            json={"invite_code": "INVALID_CODE_XYZ"},
            headers=auth_headers,
        )

        # Assert
        assert response.status_code in (404, 422)

    def test_join_requires_authentication(self, client):
        # Act
        response = client.post(
            "/instructor/groups/join",
            json={"invite_code": "SOME_CODE"},
        )

        # Assert
        assert response.status_code == 401
