import pytest

from research_team.config import resolve_llm
from research_team.output import slugify, write_post


def test_slugify():
    assert slugify("Generative AI trends in 2026!") == "generative-ai-trends-in-2026"
    assert slugify("   ") == "untitled"
    assert len(slugify("x" * 200)) <= 60


def test_write_post_creates_dated_markdown(tmp_path):
    path = write_post("My Topic", "# Title\n\nBody text.", tmp_path)
    text = path.read_text(encoding="utf-8")
    assert path.parent == tmp_path
    assert path.name.startswith(str(__import__("datetime").date.today()))
    assert 'topic: "My Topic"' in text
    assert "# Title" in text
    assert "mock LLM" in text  # provenance banner present


def test_resolve_llm_requires_key_outside_mock(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY"):
        resolve_llm(mock=False)
