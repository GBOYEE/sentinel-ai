#!/usr/bin/env python3
"""
Integration test for Sentinel AI — simulates GitHub webhook.

This script:
1. Creates a fake GitHub webhook payload
2. Calls the FastAPI app directly (bypassing HTTP)
3. Validates that the review pipeline is triggered

Usage:
  python test_integration.py
"""

import os
import sys
import json
import asyncio
from unittest.mock import patch, MagicMock

# Set test env
os.environ["GH_APP_ID"] = "12345"
os.environ["GH_WEBHOOK_SECRET"] = "testsecret"
os.environ["ENABLE_STATIC_ANALYSIS"] = "true"
os.environ["ENABLE_LLM_REVIEW"] = "false"

# Add sentinel-ai to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sentinel_ai.main import app, process_pull_request
from sentinel_ai.gh_auth import verify_webhook_signature

def test_webhook_signature():
    print("🔐 Testing webhook signature verification...")
    payload = b'{"test": "data"}'
    signature = "sha256=" + "0" * 64  # fake signature
    # With fake secret, verification will fail
    assert not verify_webhook_signature(payload, signature), "Should reject invalid signature"
    print("  ✅ Signature verification works")

def test_app_startup():
    print("\n🚀 Testing FastAPI app startup...")
    assert app.title == "Sentinel AI"
    routes = [r.path for r in app.routes]
    assert "/webhook" in routes
    assert "/health" in routes
    print(f"  ✅ App started, routes: {routes}")

def test_process_pull_request_mock():
    print("\n🔄 Testing PR processing (mocked)...")
    # Mock httpx calls to GitHub API
    with patch('sentinel_ai.main.httpx') as mock_httpx:
        mock_httpx.get.return_value.status_code = 200
        mock_httpx.get.return_value.json.return_value = [{
            "filename": "test.py",
            "patch": "def foo():\n    return 1"
        }]
        mock_httpx.post.return_value.status_code = 201

        # Call the processing function directly
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            process_pull_request("testowner", "testrepo", 1, "abc123")
        )

        # Verify GitHub API was called
        mock_httpx.get.assert_called()
        mock_httpx.post.assert_called()
        print("  ✅ PR processing pipeline executed")
        print("  ✅ GitHub API calls made")

if __name__ == "__main__":
    print("="*60)
    print("SENTINEL AI INTEGRATION TEST")
    print("="*60)
    try:
        test_webhook_signature()
        test_app_startup()
        test_process_pull_request_mock()
        print("\n" + "="*60)
        print("✅ ALL INTEGRATION TESTS PASSED")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
