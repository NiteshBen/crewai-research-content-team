"""CLI entry point.

    python main.py "Generative AI trends in 2026"               # real run (needs GOOGLE_API_KEY)
    python main.py "Generative AI trends in 2026" --mock        # offline demo, no key needed
    python main.py "Generative AI trends in 2026" --out out/    # custom output dir
"""
from __future__ import annotations

import argparse

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
    args = ap.parse_args()

    if args.mock:
        start_server()
        print("[mock] local mock LLM server started on 127.0.0.1:8766")

    path = run(args.topic, mock=args.mock, out_dir=args.out)
    print(f"[done] blog post written to: {path}")


if __name__ == "__main__":
    main()
