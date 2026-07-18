"""
RAG STEP 4: Vector storage — interface.

A VectorStore persists (embedding, text, metadata) triples per session and
supports similarity search. Defining this interface separately from the
ChromaDB implementation is what makes the "swappable for Pinecone/Weaviate
later" claim real: routes_documents.py and retriever.py only ever call
these methods, never Chroma's client directly.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class VectorRecord:
    """One chunk, ready to be persisted."""
    id: str  # globally unique id, e.g. f"{doc_id}_{chunk_index}"
    embedding: list[float]
    text: str
    metadata: dict  # doc_id, filename, page_number, chunk_index


@dataclass
class SearchResult:
    text: str
    metadata: dict
    score: float  # similarity score, higher = more relevant


class VectorStore(ABC):
    @abstractmethod
    def add(self, session_id: str, records: list[VectorRecord]) -> None:
        """Persist chunks for a given session (collection-per-session)."""
        raise NotImplementedError

    @abstractmethod
    def search(
        self, session_id: str, query_embedding: list[float], top_k: int
    ) -> list[SearchResult]:
        """Return the top_k most similar chunks for this session."""
        raise NotImplementedError

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        """Remove all vectors belonging to a session (cleanup)."""
        raise NotImplementedError
