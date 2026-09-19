from dataclasses import dataclass
from pathlib import PurePosixPath

from app.core.config import settings
from app.core.errors import ForgeAIError
from app.repository.security import normalize_relative_path, redact_secrets

IGNORED_DIRECTORIES = {
    ".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", "coverage", ".next", ".cache",
    ".pytest_cache", ".mypy_cache", ".tox", "htmlcov", "target", "vendor", "bower_components",
}
LANGUAGES = {
    ".py": "python", ".js": "javascript", ".jsx": "javascript", ".ts": "typescript", ".tsx": "typescript",
    ".java": "java", ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php", ".cs": "csharp",
    ".c": "c", ".h": "c", ".cpp": "cpp", ".md": "markdown", ".json": "json", ".yaml": "yaml", ".yml": "yaml",
    ".toml": "toml", ".css": "css", ".html": "html", ".sql": "sql", ".sh": "shell",
}


@dataclass(frozen=True)
class RepositoryFile:
    path: str
    language: str
    extension: str
    size_bytes: int
    line_count: int
    content: str
    secret_count: int = 0


@dataclass(frozen=True)
class RepositorySnapshot:
    files: tuple[RepositoryFile, ...]
    total_bytes: int


class RepositoryIngestionService:
    def ingest(self, files: list[dict[str, str]]) -> RepositorySnapshot:
        if len(files) > settings.max_repository_files:
            raise ForgeAIError("too_many_files", "The repository contains too many files for this MVP.", 413)
        accepted: list[RepositoryFile] = []
        total_bytes = 0
        seen: set[str] = set()
        for item in files:
            path = normalize_relative_path(item["path"])
            parts = PurePosixPath(path).parts
            if any(part in IGNORED_DIRECTORIES for part in parts[:-1]) or path in seen:
                continue
            content = item["content"]
            size = len(content.encode("utf-8"))
            if size > settings.max_file_size_bytes:
                continue
            if "\x00" in content:
                continue
            extension = PurePosixPath(path).suffix.lower()
            language = LANGUAGES.get(extension, "text")
            redaction = redact_secrets(content)
            total_bytes += size
            if total_bytes > settings.max_repository_size_bytes:
                raise ForgeAIError("repository_too_large", "The repository exceeds the supported upload limit.", 413)
            seen.add(path)
            accepted.append(RepositoryFile(path, language, extension, size, redaction.content.count("\n") + 1, redaction.content, redaction.secret_count))
        return RepositorySnapshot(tuple(accepted), total_bytes)
