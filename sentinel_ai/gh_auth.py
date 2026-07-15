"""GitHub App authentication utilities."""

import logging
import time

import httpx
import jwt
from cryptography.hazmat.primitives import serialization

from sentinel_ai.config import GH_APP_ID, GH_APP_PRIVATE_KEY, GH_WEBHOOK_SECRET

logger = logging.getLogger(__name__)


def create_jwt() -> str:
    """Create a JWT for GitHub App authentication."""
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + (10 * 60),
        "iss": str(GH_APP_ID),
    }
    try:
        with open(GH_APP_PRIVATE_KEY) as f:
            private_key_data = f.read()
        private_key = serialization.load_pem_private_key(
            private_key_data.encode(), password=None
        )
        # Cast to RSAPrivateKey for jwt.encode
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
        if not isinstance(private_key, RSAPrivateKey):
            raise ValueError("Private key must be RSA for GitHub App JWT")
        token = jwt.encode(payload, private_key, algorithm="RS256")
        return token
    except FileNotFoundError:
        logger.error(f"Private key not found at {GH_APP_PRIVATE_KEY}")
        raise
    except Exception as e:
        logger.error(f"Failed to create JWT: {e}")
        raise


async def get_installation_token(installation_id: int) -> str | None:
    """Exchange JWT for an installation access token.

    This is the critical step: the JWT identifies the app,
    but the installation token is needed to act on behalf of
    a specific organization/user who installed the app.
    """
    jwt_token = create_jwt()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, timeout=30)
            if resp.status_code == 201:
                token = resp.json()["token"]
                logger.info(f"Got installation token for installation {installation_id}")
                return token
            else:
                logger.error(f"Failed to get installation token: {resp.status_code} {resp.text}")
                return None
    except Exception as e:
        logger.error(f"Error getting installation token: {e}")
        return None


async def get_installation_id(owner: str, repo: str) -> int | None:
    """Get the installation ID for a given repo."""
    jwt_token = create_jwt()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/installation"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                return resp.json()["id"]
            else:
                logger.error(f"Failed to get installation: {resp.status_code} {resp.text}")
                return None
    except Exception as e:
        logger.error(f"Error getting installation: {e}")
        return None


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature (HMAC SHA256)."""
    import hashlib
    import hmac

    if not GH_WEBHOOK_SECRET:
        logger.warning("GH_WEBHOOK_SECRET not set, skipping verification")
        return False

    expected = "sha256=" + hmac.new(
        GH_WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
