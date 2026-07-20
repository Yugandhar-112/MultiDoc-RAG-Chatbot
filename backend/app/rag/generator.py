"""
RAG STEP 6: Generation.

Takes the user's question + the retrieved chunks and asks Gemini to answer
*using only that context*, citing which numbered source(s) it drew on.

Two things keep this grounded rather than free-associating:
  1. The system instruction explicitly tells the model to say it doesn't
     know if the context doesn't contain the answer, instead of guessing.
  2. Each chunk is presented to the model with a bracketed number (e.g.
     [1], [2]) and the model is told to cite those numbers inline. We then
     parse which numbers actually appear in the answer and only return
     *those* chunks as citations — so the citations shown to the user are
     the ones the model says it actually used, not just everything that
     was retrieved.

Uses Google's Gemini API (via the `google-genai` SDK) rather than a paid
LLM provider, so this whole pipeline can run on Gemini's free tier with no
billing setup — see README for API key setup and free-tier limits.
"""
import re

from google import genai
from google.genai import types

from app.rag.retriever import RetrievedChunk

SYSTEM_PROMPT = """You are a helpful assistant that answers questions strictly using the provided document excerpts.

Rules:
- Only use information from the numbered excerpts below to answer.
- Every factual claim in your answer must be followed by a citation marker like [1] or [2] referencing the excerpt(s) it came from.
- If the excerpts do not contain enough information to answer the question, say clearly that you couldn't find the answer in the uploaded documents. Do not guess or use outside knowledge.
- Be concise and direct."""


def build_context_block(chunks: list[RetrievedChunk]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        location = f"page {chunk.page_number}" if chunk.page_number else "unspecified location"
        parts.append(f"[{i}] (from \"{chunk.filename}\", {location})\n{chunk.text}")
    return "\n\n".join(parts)


def extract_cited_indices(answer_text: str) -> set[int]:
    """Find every [n] marker the model actually used in its answer."""
    return {int(n) for n in re.findall(r"\[(\d+)\]", answer_text)}


class AnswerGenerator:
    def __init__(self, api_key: str, model: str):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        chat_history: list[dict] | None = None,
    ) -> str:
        """
        Returns the raw answer text (with [n] citation markers still in it).
        The route layer is responsible for mapping those markers back to
        Citation objects using the same `chunks` list passed in here.
        """
        context_block = build_context_block(chunks)

        user_turn = (
            f"Document excerpts:\n\n{context_block}\n\n"
            f"Question: {question}"
        )

        # Gemini's chat history uses role="model" where Anthropic/OpenAI use
        # "assistant" — translate the app's internal history format (which
        # is provider-agnostic) into Gemini's expected shape.
        contents = []
        for turn in chat_history or []:
            role = "model" if turn["role"] == "assistant" else "user"
            contents.append(
                types.Content(role=role, parts=[types.Part.from_text(text=turn["content"])])
            )
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_turn)]))

        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=1024,
            ),
        )

        return response.text or ""
