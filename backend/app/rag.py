"""Retrieval: find the parts of the user's documents most relevant to a job posting.

How it works (simple version, no paid embedding API needed):
1. Split each document into overlapping chunks of ~400 characters.
2. Turn each chunk into a "bag of character n-grams" (pieces of 2-3 characters).
   Character n-grams work for both Japanese (no spaces between words) and English.
3. Weight the n-grams with TF-IDF: rare n-grams (like "Kubernetes") count more
   than common ones (like "the" or "した").
4. Score each chunk by cosine similarity to the job posting and keep the top k.

The chunks we keep are passed to the LLM, so its answer is grounded in what
the user actually wrote instead of invented. That is the "R" in RAG.
"""
import math
import re
from collections import Counter
from dataclasses import dataclass

from .schemas import Document, Evidence


@dataclass
class Chunk:
    source: str
    text: str


def split_into_chunks(doc: Document, size: int, overlap: int) -> list[Chunk]:
    text = re.sub(r"\s+", " ", doc.text).strip()
    if not text:
        return []
    chunks = []
    step = max(1, size - overlap)
    for start in range(0, len(text), step):
        piece = text[start : start + size]
        chunks.append(Chunk(source=doc.name, text=piece))
        if start + size >= len(text):
            break
    return chunks


def ngrams(text: str, sizes=(2, 3)) -> Counter:
    text = text.lower()
    grams: Counter = Counter()
    for n in sizes:
        for i in range(len(text) - n + 1):
            gram = text[i : i + n]
            if not gram.isspace():
                grams[gram] += 1
    return grams


def _tfidf(counts: Counter, idf: dict[str, float]) -> dict[str, float]:
    return {g: c * idf.get(g, 0.0) for g, c in counts.items()}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    dot = sum(v * b.get(k, 0.0) for k, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def retrieve(query: str, docs: list[Document], top_k: int, size: int, overlap: int) -> list[Evidence]:
    chunks = [c for d in docs for c in split_into_chunks(d, size, overlap)]
    if not chunks:
        return []

    chunk_counts = [ngrams(c.text) for c in chunks]
    # Document frequency: in how many chunks does each n-gram appear?
    df: Counter = Counter()
    for counts in chunk_counts:
        df.update(counts.keys())
    n = len(chunks)
    idf = {g: math.log((1 + n) / (1 + f)) + 1 for g, f in df.items()}

    q_vec = _tfidf(ngrams(query), idf)
    scored = [
        Evidence(source=c.source, text=c.text, score=round(_cosine(q_vec, _tfidf(cc, idf)), 4))
        for c, cc in zip(chunks, chunk_counts)
    ]
    scored.sort(key=lambda e: e.score, reverse=True)
    return scored[:top_k]
