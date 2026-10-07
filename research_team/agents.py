"""The two agents: a Researcher that produces a structured brief and a Writer
that turns it into a publication-ready blog post."""
from __future__ import annotations


def build_researcher(llm):
    from crewai import Agent

    return Agent(
        role="Senior Research Analyst",
        goal="Produce a well-organized research brief that a content writer can rely on",
        backstory=(
            "You are a meticulous technology research analyst. You structure findings into "
            "clear themes with concrete examples, keep claims grounded, and flag anything "
            "you are uncertain about instead of inventing sources. You never fabricate "
            "statistics or quotes."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def build_writer(llm):
    from crewai import Agent

    return Agent(
        role="Technology Content Writer",
        goal="Turn the researcher's brief into a compelling, publication-ready blog post",
        backstory=(
            "You are a technology blogger known for turning dense research into engaging, "
            "readable posts. You write a magnetic title and hook, use short sections and "
            "concrete examples, keep a neutral informative tone, and always end with a "
            "practical takeaway for the reader."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
