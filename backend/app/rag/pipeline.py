import re
from collections import Counter

from app.rag.interfaces import DocumentChunk, Retriever
from app.repository.ingestion import RepositorySnapshot


class SimpleRepositoryIndexer:
    def __init__(self, chunk_size: int = 2_000, overlap: int = 200) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def index(self, snapshot: RepositorySnapshot) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for file in snapshot.files:
            start = 0
            while start < len(file.content):
                end = min(len(file.content), start + self.chunk_size)
                chunks.append(DocumentChunk(file.content[start:end], file.path, {"language": file.language, "start": start, "end": end}))
                if end == len(file.content):
                    break
                start = max(start + 1, end - self.overlap)
        return chunks


class InMemoryVectorStore:
    def __init__(self, chunks: list[DocumentChunk] | None = None) -> None:
        self.chunks = chunks or []

    async def upsert(self, chunks: list[DocumentChunk]) -> None:
        self.chunks = list(chunks)


class LexicalRetriever(Retriever):
    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self.chunks = chunks

    async def retrieve(self, query: str, limit: int = 5) -> list[DocumentChunk]:
        terms = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", query.lower()))
        ranked: list[tuple[int, DocumentChunk]] = []
        for chunk in self.chunks:
            tokens = Counter(re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", chunk.content.lower()))
            score = sum(tokens[term] for term in terms) + (2 if any(term in chunk.source.lower() for term in terms) else 0)
            if score:
                ranked.append((score, chunk))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in ranked[:limit]]