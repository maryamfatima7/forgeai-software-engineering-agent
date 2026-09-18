from abc import ABC, abstractmethod

from app.agents.base import Agent, AgentRequest, AgentResult


class AgentOrchestrator(ABC):
    @abstractmethod
    async def route(self, request: AgentRequest) -> AgentResult:
        raise NotImplementedError


class DefaultAgentOrchestrator(AgentOrchestrator):
    def __init__(self, agents: dict[str, Agent] | None = None) -> None:
        self.agents = agents or {}

    async def route(self, request: AgentRequest) -> AgentResult:
        raise NotImplementedError("Agent routing is reserved for a future phase.")
