from pydantic import BaseModel, ConfigDict, Field

from app.schemas.repository import RepositoryRequest


class AgentTaskRequest(RepositoryRequest):
    model_config = ConfigDict(extra="forbid")

    task_type: str = Field(min_length=1, max_length=40)
    user_request: str = Field(min_length=1, max_length=8_000)


class CopilotChatRequest(RepositoryRequest):
    user_request: str = Field(min_length=1, max_length=8_000)


class AgentResultResponse(BaseModel):
    task_type: str
    answer: str
    sources: list[str] = Field(default_factory=list)
    structured: dict[str, object] = Field(default_factory=dict)


class ImplementationPlanResponse(BaseModel):
    goal: str
    assumptions: list[str]
    affected_files: list[str]
    new_files: list[str]
    implementation_steps: list[str]
    testing_steps: list[str]
    risks: list[str]
