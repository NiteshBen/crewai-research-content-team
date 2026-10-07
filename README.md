# crewai-research-content-team

A two-agent **CrewAI** pipeline that researches a topic and drafts a publication-ready
blog post. Built by [Nitesh Beniwal](https://github.com/NiteshBen) - this is the working
implementation of the "AI Multi-Agent System for Research and Content Generation" project
(Python + CrewAI + Google Gemini 2.0).

## How it works

```
                 ┌──────────────────────┐         ┌──────────────────────┐
 topic ────────► │  Senior Research     │ ──────► │  Technology Content  │ ────► dated .md
                 │  Analyst (agent 1)   │  brief  │  Writer (agent 2)    │       blog post
                 └──────────────────────┘         └──────────────────────┘
                        research_task                    writing_task
                     (sequential CrewAI process)
```

- **Researcher agent** produces a structured brief: major themes, concrete examples,
  and explicit open questions - with a hard "never fabricate statistics or sources" rule
  baked into its backstory.
- **Writer agent** turns the brief into a 600-900 word markdown post (title, hook,
  subheaded sections, practical takeaways), adding nothing the brief doesn't support.
- Tasks run sequentially; the researcher's output is passed to the writer as context.
- The final post is saved as dated markdown with topic/date front matter and a
  provenance banner.

## Quick start (real run, Google Gemini)

```bash
pip install -r requirements.txt      # crewai 1.x, python-dotenv
copy .env.example .env               # paste your free key from https://aistudio.google.com/apikey
python main.py "Generative AI trends in 2026"
```

Requires Python 3.10-3.13 (CrewAI's supported range).

## Offline demo - no API key needed

The repo ships a tiny **OpenAI-compatible mock LLM server** (stdlib only). In mock mode
CrewAI talks to it instead of Gemini, so the full two-agent pipeline runs end-to-end
anywhere:

```bash
python main.py "Generative AI trends in 2026" --mock
```

`sample_output/2026-10-07-generative-ai-trends-in-2026.md` was produced exactly this way -
the mock's banner marks it clearly as mock-generated, so sample content is never confused
with a real Gemini run.

## Design decisions worth stealing

- **Anti-hallucination instructions live in agent backstories, not just prompts** - the
  researcher must separate established facts from speculation and cannot invent sources.
- **The writer is constrained to the brief** ("do not add claims the brief does not
  support"), which keeps the two-step pipeline honest instead of letting the LLM freestyle.
- **Provenance is automatic**: every output file carries the pipeline that made it and
  whether the content came from Gemini or the mock - important when sample outputs live
  in the repo.
- **Mock mode doubles as a test fixture**: the same server that powers `--mock` lets the
  test suite exercise the real CrewAI objects without network or keys.

## Project layout

```
research_team/
  config.py    # Gemini key loading, LLM resolution (real or mock)
  agents.py    # Researcher + Writer definitions
  tasks.py     # research_task + writing_task (topic interpolated)
  crew.py      # Crew assembly + run()
  output.py    # slugify + dated markdown with front matter
mock_llm_server.py  # stdlib OpenAI-compatible mock LLM
main.py             # CLI: topic [--mock] [--out DIR]
tests/              # pytest: output format, slug rules, key handling
```

## License

MIT - see [LICENSE](LICENSE).
