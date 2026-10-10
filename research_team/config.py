"""Configuration: Gemini key loading and LLM resolution (real or mock)."""
from __future__ import annotations

import os

try:  # optional at import time so tests can run without python-dotenv
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

DEFAULT_MODEL = "gemini/gemini-2.0-flash"
MOCK_BASE_URL = "http://127.0.0.1:8766/v1"


def get_api_key() -> str | None:
    """Google AI Studio key from the environment or a local .env file."""
    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")


def resolve_llm(mock: bool = False, model: str | None = None):
    """Return a CrewAI LLM.

    - mock=True points CrewAI at the bundled OpenAI-compatible mock server so the
      full pipeline runs offline (demo/tests, no key needed).
    - otherwise requires GOOGLE_API_KEY / GEMINI_API_KEY and uses configured Gemini model.
    """
    if mock:
        from crewai import LLM
        return LLM(model="openai/gpt-4o-mini", base_url=MOCK_BASE_URL,
                   api_key="mock", temperature=0.7)
    key = get_api_key()
    if not key:
        raise RuntimeError(
            "No Gemini API key found. Set GOOGLE_API_KEY (or GEMINI_API_KEY) in the "
            "environment or in a .env file - get one free at "
            "https://aistudio.google.com/apikey - or run with --mock for the offline demo."
        )
    from crewai import LLM
    target_model = model or os.getenv("CREWAI_MODEL", DEFAULT_MODEL)
    return LLM(model=target_model, api_key=key, temperature=0.7)
