from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api import routes_documents, routes_chat, routes_health

settings = get_settings()

app = FastAPI(
    title="Multi-Document RAG Chatbot API",
    description="Upload documents, then ask grounded, cited questions about them.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router, tags=["health"])
app.include_router(routes_documents.router, tags=["documents"])
app.include_router(routes_chat.router, tags=["chat"])
