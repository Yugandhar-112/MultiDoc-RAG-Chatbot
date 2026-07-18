"""
Local, free embedding provider using sentence-transformers.

Model choice: all-MiniLM-L6-v2
  - 384-dimensional vectors, ~80MB, runs fast on CPU
  - Good general-purpose semantic similarity for English text
  - Tradeoff: lower ceiling on retrieval quality than large hosted models
    (e.g. Voyage-3, OpenAI text-embedding-3-large) on tricky/domain-specific
    text, but it's free, requires no API key, and is plenty good for a
    portfolio-scale RAG demo over PDFs/docs.

Swapping providers: implement EmbeddingProvider with a different model
(see app/embeddings/base.py) and change one line in app/config.py /
wherever the provider is instantiated. Nothing else in the app needs to
change, since ingestion and retrieval only depend on the interface.
"""
from sentence_transformers import SentenceTransformer

from app.embeddings.base import EmbeddingProvider


class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model = SentenceTransformer(model_name)
        self._dimension = self._model.get_sentence_embedding_dimension()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,  # so cosine similarity == dot product
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self._model.encode(
            text,
            normalize_embeddings=True,
        )
        return embedding.tolist()

    @property
    def dimension(self) -> int:
        return self._dimension
