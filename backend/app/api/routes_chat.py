"""
Chat endpoint. This is RAG steps 5-6 (retrieve -> generate) plus the
"no answer found" fallback and citation mapping, wired together, with
chat history read/written on either side.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.rag.retriever import Retriever
from app.rag.generator import AnswerGenerator, extract_cited_indices
from app.session.store import session_store
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    Citation,
    ChatHistoryMessage,
    ChatHistoryResponse,
)
from app.dependencies import get_retriever, get_generator

router = APIRouter()

# History window kept for LLM context — enough for follow-up questions
# ("what about section 2?") without letting the prompt grow unbounded.
MAX_HISTORY_TURNS_FOR_CONTEXT = 6


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    settings: Settings = Depends(get_settings),
    retriever: Retriever = Depends(get_retriever),
    generator: AnswerGenerator = Depends(get_generator),
):
    if not session_store.get_documents(request.session_id):
        raise HTTPException(
            status_code=400,
            detail="No documents uploaded for this session yet. Upload a document before asking a question.",
        )

    # --- Retrieval ---
    chunks = retriever.retrieve(
        session_id=request.session_id,
        question=request.question,
        top_k=settings.top_k_chunks,
    )

    if not chunks:
        # Nothing sufficiently relevant was found — this is the
        # "confidence / no answer found" fallback. We deliberately do NOT
        # call the LLM here: sending it no context and hoping it declines
        # to answer is less reliable than just short-circuiting ourselves.
        answer_text = (
            "I couldn't find anything relevant to that question in the "
            "uploaded documents. Try rephrasing, or check that the right "
            "document is uploaded."
        )
        session_store.add_message(
            request.session_id, ChatHistoryMessage(role="user", content=request.question)
        )
        session_store.add_message(
            request.session_id, ChatHistoryMessage(role="assistant", content=answer_text)
        )
        return ChatResponse(
            session_id=request.session_id,
            answer=answer_text,
            citations=[],
            no_answer_found=True,
        )

    # --- Build recent history for conversational context ---
    history = session_store.get_history(request.session_id)
    recent_history = history[-MAX_HISTORY_TURNS_FOR_CONTEXT * 2 :]
    llm_history = [{"role": m.role, "content": m.content} for m in recent_history]

    # --- Generation ---
    answer_text = generator.generate(
        question=request.question, chunks=chunks, chat_history=llm_history
    )

    # Only surface citations for sources the model actually referenced
    # inline (e.g. "[1]"), so the citation list matches the answer text.
    cited_indices = extract_cited_indices(answer_text)
    citations = [
        Citation(
            citation_number=i,
            doc_id=chunk.doc_id,
            filename=chunk.filename,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            snippet=chunk.text[:280] + ("..." if len(chunk.text) > 280 else ""),
            relevance_score=round(chunk.score, 3),
        )
        for i, chunk in enumerate(chunks, start=1)
        if i in cited_indices
    ]

    # Fall back to showing all retrieved chunks if the model didn't emit
    # any [n] markers (e.g. it answered in its own words) — better to show
    # the evidence than to show nothing. Numbers still match the [n]
    # positions the chunks were presented to the model under.
    if not citations:
        citations = [
            Citation(
                citation_number=i,
                doc_id=chunk.doc_id,
                filename=chunk.filename,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                snippet=chunk.text[:280] + ("..." if len(chunk.text) > 280 else ""),
                relevance_score=round(chunk.score, 3),
            )
            for i, chunk in enumerate(chunks, start=1)
        ]

    session_store.add_message(
        request.session_id, ChatHistoryMessage(role="user", content=request.question)
    )
    session_store.add_message(
        request.session_id,
        ChatHistoryMessage(role="assistant", content=answer_text, citations=citations),
    )

    return ChatResponse(
        session_id=request.session_id,
        answer=answer_text,
        citations=citations,
        no_answer_found=False,
    )


@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_history(session_id: str):
    history = session_store.get_history(session_id)
    return ChatHistoryResponse(session_id=session_id, messages=history)
