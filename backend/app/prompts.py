"""Prompt templates. Kept in one file so they are easy to read and tune."""
from .schemas import Evidence

QUESTION_LABELS = {
    "shiboudouki": ("志望動機", "why I want to join this company (motivation)"),
    "gakuchika": ("学生時代に力を入れたこと (ガクチカ)", "what I worked hardest on as a student"),
}


def format_evidence(evidence: list[Evidence]) -> str:
    return "\n\n".join(f"[{i + 1}] (from {e.source})\n{e.text}" for i, e in enumerate(evidence))


FIT_SYSTEM = """You are a careful career advisor for new-graduate job hunting in Japan.
Compare the candidate's documents with the job posting.
Only use facts that appear in the candidate excerpts. Never invent experience.
Reply with JSON only, in this exact shape:
{"score": <integer 0-100>, "summary": "<2 sentences>",
 "strengths": ["<short point>", ...], "gaps": ["<short point>", ...]}
Give 3-5 strengths and 2-4 gaps. Write the text in {language}."""


def fit_prompts(job: str, evidence: list[Evidence], language: str) -> tuple[str, str]:
    lang = "Japanese" if language == "ja" else "English"
    system = FIT_SYSTEM.replace("{language}", lang)
    user = f"JOB POSTING:\n{job}\n\nCANDIDATE EXCERPTS:\n{format_evidence(evidence)}"
    return system, user


DRAFT_SYSTEM = """You help a new-graduate candidate in Japan write entry sheet (ES) answers.
Write the answer to the question: {question}.
Rules:
- Use only experiences found in the candidate excerpts. Do not invent facts, numbers, or names.
- Connect the candidate's experience to what the job posting asks for.
- Write in {language}{style}.
- Keep it under {max_chars} characters.
Reply with JSON only: {"draft": "<the answer>"}"""


def draft_prompts(
    job: str, evidence: list[Evidence], question: str, language: str, max_chars: int
) -> tuple[str, str]:
    ja_label, en_label = QUESTION_LABELS[question]
    if language == "ja":
        lang, style, q = "Japanese", " using polite です/ます style", ja_label
    else:
        lang, style, q = "English", "", en_label
    system = (
        DRAFT_SYSTEM.replace("{question}", q)
        .replace("{language}", lang)
        .replace("{style}", style)
        .replace("{max_chars}", str(max_chars))
    )
    user = f"JOB POSTING:\n{job}\n\nCANDIDATE EXCERPTS:\n{format_evidence(evidence)}"
    return system, user
