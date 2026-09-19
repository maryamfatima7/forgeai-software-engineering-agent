import json
import re

from fastapi import APIRouter, Depends

from app.agents.base import AgentRequest
from app.agents.orchestrator import AgentOrchestrator
from app.core.config import settings
from app.core.auth import current_user
from app.core.errors import ForgeAIError
from app.repository.ingestion import RepositoryIngestionService, RepositorySnapshot
from app.rag.pipeline import LexicalRetriever, SimpleRepositoryIndexer
from app.schemas.agent import AgentResultResponse, CopilotChatRequest, ImplementationPlanResponse
from app.schemas.analysis import (
    ArchitectureResponse,
    CodeAnalysisRequest,
    CodeAnalysisResponse,
    DocumentationResponse,
    ProjectHealthResponse,
    RepositoryAnalysisResponse,
    SecurityReviewResponse,
    TestingAnalysisResponse,
)
from app.schemas.repository import RepositoryRequest, RepositoryScanResponse, RepositoryFileSummary
from app.services.analysis import RepositoryAnalysisService
from app.services.llm import get_llm_provider

router = APIRouter(dependencies=[Depends(current_user)])
ingestion = RepositoryIngestionService()
analysis = RepositoryAnalysisService()


def snapshot_from(request: RepositoryRequest) -> RepositorySnapshot:
    return ingestion.ingest([file.model_dump() for file in request.files])


def scan_response(snapshot: RepositorySnapshot) -> RepositoryScanResponse:
    summary = analysis.scan_summary(snapshot)
    return RepositoryScanResponse(file_count=summary["file_count"], total_bytes=summary["total_bytes"], languages=summary["languages"], files=[RepositoryFileSummary(path=file.path, language=file.language, extension=file.extension, size_bytes=file.size_bytes, line_count=file.line_count, redacted_secrets=file.secret_count) for file in snapshot.files])


async def agent_response(task_type: str, request: RepositoryRequest, user_request: str) -> AgentResultResponse:
    snapshot = snapshot_from(request)
    chunks = SimpleRepositoryIndexer().index(snapshot)
    retrieved = await LexicalRetriever(chunks).retrieve(user_request)
    selected = retrieved or chunks[:5]
    sources = tuple(dict.fromkeys(chunk.source for chunk in selected))
    context = "\n\n".join(f"FILE: {chunk.source}\n{chunk.content}" for chunk in selected)[:settings.max_context_characters]
    result = await AgentOrchestrator(get_llm_provider()).route(AgentRequest(task_type, user_request, context, sources))
    return AgentResultResponse(task_type=task_type, answer=result.answer, sources=list(result.sources), structured=result.structured)


@router.post("/repository/scan", response_model=RepositoryScanResponse)
def scan_repository(request: RepositoryRequest) -> RepositoryScanResponse:
    return scan_response(snapshot_from(request))


@router.post("/repository/analyze", response_model=RepositoryAnalysisResponse)
def analyze_repository(request: RepositoryRequest) -> RepositoryAnalysisResponse:
    snapshot = snapshot_from(request)
    symbols, findings = analysis.code_analyzer.analyze(snapshot)
    return RepositoryAnalysisResponse(repository_overview=analysis.scan_summary(snapshot), symbols=symbols, findings=findings)


@router.post("/code/analyze", response_model=CodeAnalysisResponse)
def analyze_code(request: CodeAnalysisRequest) -> CodeAnalysisResponse:
    snapshot = snapshot_from(request)
    symbols, findings = analysis.code_analyzer.analyze(snapshot, request.paths)
    return CodeAnalysisResponse(files_analyzed=len(snapshot.files), symbols=symbols, findings=findings)


@router.post("/security/review", response_model=SecurityReviewResponse)
def review_security(request: RepositoryRequest) -> SecurityReviewResponse:
    return analysis.security_review(snapshot_from(request))


@router.post("/tests/analyze", response_model=TestingAnalysisResponse)
def analyze_tests(request: RepositoryRequest) -> TestingAnalysisResponse:
    return analysis.testing_analysis(snapshot_from(request))


@router.post("/architecture/analyze", response_model=ArchitectureResponse)
def analyze_architecture(request: RepositoryRequest) -> ArchitectureResponse:
    return analysis.architecture(snapshot_from(request))


@router.post("/documentation/generate", response_model=DocumentationResponse)
def generate_documentation(request: RepositoryRequest) -> DocumentationResponse:
    return analysis.documentation(snapshot_from(request))


@router.post("/copilot/chat", response_model=AgentResultResponse)
async def copilot_chat(request: CopilotChatRequest) -> AgentResultResponse:
    return await agent_response("copilot", request, request.user_request)


@router.post("/implementation/plan", response_model=ImplementationPlanResponse)
async def implementation_plan(request: CopilotChatRequest) -> ImplementationPlanResponse:
    result = await agent_response("implementation_plan", request, request.user_request)
    try:
        cleaned = re.sub(r"^```(?:json)?|```$", "", result.answer.strip(), flags=re.MULTILINE).strip()
        data = json.loads(cleaned)
        return ImplementationPlanResponse.model_validate(data)
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        raise ForgeAIError("invalid_plan", "The provider did not return the required implementation-plan structure.", 502) from error


@router.get("/project/health", response_model=ProjectHealthResponse)
def project_health() -> ProjectHealthResponse:
    empty_testing = TestingAnalysisResponse(files_reviewed=0, existing_test_files=[], coverage_gaps=["No request-scoped repository snapshot was supplied."], suggestions=[])
    empty_architecture = ArchitectureResponse(architecture_summary="No repository snapshot is available for this request.", components=[], dependencies=[], potential_concerns=["Project health is request-scoped in the serverless MVP."], recommendations=["Upload repository files and run the analysis endpoints to generate a report."])
    empty_docs = DocumentationResponse(readme_outline=[], api_documentation_suggestions=[], module_explanations=[], setup_instructions=[], environment_variables=[])
    return ProjectHealthResponse(repository_overview={"file_count": 0, "message": "Upload a repository to generate project health."}, code_quality_findings=[], security_findings=[], testing_status=empty_testing, architecture_summary=empty_architecture, documentation_status=empty_docs, recommendations=["Connect a repository before relying on project health recommendations."])
