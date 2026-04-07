#!/usr/bin/env python3
"""
Generate GitHub App manifest for Sentinel AI.
Run this to get the JSON configuration to create the GitHub App quickly.
"""

import json
import base64
from datetime import datetime, timedelta

def generate_github_app_manifest(
    name="Sentinel AI",
    webhook_url="https://your-domain.com/webhook",
    app_id=None,
    private_key_path=None
):
    """Create a GitHub App configuration manifest."""

    manifest = {
        "name": name,
        "url": "https://github.com/GBOYEE/sentinel-ai",
        "description": "AI-powered code security and quality reviewer for GitHub pull requests",
        "public": False,  # private app
        "default_events": ["pull_request"],
        "default_permissions": {
            "contents": "read",
            "metadata": "read",
            "pull_requests": "write"
        },
        "webhook_active": True,
        "webhook_url": webhook_url
    }

    return manifest

if __name__ == "__main__":
    print("GitHub App Manifest for Sentinel AI")
    print("="*60)
    print("\nCopy this JSON when creating the GitHub App:\n")

    # Prompt for webhook URL
    webhook = input("Enter your webhook URL (e.g., https://abc123.ngrok.io/webhook): ").strip()
    if not webhook:
        webhook = "https://your-domain.com/webhook"

    manifest = generate_github_app_manifest(webhook_url=webhook)
    print(json.dumps(manifest, indent=2))

    print("\n" + "="*60)
    print("After creating the App:")
    print("1. Download the private key (.pem)")
    print("2. Note the App ID")
    print("3. Copy the Webhook secret")
    print("4. Place the private key in sentinel-ai/secrets/gh_private_key.pem")
    print("5. Update .env with GH_APP_ID and GH_WEBHOOK_SECRET")
