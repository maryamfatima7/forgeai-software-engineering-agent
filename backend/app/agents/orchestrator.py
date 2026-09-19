from app.agents.base import (
    Agent,
    AgentRequest,
    AgentResult,
    ArchitectureAgent,
    CodeAnalyzerAgent,
    DebuggingAgent,
    DocumentationAgent,
    EngineeringCopilotAgent,
    RepositoryAnalyzerAgent,
    SecurityAgent,
    TestingAgent,
)
from app.core.errors import ForgeAIError
from app.services.llm import LLMProvider


class AgentOrchestrator:
    SUPPORTED_TASKS = {
        "repository_analysis": RepositoryAnalyzerAgent,
        "code_analysis": CodeAnalyzerAgent,
        "debug": DebuggingAgent,
        "security": SecurityAgent,
        "testing": TestingAgent,
        "documentation": DocumentationAgent,
        "architecture": ArchitectureAgent,
        "copilot": EngineeringCopilotAgent,
        "implementation_plan": EngineeringCopilotAgent,
    }

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    async def route(self, request: AgentRequest) -> AgentResult:
        agent_type = self.SUPPORTED_TASKS.get(request.task_type)
        if agent_type is None:
            raise ForgeAIError("unsupported_task", f"Unsupported task type: {request.task_type}")
        return await agent_type(self.provider).run(request)
