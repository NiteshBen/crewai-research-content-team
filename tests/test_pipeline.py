import pytest

from mock_llm_server import _canned_response, _extract_topic
from research_team.config import resolve_llm
from research_team.crew import run
from research_team.output import slugify, write_post


def test_slugify():
    assert slugify("Generative AI trends in 2026!") == "generative-ai-trends-in-2026"
    assert slugify("   ") == "untitled"
    assert len(slugify("x" * 200)) <= 60


def test_write_post_creates_dated_markdown(tmp_path):
    path = write_post("My Topic", "# Title\n\nBody text.", tmp_path, mock=True)
    text = path.read_text(encoding="utf-8")
    assert path.parent == tmp_path
    assert path.name.startswith(str(__import__("datetime").date.today()))
    assert 'topic: "My Topic"' in text
    assert "# Title" in text
    assert "provider: offline-mock-llm" in text
    assert "Offline Mock LLM" in text


def test_write_post_real_mode_banner(tmp_path):
    path = write_post("Real Topic", "# Real Title\n\nContent.", tmp_path, mock=False)
    text = path.read_text(encoding="utf-8")
    assert "provider: google-gemini" in text
    assert "Google Gemini" in text
    assert "In mock mode" not in text


def test_resolve_llm_requires_key_outside_mock(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY"):
        resolve_llm(mock=False)


def test_mock_llm_topic_extraction():
    messages = [{"content": "Research the current state and latest trends of 'Quantum Computing'."}]
    topic = _extract_topic(messages)
    assert topic == "Quantum Computing"
    resp = _canned_response(messages + [{"content": "research brief"}])
    assert "Quantum Computing" in resp


def test_empty_topic_rejected():
    with pytest.raises(ValueError, match="empty"):
        run("   ", mock=True)
