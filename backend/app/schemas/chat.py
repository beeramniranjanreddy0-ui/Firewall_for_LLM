from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.firewall import FirewallAnalysis


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    provider: Literal["ollama", "openai", "gemini"] | None = None


class ChatResponse(BaseModel):
    prompt: str
    response: str
    analysis: FirewallAnalysis
    provider: str
    status: Literal["COMPLETED", "BLOCKED", "PROVIDER_ERROR"]
    error: str | None = None
    log_id: int | None = None
