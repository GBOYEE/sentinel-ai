#!/usr/bin/env python3
"""
Generate GitHub App manifest for Sentinel AI.
Usage: python scripts/generate_github_app_manifest.py <webhook_url>
Example: python scripts/generate_github_app_manifest.py https://abc123.ngrok.io/webhook
"""

import json
import sys

def generate_manifest(webhook_url):
    return {
        "name": "Sentinel AI",
        "url": "https://github.com/GBOYEE/sentinel-ai",
        "description": "AI-powered code security and quality reviewer for GitHub pull requests",
        "public": False,
        "default_events": ["pull_request"],
        "default_permissions": {
            "contents": "read",
            "metadata": "read",
            "pull_requests": "write"
        },
        "webhook_active": True,
        "webhook_url": webhook_url
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_github_app_manifest.py <webhook_url>")
        print("Example: python scripts/generate_github_app_manifest.py https://abc123.ngrok.io/webhook")
        sys.exit(1)

    webhook = sys.argv[1]
    manifest = generate_manifest(webhook)
    print(json.dumps(manifest, indent=2))
    print("\n--- Instructions ---")
    print("1. Go to GitHub → Settings → Developer settings → GitHub Apps → New GitHub App")
    print("2. Paste the above JSON using 'Import an app manifest'")
    print("3. After creating, download the private key (.pem)")
    print("4. Note the App ID and Webhook secret")
    print("5. Place private key in sentinel-ai/secrets/gh_private_key.pem")
    print("6. Update .env with GH_APP_ID and GH_WEBHOOK_SECRET")
