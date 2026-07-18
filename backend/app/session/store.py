"""
Simple in-memory session store.

Tracks, per session_id: which documents have been uploaded, and the chat
history (for context and for the GET history endpoint).

This is intentionally the simplest thing that works for a portfolio demo —
it's an in-process dict, so history is lost on server restart and won't
work across multiple backend instances. That's a fine tradeoff for an MVP.

To make this production-ready: swap this module for a Redis- or
SQLite-backed store keyed by session_id. Because routes only ever call
SessionStore's methods (never touch a dict directly), that's a localized
change — same pattern as the EmbeddingProvider/VectorStore swaps.
"""
import threading
from dataclasses import dataclass, field

from app.models.schemas import ChatHistoryMessage, UploadedDocumentInfo


@dataclass
class SessionData:
    documents: list[UploadedDocumentInfo] = field(default_factory=list)
    history: list[ChatHistoryMessage] = field(default_factory=list)


class SessionStore:
    def __init__(self):
        self._sessions: dict[str, SessionData] = {}
        self._lock = threading.Lock()

    def get_or_create(self, session_id: str) -> SessionData:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionData()
            return self._sessions[session_id]

    def add_documents(self, session_id: str, docs: list[UploadedDocumentInfo]) -> None:
        session = self.get_or_create(session_id)
        with self._lock:
            session.documents.extend(docs)

    def add_message(self, session_id: str, message: ChatHistoryMessage) -> None:
        session = self.get_or_create(session_id)
        with self._lock:
            session.history.append(message)

    def get_history(self, session_id: str) -> list[ChatHistoryMessage]:
        return self.get_or_create(session_id).history

    def get_documents(self, session_id: str) -> list[UploadedDocumentInfo]:
        return self.get_or_create(session_id).documents


# Module-level singleton, imported by routes
session_store = SessionStore()
