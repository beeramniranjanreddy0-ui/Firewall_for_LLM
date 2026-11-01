from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.firewall.engine import FirewallEngine
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.firewall import FirewallAnalysis, PromptAnalyzeRequest
from app.schemas.logs import PromptLogDetail, PromptLogList, SecurityEventList
from app.schemas.stats import FirewallStats
from app.services.llm_provider import LLMProviderError, get_provider
from app.services.logging_service import (
    create_prompt_log,
    create_security_events_for_analysis,
    get_prompt_log,
    list_prompt_logs,
    list_security_events,
)
from app.services.stats_service import get_firewall_stats
from app.utils.config import get_settings

router = APIRouter(prefix="/api", tags=["AI Firewall"])
firewall = FirewallEngine()


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/firewall/analyze", response_model=FirewallAnalysis)
async def analyze_prompt(payload: PromptAnalyzeRequest) -> FirewallAnalysis:
    return firewall.analyze(payload.prompt)


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request, db: Session = Depends(get_db)) -> ChatResponse:
    settings = get_settings()
    analysis = firewall.analyze(payload.prompt)
    user_ip = _client_ip(request)
    provider_name = (payload.provider or settings.llm_provider).lower()

    if analysis.decision == "BLOCKED":
        response_text = f"Request blocked by AI Security Firewall: {analysis.reason}"
        log = create_prompt_log(
            db=db,
            prompt=payload.prompt,
            response=response_text,
            analysis=analysis,
            user_ip=user_ip,
        )
        create_security_events_for_analysis(db, analysis, payload.prompt, user_ip)
        db.commit()
        db.refresh(log)
        return ChatResponse(
            prompt=payload.prompt,
            response=response_text,
            analysis=analysis,
            provider=provider_name,
            status="BLOCKED",
            log_id=log.id,
        )

    provider_error: str | None = None
    try:
        provider = get_provider(provider_name)
        response_text = await provider.generate(payload.prompt)
    except LLMProviderError as exc:
        provider_error = str(exc)
        response_text = f"Provider error: {provider_error}"

    log = create_prompt_log(
        db=db,
        prompt=payload.prompt,
        response=response_text,
        analysis=analysis,
        user_ip=user_ip,
    )
    create_security_events_for_analysis(db, analysis, payload.prompt, user_ip)
    db.commit()
    db.refresh(log)

    return ChatResponse(
        prompt=payload.prompt,
        response="" if provider_error else response_text,
        analysis=analysis,
        provider=provider_name,
        status="PROVIDER_ERROR" if provider_error else "COMPLETED",
        error=provider_error,
        log_id=log.id,
    )


@router.get("/logs", response_model=PromptLogList)
def get_logs(
    db: Session = Depends(get_db),
    search: str | None = Query(default=None, max_length=200),
    decision: str | None = Query(default=None, pattern="^(ALLOWED|BLOCKED)$"),
    risk_level: str | None = Query(default=None, pattern="^(SAFE|GOOD|MEDIUM|HIGH)$"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> PromptLogList:
    logs, total = list_prompt_logs(
        db=db,
        search=search,
        decision=decision,
        risk_level=risk_level,
        limit=limit,
        offset=offset,
    )
    return PromptLogList(total=total, items=logs)


@router.get("/logs/{log_id}", response_model=PromptLogDetail)
def get_log(log_id: int, db: Session = Depends(get_db)) -> PromptLogDetail:
    log = get_prompt_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Prompt log not found")
    return log


@router.get("/security-events", response_model=SecurityEventList)
def get_security_events(
    db: Session = Depends(get_db),
    severity: str | None = Query(default=None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$"),
    event_type: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> SecurityEventList:
    events, total = list_security_events(
        db=db,
        severity=severity,
        event_type=event_type,
        limit=limit,
        offset=offset,
    )
    return SecurityEventList(total=total, items=events)


@router.get("/stats", response_model=FirewallStats)
def stats(db: Session = Depends(get_db)) -> FirewallStats:
    return get_firewall_stats(db)
