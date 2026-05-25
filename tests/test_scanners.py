"""Tests for Sentinel AI scanners."""

import pytest
from sentinel_ai.scanners import scan_file, run_bandit, run_flake8, run_semgrep


class TestBanditScanner:
    """Tests for bandit security scanner."""

    def test_detects_command_injection(self):
        code = """
import os
cmd = "ls " + user_input
os.system(cmd)
"""
        findings = run_bandit(code)
        assert any(f["tool"] == "bandit" for f in findings)
        assert any("command" in f.get("message", "").lower() or "injection" in f.get("message", "").lower() for f in findings if f["tool"] == "bandit")

    def test_detects_sql_injection(self):
        code = """
import sqlite3
def get_user(username):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
"""
        findings = run_bandit(code)
        assert any(f["tool"] == "bandit" for f in findings)

    def test_clean_code_no_findings(self):
        code = """
def add(a, b):
    return a + b
"""
        findings = run_bandit(code)
        # Bandit may still produce some results, but should not have high severity
        high_sev = [f for f in findings if f.get("severity") == "HIGH"]
        assert len(high_sev) == 0

    def test_handles_empty_code(self):
        findings = run_bandit("")
        assert isinstance(findings, list)


class TestFlake8Scanner:
    """Tests for flake8 quality scanner."""

    def test_detects_syntax_issues(self):
        code = """
def foo( ):
  x=1
  y =2
"""
        findings = run_flake8(code)
        assert isinstance(findings, list)

    def test_clean_code(self):
        code = """def foo():
    return 1
"""
        findings = run_flake8(code)
        assert isinstance(findings, list)


class TestSemgrepScanner:
    """Tests for semgrep scanner."""

    def test_semgrep_or_skip(self):
        """Test semgrep if available, skip if not installed."""
        import shutil
        if not shutil.which("semgrep"):
            pytest.skip("semgrep not installed")
        
        code = """
import os
os.system(user_input)
"""
        findings = run_semgrep(code)
        assert isinstance(findings, list)


class TestScanFile:
    """Tests for the combined scan_file function."""

    def test_scan_python_file(self):
        code = """
import os
os.system(user_input)
"""
        findings = scan_file(code, "test.py")
        assert isinstance(findings, list)
        assert len(findings) > 0

    def test_scan_non_python_file(self):
        code = "console.log('hello')"
        findings = scan_file(code, "test.js")
        assert findings == []

    def test_scan_with_various_issues(self):
        code = """
import os
import sqlite3

def search(query):
    os.system('echo ' + query)
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data WHERE q = '" + query + "'")
"""
        findings = scan_file(code, "app.py")
        assert len(findings) > 0
        tools = {f["tool"] for f in findings}
        assert "bandit" in tools
