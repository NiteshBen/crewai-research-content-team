"""CLI entry point.

    python main.py "Generative AI trends in 2026"               # real run (needs GOOGLE_API_KEY)
    python main.py "Generative AI trends in 2026" --mock        # offline demo, no key needed
    python main.py "Generative AI trends in 2026" --out out/    # custom output dir
    python main.py "Generative AI trends in 2026" --model gemini/gemini-2.5-flash
"""
from __future__ import annotations

import argparse
import sys

from mock_llm_server import start_server
from research_team.crew import run


def main() -> None:
    ap = argparse.ArgumentParser(prog="research-team",
                                 description="Two-agent CrewAI pipeline: research a topic, "
                                             "draft a blog post.")
    ap.add_argument("topic", help="what the researcher should investigate")
    ap.add_argument("--mock", action="store_true",
                    help="run offline against the bundled mock LLM (no API key needed)")
    ap.add_argument("--out", default="output", help="output directory (default: ./output)")
    ap.add_argument("--model", default=None,
                    help="Gemini/LLM model identifier (default: gemini/gemini-2.0-flash)")
    args = ap.parse_args()

    topic = args.topic.strip()
    if not topic:
        print("error: topic cannot be empty", file=sys.stderr)
        sys.exit(2)

    if args.mock:
        start_server()
        print("[mock] local mock LLM server started on 127.0.0.1:8766")

    try:
        path = run(topic, mock=args.mock, out_dir=args.out, model=args.model)
        print(f"[done] blog post written to: {path}")
    except Exception as exc:
        print(f"[error] pipeline failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
