from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseSecurityAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, type[BaseSecurityAgent]] = {}
        self._instances: dict[str, BaseSecurityAgent] = {}

    def register(self, agent_cls: type[BaseSecurityAgent], *, enabled: bool = True) -> None:
        self._agents[agent_cls.__name__] = agent_cls
        if enabled:
            self._instances[agent_cls.__name__] = agent_cls()

    def get_instances(self) -> list[BaseSecurityAgent]:
        return list(self._instances.values())

    def get_agent_names(self) -> list[str]:
        return list(self._instances.keys())

    def clear(self) -> None:
        self._agents.clear()
        self._instances.clear()
