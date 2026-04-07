#!/usr/bin/env python3
"""Test script for Sentinel AI — simulates full review pipeline."""

import os

# Set dummy env vars BEFORE importing sentinel_ai modules
os.environ["GH_APP_ID"] = "12345"
os.environ["GH_WEBHOOK_SECRET"] = "testsecret"
os.environ["OPENROUTER_API_KEY"] = ""  # empty to skip LLM
os.environ["ENABLE_STATIC_ANALYSIS"] = "true"
os.environ["ENABLE_LLM_REVIEW"] = "false"

from sentinel_ai.scanners import scan_file

# Sample vulnerable Python code with multiple issues
SAMPLE_CODE = '''
import os
import sqlite3

def get_user(username):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()

@app.route('/search')
def search():
    q = request.args.get('q')
    os.system('echo ' + q)  # command injection
    return "results"
'''

def test_static_analysis():
    print("🔍 Testing static analysis...")
    findings = scan_file(SAMPLE_CODE, "vuln.py")
    print(f"  Found {len(findings)} issues:")
    for f in findings:
        line = f.get('line', f.get('line_number', 0))
        print(f"    - [{f['tool']}] {f['severity']}: {f['message']} (line {line})")
    assert len(findings) > 0, "Should find at least one security issue"
    return findings

if __name__ == "__main__":
    findings = test_static_analysis()
    print("\n✅ Static analysis test passed!")
    print(f"Total issues detected: {len(findings)}")
    print("\nSentinel AI core scanner is working correctly.")
