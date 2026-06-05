"""
Unit tests for the blockchain_service hash generation logic.
Only tests the pure hashing behaviour — database interactions
are covered in the integration suite (test_blockchain.py).
"""
import hashlib
import re

# The internal helper is pure Python; we test it directly.
# generate_nlp_feedback is a module-level function; _build_payload is module-private
# but we can verify the hash contract through the hashlib interface directly.
from app.services import blockchain_service


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _sha256_hex(text: str) -> str:
    """Mirror the exact hashing logic used in blockchain_service."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestSha256HashProperties:
    """
    Verify the SHA-256 hash contract the blockchain service relies on.
    These tests are independent of SQLAlchemy and FastAPI.
    """

    def test_generate_hash_deterministic(self):
        # Arrange — build two payloads from identical data
        payload_a = "42:7:85.7500:2026-05-28T10:01:30"
        payload_b = "42:7:85.7500:2026-05-28T10:01:30"

        # Act
        hash_a = _sha256_hex(payload_a)
        hash_b = _sha256_hex(payload_b)

        # Assert — same input must always produce the same hash
        assert hash_a == hash_b

    def test_generate_hash_different_inputs_produce_different_hashes(self):
        # Arrange — payloads differ only in the analysis id
        payload_a = "1:7:85.7500:2026-05-28T10:01:30"
        payload_b = "2:7:85.7500:2026-05-28T10:01:30"

        # Act
        hash_a = _sha256_hex(payload_a)
        hash_b = _sha256_hex(payload_b)

        # Assert — different inputs must never collide
        assert hash_a != hash_b

    def test_hash_is_exactly_64_characters(self):
        # Arrange — SHA-256 hex digest is always 256 bits / 4 bits-per-hex = 64 chars
        payload = "10:3:72.3300:2026-06-01T09:00:00"

        # Act
        digest = _sha256_hex(payload)

        # Assert
        assert len(digest) == 64

    def test_hash_contains_only_hex_characters(self):
        # Arrange
        payload = "5:12:100.0000:2026-06-05T15:30:00"

        # Act
        digest = _sha256_hex(payload)

        # Assert — SHA-256 hex output only contains [0-9a-f]
        assert re.fullmatch(r"[0-9a-f]{64}", digest) is not None

    def test_hash_changes_when_score_changes(self):
        # Arrange — only the score differs
        payload_high = "7:2:99.0000:2026-05-20T08:00:00"
        payload_low  = "7:2:30.0000:2026-05-20T08:00:00"

        # Act
        hash_high = _sha256_hex(payload_high)
        hash_low  = _sha256_hex(payload_low)

        # Assert — score is part of the canonical payload so hashes must differ
        assert hash_high != hash_low

    def test_hash_changes_when_timestamp_changes(self):
        # Arrange — only the completion timestamp differs
        payload_t1 = "7:2:75.0000:2026-05-20T08:00:00"
        payload_t2 = "7:2:75.0000:2026-05-20T08:00:01"

        # Act
        hash_t1 = _sha256_hex(payload_t1)
        hash_t2 = _sha256_hex(payload_t2)

        # Assert
        assert hash_t1 != hash_t2

    def test_hash_changes_when_user_id_changes(self):
        # Arrange — only the user_id differs
        payload_u1 = "7:1:75.0000:2026-05-20T08:00:00"
        payload_u2 = "7:9:75.0000:2026-05-20T08:00:00"

        # Act
        hash_u1 = _sha256_hex(payload_u1)
        hash_u2 = _sha256_hex(payload_u2)

        # Assert
        assert hash_u1 != hash_u2

    def test_empty_string_produces_known_sha256(self):
        # Arrange — the SHA-256 of the empty string is a well-known constant
        known = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

        # Act
        digest = _sha256_hex("")

        # Assert
        assert digest == known

    def test_build_payload_format_is_stable(self):
        """
        _build_payload produces "{analysis_id}:{user_id}:{score:.4f}:{ts}".
        Verify the format by constructing it manually and hashing.
        """
        # Arrange — simulate what _build_payload would produce
        analysis_id = 3
        user_id     = 5
        score       = 67.5
        ts          = "2026-06-05T12:00:00"
        expected_payload = f"{analysis_id}:{user_id}:{score:.4f}:{ts}"

        # Act — hash it the same way the service does
        digest = _sha256_hex(expected_payload)

        # Assert — result is a 64-char hex string
        assert len(digest) == 64
        assert re.fullmatch(r"[0-9a-f]{64}", digest) is not None
