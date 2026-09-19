from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.agents.base import AgentRequest
from app.agents.orchestrator import AgentOrchestrator
from app.code_intelligence.analyzer import CodeAnalyzer
from app.core.errors import ForgeAIError
from app.main import app
from app.repository.ingestion import RepositoryIngestionService
from app.repository.security import normalize_relative_path, redact_secrets
from app.services.llm import LLMProvider, LLMRequest, LLMResponse


class FakeProvider(LLMProvider):
    async def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(f"grounded response for {request.prompt[:20]}")


def test_ingestion_ignores_generated_directories_and_redacts_secrets() -> None:
    snapshot = RepositoryIngestionService().ingest([
        {"path": "src/app.py", "content": "TOKEN=secret-value\nprint('ok')"},
        {"path": "node_modules/pkg/index.js", "content": "ignored"},
        {"path": "image.bin", "content": "binary\x00content"},
    ])

    assert [file.path for file in snapshot.files] == ["src/app.py"]
    assert snapshot.files[0].secret_count == 1
    assert "secret-value" not in snapshot.files[0].content


def test_unsafe_paths_are_rejected() -> None:
    with pytest.raises(ForgeAIError):
        normalize_relative_path("../../outside.py")
    with pytest.raises(ForgeAIError):
        normalize_relative_path(".env")


def test_python_analysis_returns_symbols_and_findings() -> None:
    snapshot = RepositoryIngestionService().ingest([{"path": "main.py", "content": "import os\ndef run():\n    eval('1')\n# TODO: follow up\n"}])

    symbols, findings = CodeAnalyzer().analyze(snapshot)

    assert any(symbol.name == "run" for symbol in symbols)
    assert {finding.category for finding in findings} >= {"risky_construct", "todo"}


@pytest.mark.anyio
async def test_agent_orchestrator_routes_supported_tasks() -> None:
    result = await AgentOrchestrator(FakeProvider()).route(AgentRequest("copilot", "Where?", "FILE: app.py"))

    assert "grounded response" in result.answer


def test_api_validation_and_analysis_endpoint() -> None:
    client = TestClient(app)
    registration = client.post("/api/auth/register", json={"full_name": "Test User", "email": f"{uuid4().hex}@example.com", "password": "correct-horse-battery", "confirm_password": "correct-horse-battery"})
    assert registration.status_code == 201
    response = client.post("/api/v1/code/analyze", json={"files": [{"path": "main.py", "content": "def ok():\n    return True\n"}]})

    assert response.status_code == 200
    assert response.json()["symbols"][0]["name"] == "ok"
    assert client.post("/api/v1/code/analyze", json={"files": []}).status_code == 400
