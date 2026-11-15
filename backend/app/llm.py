"""LLM providers behind one small interface.

Every provider has the same method: generate_json(system, user) -> dict.
Swapping Gemini for Groq (or for Amazon Bedrock later) means adding one class,
without touching the rest of the app.
"""
import json
from typing import Protocol

import httpx

from .config import settings


class LLMError(RuntimeError):
    pass


class LLM(Protocol):
    def generate_json(self, system: str, user: str) -> dict: ...


def _parse_json(text: str) -> dict:
    text = text.strip()
    # Some models wrap JSON in ```json fences; strip them.
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{") :]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise LLMError(f"Model did not return valid JSON: {text[:200]}") from e


class GeminiLLM:
    """Google Gemini via its REST API (free tier from Google AI Studio)."""

    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise LLMError("GEMINI_API_KEY is not set")
        self.api_key, self.model = api_key, model

    def generate_json(self, system: str, user: str) -> dict:
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.4},
        }
        r = httpx.post(
            self.URL.format(model=self.model),
            headers={"x-goog-api-key": self.api_key},
            json=body,
            timeout=60,
        )
        if r.status_code != 200:
            raise LLMError(f"Gemini error {r.status_code}: {r.text[:300]}")
        try:
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise LLMError(f"Unexpected Gemini response: {r.text[:300]}") from e
        return _parse_json(text)


class GroqLLM:
    """Groq's OpenAI-compatible chat API (free tier, fast open models)."""

    URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise LLMError("GROQ_API_KEY is not set")
        self.api_key, self.model = api_key, model

    def generate_json(self, system: str, user: str) -> dict:
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"},
            "temperature": 0.4,
        }
        r = httpx.post(
            self.URL, headers={"Authorization": f"Bearer {self.api_key}"}, json=body, timeout=60
        )
        if r.status_code != 200:
            raise LLMError(f"Groq error {r.status_code}: {r.text[:300]}")
        return _parse_json(r.json()["choices"][0]["message"]["content"])


class MockLLM:
    """Returns fixed answers so the app and tests run with no API key."""

    def generate_json(self, system: str, user: str) -> dict:
        if '"score"' in system:
            return {
                "score": 72,
                "summary": "Mock result: solid CS fundamentals, some gaps in cloud experience.",
                "strengths": ["Python and web development experience", "CS degree"],
                "gaps": ["No production cloud experience mentioned"],
            }
        return {"draft": "(Mock draft) 貴社を志望する理由は、..."}


def get_llm() -> LLM:
    p = settings.llm_provider.lower()
    if p == "gemini":
        return GeminiLLM(settings.gemini_api_key, settings.gemini_model)
    if p == "groq":
        return GroqLLM(settings.groq_api_key, settings.groq_model)
    if p == "mock":
        return MockLLM()
    raise LLMError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")
