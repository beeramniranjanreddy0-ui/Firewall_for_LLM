from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.database import crud
from app.models.prompt_log import PromptLog
from app.models.security_event import SecurityEvent
from app.schemas.firewall import FirewallAnalysis


def create_prompt_log(
    db: Session,
    prompt: str,
    response: str,
    analysis: FirewallAnalysis,
    user_ip: str,
) -> PromptLog:
    # Extract semantic information if available
    semantic_score = None
    semantic_category = None
    matched_attack = None
    similarity = None
    confidence = None
    
    if analysis.semantic_analysis:
        semantic_score = analysis.semantic_analysis.semantic_score
        semantic_category = analysis.semantic_analysis.category
        matched_attack = analysis.semantic_analysis.matched_example
        similarity = analysis.semantic_analysis.semantic_score
        confidence = analysis.semantic_analysis.confidence
    
    return crud.create_prompt_log(
        db,
        prompt=prompt,
        response=response,
        risk_score=analysis.risk_score,
        risk_level=analysis.risk_level,
        decision=analysis.decision,
        user_ip=user_ip,
        reason=analysis.reason,
        semantic_score=semantic_score,
        semantic_category=semantic_category,
        matched_attack=matched_attack,
        similarity=similarity,
        confidence=confidence,
    )


def create_security_events_for_analysis(
    db: Session,
    analysis: FirewallAnalysis,
    prompt: str,
    user_ip: str,
) -> list[SecurityEvent]:
    events: list[SecurityEvent] = []

    def add_event(event_type: str, severity: str) -> None:
        details = {
            "prompt_preview": prompt[:240],
            "risk_score": analysis.risk_score,
            "risk_level": analysis.risk_level,
            "decision": analysis.decision,
            "reason": analysis.reason,
            "matched_rules": analysis.matched_rules,
            "user_ip": user_ip,
        }
        
        # Add semantic details if available
        if analysis.semantic_analysis:
            details["semantic_detection"] = {
                "semantic_score": analysis.semantic_analysis.semantic_score,
                "category": analysis.semantic_analysis.category,
                "confidence": analysis.semantic_analysis.confidence,
                "matched_example": analysis.semantic_analysis.matched_example,
            }
        
        event = crud.create_security_event(
            db,
            event_type=event_type,
            severity=severity,
            details=json.dumps(details),
        )
        events.append(event)

    severity = _severity_for_score(analysis.risk_score)
    if analysis.decision == "BLOCKED":
        add_event("PROMPT_BLOCKED", severity)
    if "prompt_injection" in analysis.categories or any("injection" in item.lower() for item in analysis.matched_rules):
        add_event("PROMPT_INJECTION_DETECTED", severity)
    if "jailbreak" in analysis.categories or any("jailbreak" in item for item in analysis.matched_rules):
        add_event("JAILBREAK_DETECTED", severity)
    if analysis.semantic_analysis and analysis.semantic_analysis.semantic_score >= 0.80:
        add_event("SEMANTIC_THREAT_DETECTED", severity)

    return events


def list_prompt_logs(
    db: Session,
    search: str | None,
    decision: str | None,
    risk_level: str | None,
    limit: int,
    offset: int,
) -> tuple[list[PromptLog], int]:
    return crud.list_prompt_logs(
        db,
        search=search,
        decision=decision,
        risk_level=risk_level,
        limit=limit,
        offset=offset,
    )


def get_prompt_log(db: Session, log_id: int) -> PromptLog | None:
    return crud.get_prompt_log(db, log_id)


def list_security_events(
    db: Session,
    severity: str | None,
    event_type: str | None,
    limit: int,
    offset: int,
) -> tuple[list[SecurityEvent], int]:
    return crud.list_security_events(
        db,
        severity=severity,
        event_type=event_type,
        limit=limit,
        offset=offset,
    )


def _severity_for_score(score: int) -> str:
    if score >= 90:
        return "CRITICAL"
    if score >= 61:
        return "HIGH"
    if score >= 31:
        return "MEDIUM"
    return "LOW"
