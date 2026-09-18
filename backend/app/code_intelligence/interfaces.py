from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class FileMetadata:
    path: Path
    size_bytes: int
    modified_at: datetime


@dataclass(frozen=True)
class SourceFile:
    metadata: FileMetadata
    content: str


class RepositoryScanner(ABC):
    @abstractmethod
    def scan(self, repository_path: Path) -> Sequence[FileMetadata]:
        raise NotImplementedError


class ASTAnalysisService(ABC):
    @abstractmethod
    def analyze(self, source_file: SourceFile) -> dict[str, object]:
        raise NotImplementedError
