"""
Local, file-based vector store using ChromaDB.

Design choice: one Chroma *collection* per chat session
  (collection name = f"session_{session_id}").
This gives us free multi-tenancy — one user's uploaded documents are never
searched against another user's session — without needing a metadata
filter on every query. It also makes "delete a session" a single
collection drop instead of a filtered delete.

Swapping to Pinecone/Weaviate later: implement VectorStore against that
SDK (e.g. one Pinecone *namespace* per session instead of a collection),
and change the single instantiation site in app/main.py. Nothing in
routes_documents.py, retriever.py, etc. needs to know which store is
behind the interface.
"""
import chromadb

from app.vectorstore.base import VectorStore, VectorRecord, SearchResult


class ChromaVectorStore(VectorStore):
    def __init__(self, persist_dir: str):
        self._client = chromadb.PersistentClient(path=persist_dir)

    def _collection_name(self, session_id: str) -> str:
        return f"session_{session_id}"

    def add(self, session_id: str, records: list[VectorRecord]) -> None:
        if not records:
            return
        collection = self._client.get_or_create_collection(
            name=self._collection_name(session_id),
            metadata={"hnsw:space": "cosine"},
        )
        collection.add(
            ids=[r.id for r in records],
            embeddings=[r.embedding for r in records],
            documents=[r.text for r in records],
            metadatas=[r.metadata for r in records],
        )

    def search(
        self, session_id: str, query_embedding: list[float], top_k: int
    ) -> list[SearchResult]:
        try:
            collection = self._client.get_collection(self._collection_name(session_id))
        except Exception:
            # No documents uploaded yet for this session
            return []

        # Guard against asking for more results than exist in the collection
        count = collection.count()
        if count == 0:
            return []
        top_k = min(top_k, count)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        search_results = []
        # Chroma nests results one level deep per query (we only send one query)
        for text, metadata, distance in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        ):
            # Chroma returns cosine *distance* (0 = identical); convert to a
            # similarity score (1 = identical) which is more intuitive to
            # surface to the frontend as a "relevance" percentage.
            similarity_score = 1 - distance
            search_results.append(
                SearchResult(text=text, metadata=metadata, score=similarity_score)
            )
        return search_results

    def delete_session(self, session_id: str) -> None:
        try:
            self._client.delete_collection(self._collection_name(session_id))
        except Exception:
            pass  # collection didn't exist — nothing to do
