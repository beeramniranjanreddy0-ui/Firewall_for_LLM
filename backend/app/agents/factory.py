from __future__ import annotations

from app.agents.agent_registry import AgentRegistry
from app.agents.jailbreak_agent import JailbreakAgent
from app.agents.prompt_injection_agent import PromptInjectionAgent
from app.agents.privacy_agent import PrivacyAgent
from app.agents.toxicity_agent import ToxicityAgent


def create_default_agents(*, registry: AgentRegistry | None = None) -> list[object]:
    registry = registry or AgentRegistry()
    agent_classes = [
        PromptInjectionAgent,
        JailbreakAgent,
        PrivacyAgent,
        ToxicityAgent,
    ]
    for cls in agent_classes:
        registry.register(cls)
    return registry.get_instances()
