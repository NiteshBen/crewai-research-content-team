"""Task definitions. The topic is interpolated directly into the descriptions,
so kickoff() needs no inputs dict."""
from __future__ import annotations


def research_task(agent, topic: str):
    from crewai import Task

    return Task(
        description=(
            f"Research the current state and latest trends of '{topic}'. Produce a structured "
            f"research brief with: 1) the 4-6 most significant developments or themes, "
            f"2) one or two concrete examples or use cases per theme, "
            f"3) open questions or risks worth watching. "
            f"Clearly separate well-established facts from speculation. Do not invent "
            f"statistics, sources, or quotes."
        ),
        expected_output=(
            "A markdown brief of 300-500 words with themed sections, concrete examples, "
            "and an explicit 'open questions' section."
        ),
        agent=agent,
    )


def writing_task(agent, topic: str):
    from crewai import Task

    return Task(
        description=(
            f"Using the researcher's brief, write a publishable blog post about '{topic}'. "
            f"Requirements: a specific attention-grabbing title, a short hook paragraph, "
            f"3-5 sections with markdown subheadings, grounded in the brief (do not add "
            f"claims the brief does not support), and a closing 'What this means for you' "
            f"section with 3 practical takeaways."
        ),
        expected_output=(
            "A complete blog post in markdown (600-900 words): title as an H1, hook, "
            "3-5 subheaded sections, and a takeaways section."
        ),
        agent=agent,
    )
