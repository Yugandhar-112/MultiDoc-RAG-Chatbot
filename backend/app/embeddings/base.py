"""
RAG STEP 3: Embeddings — interface.

An EmbeddingProvider turns text into a fixed-length vector such that
semantically similar text produces vectors that are close together
(by cosine similarity / dot product). This abstraction is what lets us
swap the local sentence-transformers model for a hosted API (Voyage,
OpenAI, Cohere) later without touching any other layer of the app —
ingestion, vector store, and retrieval only ever talk to this interface.
"""
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of chunk texts (called at ingestion time)."""
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed a single user question (called at query time)."""
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Vector dimensionality — needed by some vector stores at collection-creation time."""
        raise NotImplementedError
