"""
RAG STEP 2: Chunking.

Why chunk at all? Embedding models and LLM context windows both work
better with small, semantically coherent pieces of text rather than
whole documents:
  - Embeddings of a giant page are "muddy" — they average together many
    unrelated ideas, so similarity search gets worse.
  - Smaller chunks let retrieval pull in exactly the relevant paragraph
    instead of a whole page of mostly-irrelevant text, which keeps the
    LLM's context window focused and cheap.

Why overlap? If a sentence describing the answer straddles a chunk
boundary, a hard cut can separate a question from its answer or a claim
from its evidence. A small overlap (here in tokens, not characters)
ensures that boundary content appears in full in at least one chunk.

We chunk by *token* count (via tiktoken) rather than characters/words
because token count is what actually determines how much of the LLM's
context window a chunk will consume — it's the more faithful unit here,
even though we're using Claude and not GPT for generation (tiktoken is a
close-enough proxy for chunk-sizing purposes; it doesn't need to be
Claude's exact tokenizer).
"""
from dataclasses import dataclass

import tiktoken

from app.ingestion.parsers import ParsedPage

_encoding = tiktoken.get_encoding("cl100k_base")


@dataclass
class Chunk:
    chunk_index: int
    page_number: int | None
    text: str


def chunk_pages(
    pages: list[ParsedPage],
    chunk_size_tokens: int = 500,
    chunk_overlap_tokens: int = 75,
) -> list[Chunk]:
    """
    Turn parsed pages into overlapping chunks, tagging each chunk with the
    page number it came from so citations can point back to a location.

    We chunk each page independently (rather than concatenating the whole
    document first) so that a chunk never spans two different page
    numbers — that would make "page X" citations misleading.
    """
    chunks: list[Chunk] = []
    chunk_index = 0

    for page in pages:
        token_ids = _encoding.encode(page.text)
        if not token_ids:
            continue

        start = 0
        while start < len(token_ids):
            end = min(start + chunk_size_tokens, len(token_ids))
            chunk_token_ids = token_ids[start:end]
            chunk_text = _encoding.decode(chunk_token_ids).strip()

            if chunk_text:
                chunks.append(
                    Chunk(
                        chunk_index=chunk_index,
                        page_number=page.page_number,
                        text=chunk_text,
                    )
                )
                chunk_index += 1

            if end == len(token_ids):
                break
            # Slide the window forward, leaving `chunk_overlap_tokens` of
            # the previous chunk visible at the start of the next one.
            start = end - chunk_overlap_tokens

    return chunks
