"""Database models for Sentinel AI findings and reviews."""

from datetime import datetime
from typing import Optional, List
import json

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime,
    Float, Boolean, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import func

from sentinel_ai.config import DATABASE_URL

Base = declarative_base()


class Review(Base):
    """A review performed on a PR."""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner = Column(String(255), nullable=False)
    repo = Column(String(255), nullable=False)
    pull_number = Column(Integer, nullable=False)
    commit_sha = Column(String(40), nullable=False)
    status = Column(String(20), default="pending")  # pending, completed, error
    total_findings = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    findings = relationship("Finding", back_populates="review", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_repo_pr", "owner", "repo", "pull_number"),
        Index("idx_created", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "owner": self.owner,
            "repo": self.repo,
            "pull_number": self.pull_number,
            "commit_sha": self.commit_sha,
            "status": self.status,
            "total_findings": self.total_findings,
            "severity_breakdown": {
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": self.medium_count,
                "low": self.low_count,
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class Finding(Base):
    """A single finding from a review."""
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    line = Column(Integer, default=0)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low, info
    category = Column(String(50), nullable=False)  # security, quality, performance, best-practice
    description = Column(Text, nullable=False)
    suggestion = Column(Text, nullable=True)
    tool = Column(String(50), nullable=False)  # bandit, flake8, semgrep, llm
    created_at = Column(DateTime, default=datetime.utcnow)

    review = relationship("Review", back_populates="findings")

    __table_args__ = (
        Index("idx_review", "review_id"),
        Index("idx_severity", "severity"),
        Index("idx_tool", "tool"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "line": self.line,
            "severity": self.severity,
            "category": self.category,
            "description": self.description,
            "suggestion": self.suggestion,
            "tool": self.tool,
        }


# ── Database helpers ─────────────────────────────────────────

_engine = None
_Session = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, echo=False)
    return _engine


def get_session():
    global _Session
    if _Session is None:
        _Session = sessionmaker(bind=get_engine())
    return _Session()


def init_db():
    """Create all tables."""
    Base.metadata.create_all(get_engine())


def create_review(owner: str, repo: str, pull_number: int, commit_sha: str) -> Review:
    """Create a new review record."""
    session = get_session()
    review = Review(
        owner=owner,
        repo=repo,
        pull_number=pull_number,
        commit_sha=commit_sha,
        status="pending",
    )
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


def add_finding(review_id: int, filename: str, line: int, severity: str,
                category: str, description: str, suggestion: str, tool: str) -> Finding:
    """Add a finding to a review."""
    session = get_session()
    finding = Finding(
        review_id=review_id,
        filename=filename,
        line=line,
        severity=severity,
        category=category,
        description=description,
        suggestion=suggestion,
        tool=tool,
    )
    session.add(finding)
    session.commit()
    session.refresh(finding)
    return finding


def complete_review(review_id: int, error: Optional[str] = None):
    """Mark a review as completed."""
    session = get_session()
    review = session.query(Review).filter_by(id=review_id).first()
    if review:
        review.status = "error" if error else "completed"
        review.completed_at = datetime.utcnow()
        review.error_message = error
        
        # Count findings by severity
        findings = session.query(Finding).filter_by(review_id=review_id).all()
        review.total_findings = len(findings)
        review.critical_count = sum(1 for f in findings if f.severity == "critical")
        review.high_count = sum(1 for f in findings if f.severity == "high")
        review.medium_count = sum(1 for f in findings if f.severity == "medium")
        review.low_count = sum(1 for f in findings if f.severity in ("low", "info"))
        
        session.commit()


def get_recent_reviews(limit: int = 50) -> List[dict]:
    """Get recent reviews."""
    session = get_session()
    reviews = session.query(Review).order_by(Review.created_at.desc()).limit(limit).all()
    return [r.to_dict() for r in reviews]


def get_review_stats() -> dict:
    """Get aggregate statistics."""
    session = get_session()
    total_reviews = session.query(func.count(Review.id)).filter(Review.status == "completed").scalar()
    total_findings = session.query(func.count(Finding.id)).scalar()
    
    severity_counts = dict(
        session.query(Finding.severity, func.count(Finding.id))
        .group_by(Finding.severity)
        .all()
    )
    
    tool_counts = dict(
        session.query(Finding.tool, func.count(Finding.id))
        .group_by(Finding.tool)
        .all()
    )
    
    return {
        "total_reviews": total_reviews,
        "total_findings": total_findings,
        "severity_breakdown": severity_counts,
        "tool_breakdown": tool_counts,
    }
