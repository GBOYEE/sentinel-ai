"""Tests for Sentinel AI models and database."""

import os

import pytest

# Use SQLite for testing
os.environ["DATABASE_URL"] = "sqlite:///./test_sentinel.db"

from sentinel_ai.models import (
    add_finding,
    complete_review,
    create_review,
    get_recent_reviews,
    get_review_stats,
    init_db,
)


class TestDatabaseModels:
    """Test database operations."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        init_db()
        yield
        # Cleanup
        try:
            os.remove("test_sentinel.db")
        except FileNotFoundError:
            pass

    def test_create_review(self):
        review = create_review("testowner", "testrepo", 1, "abc123")
        assert review.id is not None
        assert review.owner == "testowner"
        assert review.repo == "testrepo"
        assert review.pull_number == 1
        assert review.status == "pending"

    def test_add_finding(self):
        review = create_review("testowner", "testrepo", 1, "abc123")
        finding = add_finding(
            review_id=review.id,
            filename="app.py",
            line=10,
            severity="high",
            category="security",
            description="SQL injection vulnerability",
            suggestion="Use parameterized queries",
            tool="bandit",
        )
        assert finding.id is not None
        assert finding.filename == "app.py"
        assert finding.severity == "high"

    def test_complete_review(self):
        review = create_review("testowner", "testrepo", 1, "abc123")
        add_finding(review.id, "app.py", 10, "high", "security", "SQL injection", "Use params", "bandit")
        add_finding(review.id, "app.py", 20, "medium", "quality", "Unused import", "Remove it", "flake8")

        complete_review(review.id)

        # Re-fetch to check
        reviews = get_recent_reviews(10)
        assert len(reviews) > 0
        r = reviews[0]
        assert r["status"] == "completed"
        assert r["total_findings"] == 2

    def test_get_recent_reviews(self):
        for i in range(3):
            create_review("owner", f"repo{i}", i, f"sha{i}")

        reviews = get_recent_reviews(10)
        assert len(reviews) >= 3

    def test_get_review_stats(self):
        review = create_review("testowner", "testrepo", 1, "abc123")
        add_finding(review.id, "app.py", 10, "critical", "security", "RCE", "Fix it", "bandit")
        complete_review(review.id)

        stats = get_review_stats()
        assert stats["total_reviews"] >= 1
        assert stats["total_findings"] >= 1
