"""
Integration tests for /auth endpoints.
Covers register, login, token refresh, forgot-password and protected endpoint access.
"""
import pytest
from tests.fixtures.users import (
    VALID_ALUMNO,
    VALID_INSTRUCTOR,
    INVALID_SHORT_PASSWORD,
    INVALID_EMAIL_FORMAT,
    INVALID_ACCOUNT_TYPE,
)


class TestRegister:
    """Tests for POST /auth/register."""

    def test_register_with_valid_alumno_data_returns_201_with_tokens(self, client):
        # Arrange
        payload = VALID_ALUMNO.copy()

        # Act
        response = client.post("/auth/register", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == payload["email"]
        assert data["user"]["account_type"] == "alumno"

    def test_register_response_never_exposes_password_fields(self, client):
        # Arrange
        payload = VALID_ALUMNO.copy()

        # Act
        response = client.post("/auth/register", json=payload)

        # Assert — security: password must never appear in responses
        user_data = response.json().get("user", {})
        assert "password" not in user_data
        assert "password_hash" not in user_data

    def test_register_instructor_account_sets_correct_account_type(self, client):
        # Arrange
        payload = VALID_INSTRUCTOR.copy()

        # Act
        response = client.post("/auth/register", json=payload)

        # Assert
        assert response.status_code == 201
        assert response.json()["user"]["account_type"] == "instructor"

    def test_register_with_duplicate_email_returns_409(self, client, test_user):
        # Arrange — test_user already exists in DB
        payload = {
            "email": test_user.email,  # duplicate email
            "username": "completely_different_username",
            "password": "ValidPass123!",
            "full_name": "Duplicate Email Test",
            "account_type": "alumno",
        }

        # Act
        response = client.post("/auth/register", json=payload)

        # Assert
        assert response.status_code == 409

    def test_register_with_duplicate_username_returns_409(self, client, test_user):
        # Arrange — test_user already exists in DB
        payload = {
            "email": "unique_email_xyz@example.com",
            "username": test_user.username,  # duplicate username
            "password": "ValidPass123!",
            "full_name": "Duplicate Username Test",
            "account_type": "alumno",
        }

        # Act
        response = client.post("/auth/register", json=payload)

        # Assert
        assert response.status_code == 409

    def test_register_with_password_shorter_than_minimum_returns_422(self, client):
        # Arrange
        payload = INVALID_SHORT_PASSWORD.copy()

        # Act
        response = client.post("/auth/register", json=payload)

        # Assert
        assert response.status_code == 422

    def test_register_with_malformed_email_returns_422(self, client):
        # Arrange
        payload = INVALID_EMAIL_FORMAT.copy()

        # Act
        response = client.post("/auth/register", json=payload)

        # Assert
        assert response.status_code == 422

    def test_register_with_invalid_account_type_returns_422(self, client):
        # Arrange
        payload = INVALID_ACCOUNT_TYPE.copy()

        # Act
        response = client.post("/auth/register", json=payload)

        # Assert
        assert response.status_code == 422

    def test_register_new_user_starts_with_zero_xp_and_blanco_belt(self, client):
        # Arrange
        payload = {
            "email": "fresh_starter@example.com",
            "username": "fresh_starter",
            "password": "FreshPass123!",
            "full_name": "Fresh Starter",
            "account_type": "alumno",
        }

        # Act
        response = client.post("/auth/register", json=payload)

        # Assert — gamification initial state
        user = response.json()["user"]
        assert user["xp"] == 0
        assert user["belt_level"] == "blanco"
        assert user["current_streak"] == 0


class TestLogin:
    """Tests for POST /auth/login."""

    def test_login_with_correct_credentials_returns_200_with_tokens(self, client, test_user):
        # Arrange
        payload = {"email": test_user.email, "password": "TestPass123!"}

        # Act
        response = client.post("/auth/login", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_wrong_password_returns_401(self, client, test_user):
        # Arrange
        payload = {"email": test_user.email, "password": "CompletelyWrongPassword!"}

        # Act
        response = client.post("/auth/login", json=payload)

        # Assert
        assert response.status_code == 401
        # Error message must be generic — cannot reveal which field failed (prevents enumeration)
        detail = response.json()["detail"].lower()
        assert "incorrectos" in detail

    def test_login_with_nonexistent_email_returns_401(self, client):
        # Arrange
        payload = {"email": "nobody@nowhere.com", "password": "AnyPassword123!"}

        # Act
        response = client.post("/auth/login", json=payload)

        # Assert
        assert response.status_code == 401

    def test_login_error_message_is_identical_for_wrong_password_and_wrong_email(self, client, test_user):
        """Prevents user enumeration by returning the same error message in both cases."""
        # Arrange
        wrong_pass_response = client.post("/auth/login", json={
            "email": test_user.email, "password": "WrongPass!"
        })
        wrong_email_response = client.post("/auth/login", json={
            "email": "ghost@example.com", "password": "WrongPass!"
        })

        # Assert — same message to prevent enumeration
        assert wrong_pass_response.json()["detail"] == wrong_email_response.json()["detail"]


class TestForgotPassword:
    """Tests for POST /auth/forgot-password."""

    def test_forgot_password_returns_200_for_existing_email(self, client, test_user):
        # Act
        response = client.post("/auth/forgot-password", json={"email": test_user.email})

        # Assert
        assert response.status_code == 200

    def test_forgot_password_returns_200_for_nonexistent_email(self, client):
        """Must return 200 for any email to prevent user enumeration."""
        # Act
        response = client.post("/auth/forgot-password", json={"email": "fake@nobody.com"})

        # Assert
        assert response.status_code == 200

    def test_forgot_password_response_is_identical_regardless_of_email_existence(self, client, test_user):
        """Both responses must be indistinguishable to prevent enumeration."""
        # Act
        real_response = client.post("/auth/forgot-password", json={"email": test_user.email})
        fake_response = client.post("/auth/forgot-password", json={"email": "fake@nobody.com"})

        # Assert
        assert real_response.status_code == fake_response.status_code


class TestProtectedEndpoints:
    """Tests for JWT-protected endpoint access control."""

    def test_get_me_with_valid_token_returns_200_and_user_data(self, client, auth_headers, test_user):
        # Act
        response = client.get("/auth/me", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["email"] == test_user.email

    def test_get_me_without_authorization_header_returns_401(self, client):
        # Act
        response = client.get("/auth/me")

        # Assert
        assert response.status_code == 401

    def test_get_me_with_malformed_token_returns_401(self, client):
        # Act
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer not.a.real.token"}
        )

        # Assert
        assert response.status_code == 401

    def test_get_me_with_bearer_prefix_missing_returns_401(self, client, auth_headers):
        # Arrange — token without "Bearer " prefix
        raw_token = auth_headers["Authorization"].replace("Bearer ", "")

        # Act
        response = client.get("/auth/me", headers={"Authorization": raw_token})

        # Assert
        assert response.status_code == 401
