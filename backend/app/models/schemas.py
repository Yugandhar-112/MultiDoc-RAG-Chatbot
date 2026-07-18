"""
Pydantic models describing the shapes of data that flow through the API.
Defining these explicitly (rather than passing raw dicts around) gives us
automatic request validation and self-documenting OpenAPI docs at /docs.
"""
from pydantic import BaseModel, Field


class UploadedDocumentInfo(BaseModel):
    """Returned after a document is successfully ingested."""
    doc_id: str
    filename: str
    num_chunks: int
    num_pages: int | None = None


class UploadResponse(BaseModel):
    session_id: str
    documents: list[UploadedDocumentInfo]


class ChatRequest(BaseModel):
    session_id: str
    question: str = Field(..., min_length=1)


class Citation(BaseModel):
    """
    One piece of evidence backing an answer. Carrying doc_id/filename/page
    all the way from ingestion through retrieval into the final response is
    what makes the citation trustworthy rather than a guess bolted on after
    the fact.
    """
    citation_number: int  # matches the [n] marker Claude used inline in the answer
    doc_id: str
    filename: str
    page_number: int | None = None
    chunk_index: int
    snippet: str
    relevance_score: float


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: list[Citation]
    no_answer_found: bool = False


class ChatHistoryMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    citations: list[Citation] = []


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatHistoryMessage]
