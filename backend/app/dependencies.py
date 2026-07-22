"""
FastAPI dependency providers.

These are constructed once (lru_cache) and reused across requests — most
importantly the embedding model, which is expensive to load into memory
and should not be re-instantiated per-request.

This module is also the *single place* that decides which concrete
implementation backs each interface (SentenceTransformerProvider vs. some
future VoyageProvider; ChromaVectorStore vs. some future PineconeStore).
Swapping providers later means changing two lines here — nowhere else.
"""
from functools import lru_cache

from app.config import get_settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.gemini_embedding_provider import GeminiEmbeddingProvider
from app.vectorstore.base import VectorStore
from app.vectorstore.chroma_store import ChromaVectorStore
from app.rag.retriever import Retriever
from app.rag.generator import AnswerGenerator


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    return GeminiEmbeddingProvider(api_key=settings.gemini_api_key, model=settings.embedding_model)


@lru_cache
def get_vector_store() -> VectorStore:
    settings = get_settings()
    return ChromaVectorStore(persist_dir=settings.chroma_persist_dir)


@lru_cache
def get_retriever() -> Retriever:
    return Retriever(
        embedding_provider=get_embedding_provider(),
        vector_store=get_vector_store(),
    )


@lru_cache
def get_generator() -> AnswerGenerator:
    settings = get_settings()
    return AnswerGenerator(api_key=settings.gemini_api_key, model=settings.gemini_model)
