from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.prompt_log import PromptLog
from app.models.security_event import SecurityEvent


def create_prompt_log(
    db: Session,
    *,
    prompt: str,
    response: str | None,
    risk_score: int,
    risk_level: str,
    decision: str,
    user_ip: str,
    reason: str,
    semantic_score: float | None = None,
    semantic_category: str | None = None,
    matched_attack: str | None = None,
    similarity: float | None = None,
    confidence: str | None = None,
) -> PromptLog:
    log = PromptLog(
        prompt=prompt,
        response=response,
        risk_score=risk_score,
        risk_level=risk_level,
        decision=decision,
        user_ip=user_ip,
        reason=reason,
        semantic_score=semantic_score,
        semantic_category=semantic_category,
        matched_attack=matched_attack,
        similarity=similarity,
        confidence=confidence,
    )
    db.add(log)
    db.flush()
    return log


def get_prompt_log(db: Session, log_id: int) -> PromptLog | None:
    return db.get(PromptLog, log_id)


def list_prompt_logs(
    db: Session,
    *,
    search: str | None = None,
    decision: str | None = None,
    risk_level: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[PromptLog], int]:
    statement: Select[tuple[PromptLog]] = select(PromptLog)
    count_statement = select(func.count()).select_from(PromptLog)

    filters = []
    if search:
        like_value = f"%{search}%"
        filters.append(or_(PromptLog.prompt.ilike(like_value), PromptLog.response.ilike(like_value)))
    if decision:
        filters.append(PromptLog.decision == decision)
    if risk_level:
        filters.append(PromptLog.risk_level == risk_level)

    for item in filters:
        statement = statement.where(item)
        count_statement = count_statement.where(item)

    total = db.scalar(count_statement) or 0
    logs = db.scalars(statement.order_by(PromptLog.timestamp.desc()).offset(offset).limit(limit)).all()
    return list(logs), total


def update_prompt_log(
    db: Session,
    log_id: int,
    *,
    prompt: str | None = None,
    response: str | None = None,
    risk_score: int | None = None,
    risk_level: str | None = None,
    decision: str | None = None,
    user_ip: str | None = None,
    reason: str | None = None,
) -> PromptLog | None:
    log = get_prompt_log(db, log_id)
    if not log:
        return None

    updates = {
        "prompt": prompt,
        "response": response,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "decision": decision,
        "user_ip": user_ip,
        "reason": reason,
    }
    for field, value in updates.items():
        if value is not None:
            setattr(log, field, value)

    db.flush()
    return log


def delete_prompt_log(db: Session, log_id: int) -> bool:
    log = get_prompt_log(db, log_id)
    if not log:
        return False
    db.delete(log)
    db.flush()
    return True


def create_security_event(
    db: Session,
    *,
    event_type: str,
    severity: str,
    details: str,
) -> SecurityEvent:
    event = SecurityEvent(event_type=event_type, severity=severity, details=details)
    db.add(event)
    db.flush()
    return event


def get_security_event(db: Session, event_id: int) -> SecurityEvent | None:
    return db.get(SecurityEvent, event_id)


def list_security_events(
    db: Session,
    *,
    severity: str | None = None,
    event_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[SecurityEvent], int]:
    statement: Select[tuple[SecurityEvent]] = select(SecurityEvent)
    count_statement = select(func.count()).select_from(SecurityEvent)

    filters = []
    if severity:
        filters.append(SecurityEvent.severity == severity)
    if event_type:
        filters.append(SecurityEvent.event_type == event_type)

    for item in filters:
        statement = statement.where(item)
        count_statement = count_statement.where(item)

    total = db.scalar(count_statement) or 0
    events = db.scalars(statement.order_by(SecurityEvent.timestamp.desc()).offset(offset).limit(limit)).all()
    return list(events), total


def update_security_event(
    db: Session,
    event_id: int,
    *,
    event_type: str | None = None,
    severity: str | None = None,
    details: str | None = None,
) -> SecurityEvent | None:
    event = get_security_event(db, event_id)
    if not event:
        return None

    updates = {
        "event_type": event_type,
        "severity": severity,
        "details": details,
    }
    for field, value in updates.items():
        if value is not None:
            setattr(event, field, value)

    db.flush()
    return event


def delete_security_event(db: Session, event_id: int) -> bool:
    event = get_security_event(db, event_id)
    if not event:
        return False
    db.delete(event)
    db.flush()
    return True
