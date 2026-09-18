from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(frozen=True)
class DocumentChunk:
    content: str
    source: str
    metadata: dict[str, Any]


class RepositoryIndexer(ABC):
    @abstractmethod
    async def index(self, repository_path: str) -> Sequence[DocumentChunk]:
        raise NotImplementedError


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, chunks: Sequence[DocumentChunk]) -> Sequence[Sequence[float]]:
        raise NotImplementedError


class VectorStore(ABC):
    @abstractmethod
    async def upsert(self, chunks: Sequence[DocumentChunk], embeddings: Sequence[Sequence[float]]) -> None:
        raise NotImplementedError


class Retriever(ABC):
    @abstractmethod
    async def retrieve(self, query: str, limit: int = 5) -> Sequence[DocumentChunk]:
        raise NotImplementedError
