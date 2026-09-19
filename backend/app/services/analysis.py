import re
from collections import Counter

from app.code_intelligence.analyzer import CodeAnalyzer
from app.repository.ingestion import RepositorySnapshot
from app.schemas.analysis import (
    ArchitectureResponse,
    DocumentationResponse,
    Finding,
    SecurityReviewResponse,
    TestSuggestion,
    TestingAnalysisResponse,
)


class RepositoryAnalysisService:
    def __init__(self) -> None:
        self.code_analyzer = CodeAnalyzer()

    def scan_summary(self, snapshot: RepositorySnapshot) -> dict[str, object]:
        languages = Counter(file.language for file in snapshot.files)
        return {"file_count": len(snapshot.files), "total_bytes": snapshot.total_bytes, "languages": dict(languages)}

    def security_review(self, snapshot: RepositorySnapshot) -> SecurityReviewResponse:
        findings: list[Finding] = []
        for file in snapshot.files:
            if file.secret_count:
                findings.append(Finding(severity="high", category="secret", file=file.path, description="A credential-like value was redacted before analysis.", reason="The uploaded source contained a pattern matching a common secret assignment or key format.", remediation="Rotate the credential, remove it from source control, and use a managed secret store."))
            for line_number, line in enumerate(file.content.splitlines(), 1):
                checks = ((r"\b(eval|exec)\s*\(", "dynamic evaluation", "Avoid executing data as code."), (r"subprocess\.(?:run|Popen|call)\([^\n]*(?:shell\s*=\s*True|shell=True)", "shell execution", "Avoid shell mode and pass arguments as a list."), (r"(?:open|Path)\([^\n]*input\(", "filesystem input", "Validate and constrain user-controlled paths."))
                for pattern, label, remediation in checks:
                    if re.search(pattern, line):
                        findings.append(Finding(severity="high", category=label, file=file.path, line=line_number, description=f"Potentially risky {label} pattern detected.", reason="This is a static heuristic and requires developer review of data flow.", remediation=remediation))
        return SecurityReviewResponse(files_reviewed=len(snapshot.files), findings=findings)

    def testing_analysis(self, snapshot: RepositorySnapshot) -> TestingAnalysisResponse:
        test_files = [file.path for file in snapshot.files if re.search(r"(^|/)(test|tests)(/|_)|\.(test|spec)\.", file.path, re.IGNORECASE)]
        source_files = [file for file in snapshot.files if file.path not in test_files and file.language in {"python", "javascript", "typescript"}]
        gaps = []
        suggestions = []
        if not test_files:
            gaps.append("No obvious test files were detected.")
        for file in source_files:
            if re.search(r"\b(def|function|class)\b", file.content):
                gaps.append(f"No obvious test pairing was detected for {file.path}.")
                suggestions.append(TestSuggestion(area="source module", file=file.path, rationale="The module declares executable code but no matching test file was detected.", suggested_test=f"Add focused unit tests for the public functions and error paths in {file.path}."))
        return TestingAnalysisResponse(files_reviewed=len(snapshot.files), existing_test_files=test_files, coverage_gaps=gaps[:20], suggestions=suggestions[:20])

    def architecture(self, snapshot: RepositorySnapshot) -> ArchitectureResponse:
        languages = Counter(file.language for file in snapshot.files)
        components = []
        if any(file.path.startswith("frontend/") or file.language in {"javascript", "typescript", "css"} for file in snapshot.files):
            components.append("frontend or client-side source")
        if any(file.language == "python" for file in snapshot.files):
            components.append("Python application or service layer")
        if any("api" in file.path.lower() for file in snapshot.files):
            components.append("API boundary")
        dependencies = [file.path for file in snapshot.files if file.path.lower().endswith(("requirements.txt", "pyproject.toml", "package.json", "package-lock.json"))]
        concerns = []
        if len(snapshot.files) > 100:
            concerns.append("The repository is large for a request-scoped serverless analysis.")
        if not dependencies:
            concerns.append("No common dependency manifest was detected.")
        return ArchitectureResponse(architecture_summary=f"Detected {len(snapshot.files)} supported files across {len(languages)} language categories.", components=components, dependencies=dependencies, potential_concerns=concerns, recommendations=["Keep analysis boundaries explicit and add focused tests around public modules.", "Persist an indexed snapshot in a managed store before supporting larger repositories."])

    def documentation(self, snapshot: RepositorySnapshot) -> DocumentationResponse:
        env_files = [file.path for file in snapshot.files if "env" in file.path.lower() or "config" in file.path.lower()]
        modules = [file.path for file in snapshot.files if file.language in {"python", "javascript", "typescript"}][:20]
        return DocumentationResponse(readme_outline=["Overview and problem statement", "Local setup", "Configuration", "Architecture", "Testing", "Deployment"], api_documentation_suggestions=["Document public endpoints and validation errors.", "Include request and response examples for externally visible APIs."], module_explanations=[f"Add a responsibility and public API description for {path}." for path in modules], setup_instructions=["Document runtime prerequisites and dependency installation.", "Document test and development commands."], environment_variables=[f"Review and document configuration source: {path}" for path in env_files])
