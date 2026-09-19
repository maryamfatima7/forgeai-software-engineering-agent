from pydantic import BaseModel, ConfigDict, Field

from app.schemas.repository import RepositoryRequest


class Finding(BaseModel):
    severity: str
    category: str
    file: str
    line: int | None = None
    description: str
    reason: str
    remediation: str


class Symbol(BaseModel):
    kind: str
    name: str
    file: str
    line: int


class CodeAnalysisRequest(RepositoryRequest):
    paths: list[str] = Field(default_factory=list, max_length=100)


class CodeAnalysisResponse(BaseModel):
    files_analyzed: int
    symbols: list[Symbol]
    findings: list[Finding]


class RepositoryAnalysisResponse(BaseModel):
    repository_overview: dict[str, object]
    symbols: list[Symbol]
    findings: list[Finding]


class SecurityReviewResponse(BaseModel):
    review_type: str = "static heuristic security review"
    files_reviewed: int
    findings: list[Finding]


class TestSuggestion(BaseModel):
    area: str
    file: str | None = None
    rationale: str
    suggested_test: str


class TestingAnalysisResponse(BaseModel):
    files_reviewed: int
    existing_test_files: list[str]
    coverage_gaps: list[str]
    suggestions: list[TestSuggestion]


class ArchitectureResponse(BaseModel):
    architecture_summary: str
    components: list[str]
    dependencies: list[str]
    potential_concerns: list[str]
    recommendations: list[str]


class DocumentationResponse(BaseModel):
    readme_outline: list[str]
    api_documentation_suggestions: list[str]
    module_explanations: list[str]
    setup_instructions: list[str]
    environment_variables: list[str]


class ProjectHealthResponse(BaseModel):
    repository_overview: dict[str, object]
    code_quality_findings: list[Finding]
    security_findings: list[Finding]
    testing_status: TestingAnalysisResponse
    architecture_summary: ArchitectureResponse
    documentation_status: DocumentationResponse
    recommendations: list[str]
