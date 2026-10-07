"""Crew assembly and the high-level run() entry point."""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("CREWAI_TELEMETRY_OPT_OUT", "1")  # keep runs private and quiet

from .agents import build_researcher, build_writer  # noqa: E402
from .config import resolve_llm  # noqa: E402
from .output import write_post  # noqa: E402
from .tasks import research_task, writing_task  # noqa: E402


def build_crew(topic: str, llm):
    from crewai import Crew, Process

    researcher = build_researcher(llm)
    writer = build_writer(llm)
    return Crew(
        agents=[researcher, writer],
        tasks=[research_task(researcher, topic), writing_task(writer, topic)],
        process=Process.sequential,
        verbose=False,
    )


def run(topic: str, mock: bool = False, out_dir: str | Path = "output") -> Path:
    """Research + write a blog post about `topic`; returns the written file path.

    mock=True runs the whole pipeline against the bundled OpenAI-compatible
    mock server (offline demo, no API key required).
    """
    llm = resolve_llm(mock=mock)
    crew = build_crew(topic, llm)
    result = crew.kickoff()
    return write_post(topic, str(result.raw), out_dir)
