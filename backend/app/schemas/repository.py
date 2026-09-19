from pydantic import BaseModel, ConfigDict, Field


class RepositoryFileInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(min_length=1, max_length=500)
    content: str = Field(max_length=300_000)


class RepositoryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    files: list[RepositoryFileInput] = Field(min_length=1, max_length=1_000)


class RepositoryFileSummary(BaseModel):
    path: str
    language: str
    extension: str
    size_bytes: int
    line_count: int
    redacted_secrets: int


class RepositoryScanResponse(BaseModel):
    file_count: int
    total_bytes: int
    languages: dict[str, int]
    files: list[RepositoryFileSummary]
