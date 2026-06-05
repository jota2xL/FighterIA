"""
Unit tests for utils.security — JWT creation, decoding and password hashing.
"""
import pytest
import time
from jose import JWTError

from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TestPasswordHashing:
    """Tests for bcrypt password hashing utilities."""

    def test_hash_password_returns_string_different_from_plaintext(self):
        # Arrange
        raw = "MySecurePassword123!"

        # Act
        hashed = hash_password(raw)

        # Assert
        assert hashed != raw
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_password_returns_true_for_correct_password(self):
        # Arrange
        raw = "MySecurePassword123!"
        hashed = hash_password(raw)

        # Act / Assert
        assert verify_password(raw, hashed) is True

    def test_verify_password_returns_false_for_wrong_password(self):
        # Arrange
        hashed = hash_password("CorrectPassword123!")

        # Act / Assert
        assert verify_password("WrongPassword!", hashed) is False

    def test_same_password_produces_different_hashes_each_time(self):
        # Arrange — bcrypt uses a random salt each time
        raw = "SamePassword123!"
        hash1 = hash_password(raw)
        hash2 = hash_password(raw)

        # Assert — hashes differ due to unique salts
        assert hash1 != hash2

    def test_empty_password_still_hashes_without_error(self):
        # Act
        hashed = hash_password("")

        # Assert
        assert isinstance(hashed, str)
        assert verify_password("", hashed) is True


class TestJWTTokens:
    """Tests for JWT access and refresh token creation and validation."""

    def test_create_access_token_returns_string(self):
        # Act
        token = create_access_token({"sub": "42"})

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token_returns_correct_subject(self):
        # Arrange
        token = create_access_token({"sub": "99"})

        # Act
        payload = decode_token(token)

        # Assert
        assert payload["sub"] == "99"
        assert payload["type"] == "access"

    def test_create_refresh_token_has_different_type_than_access(self):
        # Arrange
        access = create_access_token({"sub": "1"})
        refresh = create_refresh_token({"sub": "1"})

        # Act
        access_payload = decode_token(access)
        refresh_payload = decode_token(refresh)

        # Assert
        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"

    def test_decode_token_raises_on_tampered_token(self):
        # Arrange
        token = create_access_token({"sub": "1"})
        tampered = token[:-5] + "XXXXX"

        # Act / Assert
        with pytest.raises(JWTError):
            decode_token(tampered)

    def test_decode_token_raises_on_completely_invalid_string(self):
        # Act / Assert
        with pytest.raises(JWTError):
            decode_token("not.a.jwt.token.at.all")

    def test_access_token_contains_exp_field(self):
        # Arrange
        token = create_access_token({"sub": "5"})

        # Act
        payload = decode_token(token)

        # Assert
        assert "exp" in payload
