from __future__ import annotations

from pydantic import BaseModel


class RiskDistribution(BaseModel):
    SAFE: int
    GOOD: int
    MEDIUM: int
    HIGH: int


class RecentActivityItem(BaseModel):
    date: str
    total: int
    blocked: int


class FirewallStats(BaseModel):
    total_prompts: int
    allowed_prompts: int
    blocked_prompts: int
    high_risk_prompts: int
    total_security_events: int
    risk_distribution: RiskDistribution
    recent_activity: list[RecentActivityItem]
