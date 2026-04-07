"""GitHub App authentication utilities."""

import time
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from config import GH_APP_ID, GH_APP_PRIVATE_KEY, GH_WEBHOOK_SECRET  # noqa: F401


def create_jwt():
    """Create a JWT for GitHub App authentication."""
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + (10 * 60),
        "iss": GH_APP_ID,
    }
    with open(GH_APP_PRIVATE_KEY, "r") as f:
        private_key = serialization.load_pem_private_key(
            f.read().encode(), password=None
        )
    token = jwt.encode(payload, private_key, algorithm="RS256")
    return token


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature (HMAC SHA256)."""
    import hmac
    import hashlib

    expected = "sha256=" + hmac.new(
        GH_WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
