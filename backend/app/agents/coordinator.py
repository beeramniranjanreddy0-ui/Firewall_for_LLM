from __future__ import annotations

import asyncio
import time

from app.agents.base_agent import AgentResult
from app.agents.factory import create_default_agents
from app.agents.risk_engine import RiskEngine
from app.agents.agent_registry import AgentRegistry


class CoordinatorAgent:
    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or AgentRegistry()
        self.risk_engine = RiskEngine()

    async def _run_agent(self, agent: object, prompt: str) -> AgentResult:
        return agent.analyze(prompt)

    async def _collect_results(self, prompt: str) -> list[AgentResult]:
        agents = self.registry.get_instances() or create_default_agents(registry=self.registry)
        tasks = [asyncio.create_task(self._run_agent(agent, prompt)) for agent in agents]
        return await asyncio.gather(*tasks)

    def analyze(self, results: list[AgentResult] | None = None, prompt: str | None = None) -> dict[str, object]:
        if results is None and prompt is None:
            raise ValueError("Provide either agent results or a prompt")
        if results is None:
            results = asyncio.run(self._collect_results(prompt))

        rule_score = 10
        semantic_score = 0.0
        injection_score = 0
        jailbreak_score = 0
        privacy_score = 0
        toxicity_score = 0

        for result in results:
            if result.agent_name == "PromptInjectionAgent":
                injection_score = result.score
            elif result.agent_name == "JailbreakAgent":
                jailbreak_score = result.score
            elif result.agent_name == "PrivacyAgent":
                privacy_score = result.score
            elif result.agent_name == "ToxicityAgent":
                toxicity_score = result.score

        evaluation = self.risk_engine.evaluate(
            rule_score=rule_score,
            semantic_score=semantic_score,
            injection_score=injection_score,
            jailbreak_score=jailbreak_score,
            privacy_score=privacy_score,
            toxicity_score=toxicity_score,
        )
        summary = "; ".join(
            f"{result.agent_name}: {result.recommendation} ({result.score})" for result in results
        )
        return {
            "decision": evaluation["decision"],
            "final_score": evaluation["final_score"],
            "risk_level": evaluation["risk_level"],
            "summary": summary,
            "agent_results": results,
            "confidence": round(sum(result.confidence for result in results) / max(1, len(results)), 3),
            "processing_time": round(time.perf_counter(), 3),
        }
