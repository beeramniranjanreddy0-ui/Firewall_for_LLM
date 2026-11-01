from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.prompt_log import PromptLog
from app.models.security_event import SecurityEvent


def get_firewall_stats(db: Session) -> dict:
    total_prompts = db.scalar(select(func.count()).select_from(PromptLog)) or 0
    allowed_prompts = db.scalar(
        select(func.count()).select_from(PromptLog).where(PromptLog.decision == "ALLOWED")
    ) or 0
    blocked_prompts = db.scalar(
        select(func.count()).select_from(PromptLog).where(PromptLog.decision == "BLOCKED")
    ) or 0
    high_risk_prompts = db.scalar(
        select(func.count()).select_from(PromptLog).where(PromptLog.risk_level == "HIGH")
    ) or 0
    total_events = db.scalar(select(func.count()).select_from(SecurityEvent)) or 0

    risk_distribution = {
        "SAFE": db.scalar(select(func.count()).select_from(PromptLog).where(PromptLog.risk_level == "SAFE")) or 0,
        "GOOD": db.scalar(select(func.count()).select_from(PromptLog).where(PromptLog.risk_level == "GOOD")) or 0,
        "MEDIUM": db.scalar(select(func.count()).select_from(PromptLog).where(PromptLog.risk_level == "MEDIUM")) or 0,
        "HIGH": db.scalar(select(func.count()).select_from(PromptLog).where(PromptLog.risk_level == "HIGH")) or 0,
    }

    since = datetime.now(timezone.utc) - timedelta(days=6)
    recent_logs = db.scalars(select(PromptLog).where(PromptLog.timestamp >= since)).all()
    day_counts: Counter[str] = Counter()
    blocked_counts: Counter[str] = Counter()
    for log in recent_logs:
        label = log.timestamp.date().isoformat()
        day_counts[label] += 1
        if log.decision == "BLOCKED":
            blocked_counts[label] += 1

    recent_activity = []
    for days_back in range(6, -1, -1):
        label = (datetime.now(timezone.utc) - timedelta(days=days_back)).date().isoformat()
        recent_activity.append(
            {
                "date": label,
                "total": day_counts[label],
                "blocked": blocked_counts[label],
            }
        )

    return {
        "total_prompts": total_prompts,
        "allowed_prompts": allowed_prompts,
        "blocked_prompts": blocked_prompts,
        "high_risk_prompts": high_risk_prompts,
        "total_security_events": total_events,
        "risk_distribution": risk_distribution,
        "recent_activity": recent_activity,
    }
