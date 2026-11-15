from fastapi.testclient import TestClient

from app.main import app, llm_dep
from app.llm import MockLLM

app.dependency_overrides[llm_dep] = lambda: MockLLM()
client = TestClient(app)

JOB = "We are hiring an AI engineer with Python, React and AWS experience."
DOCS = [{"name": "resume", "text": "Built a Python FastAPI service and a React front end."}]


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_fit_returns_score_and_evidence():
    r = client.post("/api/fit", json={"job_posting": JOB, "documents": DOCS})
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["score"] <= 100
    assert body["evidence"][0]["source"] == "resume"


def test_draft():
    r = client.post("/api/draft", json={"job_posting": JOB, "documents": DOCS, "language": "ja"})
    assert r.status_code == 200
    assert r.json()["draft"]


def test_extract_text_file():
    r = client.post("/api/extract", files={"file": ("es.txt", "ガクチカ本文".encode(), "text/plain")})
    assert r.json()["text"] == "ガクチカ本文"


def test_validation_rejects_empty_documents():
    r = client.post("/api/fit", json={"job_posting": JOB, "documents": []})
    assert r.status_code == 422
