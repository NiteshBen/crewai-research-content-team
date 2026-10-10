"""A tiny OpenAI-compatible mock LLM server (no dependencies, stdlib only).

Lets the full CrewAI pipeline run offline: crewai's LLM (via litellm) posts
/v1/chat/completions here, and the mock returns keyword-matched canned content.

Start standalone:
    python mock_llm_server.py            # serves on 127.0.0.1:8766
or import start_server() from tests / main.py --mock.
"""
from __future__ import annotations

import json
import re
import socket
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST, PORT = "127.0.0.1", 8766


def _extract_topic(messages: list[dict]) -> str:
    raw = json.dumps(messages)
    m = re.search(r"trends of ['\"]([^'\"]+)['\"]", raw, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(r"blog post about ['\"]([^'\"]+)['\"]", raw, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return "the Requested Topic"


def _get_research_brief(topic: str) -> str:
    return f"""## Research brief: {topic}

### Theme 1: Emerging Breakthroughs in {topic}
Recent developments show accelerating innovation in {topic}, delivering higher efficiency and quality across foundational workflows.

### Theme 2: Production Adoption and Scaling
Organizations are transitioning from isolated prototypes to production architectures, with enterprise frameworks maturing rapidly.

### Theme 3: Practical Implementation and Performance
Practical deployments emphasize lower latency, higher security, and cost effectiveness.

### Theme 4: Standards and Best Practices
Industry practitioners are establishing benchmarks, compliance safeguards, and quality assurance workflows.

### Open questions
- How will next-generation tooling address remaining integration bottlenecks in {topic}?
- Which deployment architectures will emerge as the standard across the industry?
"""


def _get_blog_post(topic: str) -> str:
    return f"""# Navigating {topic}: A Comprehensive Strategic Overview

As innovation accelerates, {topic} is rapidly shifting from emerging concept to essential capability. Here is an analysis of what is driving this transition and where the field is heading.

## The Core Shift
Recent advancements in {topic} demonstrate a significant leap forward in capabilities, making previously complex tasks reliable and cost-effective.

## From Experiments to Production
Teams are no longer treating {topic} as a novelty. Production architectures are standardizing around reliable pipelines and verifiable benchmarks.

## Practical Advantages
Deployments in {topic} consistently show measurable improvements in turnaround time, resource efficiency, and user experience.

## What this means for you
1. Assess your readiness: Review your existing technical stack to identify where {topic} yields the highest immediate leverage.
2. Standardize workflows: Build modular, repeatable processes rather than ad-hoc experiments.
3. Focus on verification: Establish clear evaluation metrics to continuously measure impact.
"""


def _canned_response(messages: list[dict]) -> str:
    text = json.dumps(messages).lower()
    topic = _extract_topic(messages)
    # The research task runs first; the writing task references the research context
    if "research brief" in text and "blog post" not in text:
        return _get_research_brief(topic)
    if any(k in text for k in ("blog post", "publishable", "title")):
        return _get_blog_post(topic)
    return "Understood."


class MockLLMHandler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        content = _canned_response(body.get("messages", []))
        resp = {
            "id": "chatcmpl-mock",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": body.get("model", "mock"),
            "choices": [{"index": 0,
                         "message": {"role": "assistant", "content": content},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": len(re.findall(r"\w+", content)),
                       "total_tokens": 2},
        }
        data = json.dumps(resp).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):  # silence the console during runs
        pass


def is_server_running(host: str = HOST, port: int = PORT) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex((host, port)) == 0
    except OSError:
        return False


def start_server(host: str = HOST, port: int = PORT) -> ThreadingHTTPServer | None:
    if is_server_running(host, port):
        return None
    server = ThreadingHTTPServer((host, port), MockLLMHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


if __name__ == "__main__":
    print(f"mock LLM server on http://{HOST}:{PORT}/v1/chat/completions (Ctrl+C to stop)")
    server = start_server()
    if server:
        server.serve_forever()
    else:
        print("Server is already running.")
