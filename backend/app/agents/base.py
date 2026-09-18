from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRequest:
    prompt: str


@dataclass(frozen=True)
class AgentResult:
    message: str


class Agent(ABC):
    name: str

    @abstractmethod
    async def run(self, request: AgentRequest) -> AgentResult:
        raise NotImplementedError


class RepositoryAnalyzerAgent(Agent):
    name = "repository_analyzer"


class CodeAnalyzerAgent(Agent):
    name = "code_analyzer"


class DebuggingAgent(Agent):
    name = "debugging"


class SecurityAgent(Agent):
    name = "security"


class TestingAgent(Agent):
    name = "testing"


class DocumentationAgent(Agent):
    name = "documentation"


class ArchitectureAgent(Agent):
    name = "architecture"


class EngineeringCopilotAgent(Agent):
    name = "engineering_copilot"
