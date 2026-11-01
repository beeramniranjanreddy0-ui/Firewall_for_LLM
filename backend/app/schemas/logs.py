from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PromptLogDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    prompt: str
    response: str | None
    risk_score: int
    risk_level: str
    decision: str
    user_ip: str
    reason: str


class PromptLogList(BaseModel):
    total: int
    items: list[PromptLogDetail]


class SecurityEventDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    event_type: str
    severity: str
    details: str


class SecurityEventList(BaseModel):
    total: int
    items: list[SecurityEventDetail]
