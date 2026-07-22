"""
Hosted embedding provider using Google's Gemini Embedding API.

This replaces the local sentence-transformers model. Running a local
transformer model (even a small one) needs enough RAM to hold the model
weights plus PyTorch's own overhead — on a 512MB-RAM free-tier server,
that's tight enough to cause out-of-memory crashes under real load. A
hosted embeddings API removes that entire dependency: no model weights,
no torch, no transformers library — just an HTTP call, using the same
GEMINI_API_KEY already configured for answer generation.

task_type matters here: RETRIEVAL_DOCUMENT and RETRIEVAL_QUERY tell the
model which side of an asymmetric search this text represents (a stored
passage vs. a user's question), which measurably improves retrieval
quality over treating both the same way.
"""
from google import genai
from google.genai import types

from app.embeddings.base import EmbeddingProvider

# gemini-embedding-001 defaults to 3072-dim vectors; 768 keeps storage and
# search fast for a small-scale app while still following Google's
# suggested reduced-dimension options (768, 1536, or 3072).
OUTPUT_DIMENSIONALITY = 768


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str = "gemini-embedding-001"):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = self._client.models.embed_content(
            model=self._model,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=OUTPUT_DIMENSIONALITY,
            ),
        )
        return [e.values for e in result.embeddings]

    def embed_query(self, text: str) -> list[float]:
        result = self._client.models.embed_content(
            model=self._model,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=OUTPUT_DIMENSIONALITY,
            ),
        )
        return result.embeddings[0].values

    @property
    def dimension(self) -> int:
        return OUTPUT_DIMENSIONALITY