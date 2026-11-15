"""FastAPI app: the HTTP layer. Each endpoint is: retrieve -> prompt -> LLM -> validate."""
import io

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

from . import prompts
from .config import settings
from .llm import LLM, LLMError, get_llm
from .rag import retrieve
from .ratelimit import check_rate_limit
from .schemas import DraftRequest, DraftResponse, ExtractResponse, FitRequest, FitResponse

app = FastAPI(title="Shukatsu Assistant API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def llm_dep() -> LLM:
    try:
        return get_llm()
    except LLMError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health():
    return {"status": "ok", "provider": settings.llm_provider}


@app.post("/api/extract", response_model=ExtractResponse)
async def extract(file: UploadFile = File(...)):
    """Turn an uploaded PDF or text file into plain text."""
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File is larger than 5 MB")
    name = file.filename or "upload"
    if name.lower().endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(data))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            raise HTTPException(400, "Could not read this PDF")
    else:
        text = data.decode("utf-8", errors="replace")
    if not text.strip():
        raise HTTPException(400, "No text found in the file")
    return ExtractResponse(name=name, text=text)


def _evidence(job: str, docs):
    return retrieve(job, docs, settings.top_k, settings.chunk_size, settings.chunk_overlap)


@app.post("/api/fit", response_model=FitResponse, dependencies=[Depends(check_rate_limit)])
def fit(req: FitRequest, llm: LLM = Depends(llm_dep)):
    evidence = _evidence(req.job_posting, req.documents)
    system, user = prompts.fit_prompts(req.job_posting, evidence, req.language)
    try:
        out = llm.generate_json(system, user)
        return FitResponse(
            score=max(0, min(100, int(out["score"]))),
            summary=str(out.get("summary", "")),
            strengths=[str(s) for s in out.get("strengths", [])],
            gaps=[str(g) for g in out.get("gaps", [])],
            evidence=evidence,
        )
    except (LLMError, KeyError, ValueError, TypeError) as e:
        raise HTTPException(502, f"LLM failed: {e}")


@app.post("/api/draft", response_model=DraftResponse, dependencies=[Depends(check_rate_limit)])
def draft(req: DraftRequest, llm: LLM = Depends(llm_dep)):
    evidence = _evidence(req.job_posting, req.documents)
    system, user = prompts.draft_prompts(
        req.job_posting, evidence, req.question, req.language, req.max_chars
    )
    try:
        out = llm.generate_json(system, user)
        return DraftResponse(draft=str(out["draft"]), evidence=evidence)
    except (LLMError, KeyError) as e:
        raise HTTPException(502, f"LLM failed: {e}")
