"""Request and response shapes. FastAPI uses these to validate JSON
and to generate the interactive API docs at /docs."""
from typing import Literal

from pydantic import BaseModel, Field


class Document(BaseModel):
    name: str = Field(..., examples=["resume.pdf"])
    text: str


class Evidence(BaseModel):
    """A chunk of the user's own documents that the answer is based on."""
    source: str
    text: str
    score: float


class FitRequest(BaseModel):
    job_posting: str = Field(..., min_length=20)
    documents: list[Document] = Field(..., min_length=1)
    language: Literal["ja", "en"] = "en"


class FitResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    summary: str
    strengths: list[str]
    gaps: list[str]
    evidence: list[Evidence]


class DraftRequest(BaseModel):
    job_posting: str = Field(..., min_length=20)
    documents: list[Document] = Field(..., min_length=1)
    question: Literal["shiboudouki", "gakuchika"] = "shiboudouki"
    language: Literal["ja", "en"] = "ja"
    max_chars: int = Field(400, ge=100, le=2000)


class DraftResponse(BaseModel):
    draft: str
    evidence: list[Evidence]


class ExtractResponse(BaseModel):
    name: str
    text: str
