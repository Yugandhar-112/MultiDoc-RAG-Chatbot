"""
Upload endpoint. This is where ingestion steps 1-4 of the RAG pipeline
(parse -> chunk -> embed -> store) are wired together in sequence.
"""
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException

from app.config import Settings, get_settings
from app.ingestion.parsers import parse_document
from app.ingestion.chunker import chunk_pages
from app.embeddings.base import EmbeddingProvider
from app.vectorstore.base import VectorStore, VectorRecord
from app.session.store import session_store
from app.models.schemas import UploadResponse, UploadedDocumentInfo
from app.dependencies import get_embedding_provider, get_vector_store

router = APIRouter()


@router.post("/documents", response_model=UploadResponse)
async def upload_documents(
    files: list[UploadFile] = File(...),
    session_id: str | None = Form(default=None),
    settings: Settings = Depends(get_settings),
    embeddings: EmbeddingProvider = Depends(get_embedding_provider),
    vector_store: VectorStore = Depends(get_vector_store),
):
    # A session groups one user's uploaded documents + chat history.
    # If the frontend doesn't send one, this is the first upload of a new
    # chat session, so we mint one.
    session_id = session_id or str(uuid.uuid4())

    uploaded_docs: list[UploadedDocumentInfo] = []

    for file in files:
        raw_bytes = await file.read()
        if not raw_bytes:
            raise HTTPException(status_code=400, detail=f"'{file.filename}' is empty")

        try:
            pages = parse_document(file.filename, raw_bytes)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if not pages:
            raise HTTPException(
                status_code=400,
                detail=f"No extractable text found in '{file.filename}' (is it a scanned/image-only PDF?)",
            )

        doc_id = str(uuid.uuid4())

        chunks = chunk_pages(
            pages,
            chunk_size_tokens=settings.chunk_size_tokens,
            chunk_overlap_tokens=settings.chunk_overlap_tokens,
        )

        # Embed the whole batch of chunks for this document at once —
        # much faster than one API/model call per chunk.
        chunk_texts = [c.text for c in chunks]
        chunk_embeddings = embeddings.embed_documents(chunk_texts)

        records = [
            VectorRecord(
                id=f"{doc_id}_{chunk.chunk_index}",
                embedding=chunk_embeddings[i],
                text=chunk.text,
                metadata={
                    "doc_id": doc_id,
                    "filename": file.filename,
                    "page_number": chunk.page_number if chunk.page_number is not None else -1,
                    "chunk_index": chunk.chunk_index,
                },
            )
            for i, chunk in enumerate(chunks)
        ]
        vector_store.add(session_id=session_id, records=records)

        doc_info = UploadedDocumentInfo(
            doc_id=doc_id,
            filename=file.filename,
            num_chunks=len(chunks),
            num_pages=len({c.page_number for c in chunks if c.page_number is not None}) or None,
        )
        uploaded_docs.append(doc_info)

    session_store.add_documents(session_id, uploaded_docs)

    return UploadResponse(session_id=session_id, documents=uploaded_docs)
