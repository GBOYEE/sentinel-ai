"""Tests for scanners module."""

from sentinel_ai.scanners import scan_file

def test_scan_file_with_simple_vuln():
    code = """
import os
cmd = "ls " + user_input
os.system(cmd)  # command injection
"""
    findings = scan_file(code, "test.py")
    # bandit should catch this as a security issue
    assert any(f["tool"] == "bandit" for f in findings)
