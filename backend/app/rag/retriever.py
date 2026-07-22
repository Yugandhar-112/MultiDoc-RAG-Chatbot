"""
RAG STEP 5: Retrieval.

Given a user question, embed it with the *same* embedding model used at
ingestion time (critical — query and document embeddings must live in the
same vector space), then ask the vector store for the top-k most similar
chunks.

We also apply a minimum similarity threshold. This is what powers the
"no answer found" fallback: if even the best-matching chunk is a weak
match, the question is probably not covered by the uploaded documents,
and we'd rather say so than hand the LLM irrelevant context and risk a
hallucinated answer.
"""
from dataclasses import dataclass

from app.embeddings.base import EmbeddingProvider
from app.vectorstore.base import VectorStore, SearchResult

# Below this cosine similarity, we treat retrieval as "nothing relevant
# found" rather than forcing a low-quality answer. Tuned empirically —
# lower it if the corpus uses very different vocabulary than the questions.
MIN_RELEVANCE_SCORE = 0.08


@dataclass
class RetrievedChunk:
    text: str
    doc_id: str
    filename: str
    page_number: int | None
    chunk_index: int
    score: float


class Retriever:
    def __init__(self, embedding_provider: EmbeddingProvider, vector_store: VectorStore):
        self._embeddings = embedding_provider
        self._store = vector_store

    def retrieve(
        self, session_id: str, question: str, top_k: int
    ) -> list[RetrievedChunk]:
        query_embedding = self._embeddings.embed_query(question)
        raw_results: list[SearchResult] = self._store.search(
            session_id=session_id, query_embedding=query_embedding, top_k=top_k
        )
        print("RETRIEVAL DEBUG:", [(r.score, r.text[:60]) for r in raw_results])

        chunks = []
        for r in raw_results:
            if r.score < MIN_RELEVANCE_SCORE:
                continue
            # Chroma metadata can't store None, so ingestion writes -1 as a
            # sentinel for "no page number" (txt/docx uploads) — translate
            # it back here so downstream code deals in real Optional[int].
            raw_page = r.metadata.get("page_number")
            page_number = None if raw_page in (None, -1) else raw_page
            chunks.append(
                RetrievedChunk(
                    text=r.text,
                    doc_id=r.metadata["doc_id"],
                    filename=r.metadata["filename"],
                    page_number=page_number,
                    chunk_index=r.metadata["chunk_index"],
                    score=r.score,
                )
            )
        return chunks
