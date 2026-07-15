"""Static code analysis tools."""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def run_bandit(code: str) -> list[dict[str, Any]]:
    """Run bandit security scanner on Python code.

    Returns [] if bandit is not installed (so callers can degrade gracefully).
    """
    if not shutil.which("bandit"):
        return []
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        try:
            result = subprocess.run(
                ["bandit", "-f", "json", "-r", f.name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            # Parse JSON output
            output = json.loads(result.stdout) if result.stdout else {"results": []}
            findings = []
            for item in output.get("results", []):
                findings.append({
                    "tool": "bandit",
                    "severity": item.get("issue_severity", "medium"),
                    "line": item.get("line_number", 0),
                    "message": item.get("issue_text", ""),
                    "code": item.get("code", ""),
                    "test_id": item.get("test_id", ""),
                })
            return findings
        except json.JSONDecodeError:
            return []
        except Exception as e:
            return [{"tool": "bandit", "severity": "error", "message": str(e)}]
        finally:
            Path(f.name).unlink(missing_ok=True)


def run_flake8(code: str) -> list[dict[str, Any]]:
    """Run flake8 for code quality issues. Returns [] if flake8 not installed."""
    if not shutil.which("flake8"):
        return []
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        try:
            result = subprocess.run(
                ["flake8", "--format=json", f.name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = json.loads(result.stdout) if result.stdout else []
            findings = []
            for item in output:
                findings.append({
                    "tool": "flake8",
                    "severity": "low",
                    "line": item.get("line_number", 0),
                    "message": item.get("text", ""),
                    "code": "",
                })
            return findings
        except json.JSONDecodeError:
            return []
        except Exception as e:
            return [{"tool": "flake8", "severity": "error", "message": str(e)}]
        finally:
            Path(f.name).unlink(missing_ok=True)


def run_semgrep(code: str) -> list[dict[str, Any]]:
    """Run semgrep for pattern-based security scanning (if available)."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            result = subprocess.run(
                ["semgrep", "--config=auto", "--json", f.name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = json.loads(result.stdout) if result.stdout else {"results": []}
            findings = []
            for item in output.get("results", []):
                findings.append({
                    "tool": "semgrep",
                    "severity": item.get("severity", "medium"),
                    "line": item.get("start", {}).get("line", 0),
                    "message": item.get("extra", {}).get("message", ""),
                    "code": "",
                })
            return findings
    except FileNotFoundError:
        return []  # semgrep not installed
    except Exception as e:
        return [{"tool": "semgrep", "severity": "error", "message": str(e)}]
    finally:
        Path(f.name).unlink(missing_ok=True)


def scan_file(code: str, filename: str = "code.py") -> list[dict[str, Any]]:
    """Run all static analyzers on a code snippet."""
    all_findings = []
    if filename.endswith(".py"):
        all_findings.extend(run_bandit(code))
        all_findings.extend(run_flake8(code))
        all_findings.extend(run_semgrep(code))
    return all_findings
