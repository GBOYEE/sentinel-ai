"""Tests for Sentinel AI GitHub authentication."""

import os

# Set test env before importing
os.environ["GH_APP_ID"] = "12345"
os.environ["GH_WEBHOOK_SECRET"] = "testsecret"
os.environ["GH_APP_PRIVATE_KEY"] = "/tmp/test_key.pem"

from sentinel_ai.gh_auth import verify_webhook_signature


class TestWebhookVerification:
    """Test webhook signature verification."""

    def test_rejects_invalid_signature(self):
        payload = b'{"test": "data"}'
        signature = "sha256=" + "0" * 64
        assert not verify_webhook_signature(payload, signature)

    def test_accepts_valid_signature(self):
        import hashlib
        import hmac
        payload = b'{"test": "data"}'
        expected = "sha256=" + hmac.new(
            b"testsecret", payload, hashlib.sha256
        ).hexdigest()
        assert verify_webhook_signature(payload, expected)

    def test_rejects_tampered_payload(self):
        import hashlib
        import hmac
        payload = b'{"test": "data"}'
        signature = "sha256=" + hmac.new(
            b"testsecret", payload, hashlib.sha256
        ).hexdigest()
        # Tampered payload
        assert not verify_webhook_signature(b'{"test": "tampered"}', signature)

    def test_empty_secret_rejects_all(self):
        """With empty secret, should reject."""
        original = os.environ.get("GH_WEBHOOK_SECRET")
        os.environ["GH_WEBHOOK_SECRET"] = ""
        assert not verify_webhook_signature(b'{"test": "data"}', "sha256=abc")
        os.environ["GH_WEBHOOK_SECRET"] = original or "testsecret"
