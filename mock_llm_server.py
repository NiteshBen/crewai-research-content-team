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
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST, PORT = "127.0.0.1", 8766

RESEARCH = """## Research brief

### Theme 1: Small, efficient models are eating the frontier
Recent releases show a clear shift toward smaller models distilled from frontier systems,
delivering 80-90% of the quality at a fraction of the cost and latency.

### Theme 2: Agents move from demos to workflows
Multi-agent systems are being productized for research, coding, and content workflows, with
orchestration frameworks (CrewAI, LangGraph) reaching production maturity.

### Theme 3: On-device and edge inference
Phones and laptops now ship NPUs capable of running 3-7B parameter models locally, enabling
private, offline AI features.

### Theme 4: Regulation and provenance
Jurisdictions are moving toward labeling AI-generated content and auditing high-risk systems.

### Open questions
- How quickly will distilled models close the remaining quality gap?
- Which agent orchestration patterns become standard practice?
- Will on-device models change data-privacy expectations faster than regulation can respond?
"""

BLOG = """# The Quiet Revolution: How AI Got Smaller, Faster, and Closer

While headlines chased ever-bigger models, something more interesting happened in the
background: AI got small enough to live next to you. Here is what that shift looks like.

## Small models, big consequence
Distilled models now deliver most of the frontier quality at a fraction of the cost. For
teams building products, that changes the math: features that were uneconomical last year
fit this year's budget.

## Agents grow up
Multi-agent pipelines have graduated from impressive demos to dependable workflows -
research, coding assistance, content generation. The frameworks that orchestrate them are
stabilizing into real engineering choices rather than experiments.

## AI moves into your pocket
With modern NPUs, phones and laptops run capable models locally. Privacy improves, latency
drops, and features keep working on a plane.

## The rules catch up
Regulators are converging on provenance labeling and audits for high-risk uses. Teams that
build provenance in early will move faster than teams that retrofit it.

## What this means for you
1. Prototype with frontier models, ship with distilled ones - the cost curve is on your side.
2. Treat agent frameworks as infrastructure: pick one, learn it deeply, automate one real workflow.
3. Design for on-device early: local inference is becoming a product expectation, not a party trick.
"""


def _canned_response(messages: list[dict]) -> str:
    text = json.dumps(messages).lower()
    # the research task runs first; the writing task references the research context
    if "research brief" in text and "blog post" not in text:
        return RESEARCH
    if any(k in text for k in ("blog post", "publishable", "title")):
        return BLOG
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


def start_server(host: str = HOST, port: int = PORT) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), MockLLMHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


if __name__ == "__main__":
    print(f"mock LLM server on http://{HOST}:{PORT}/v1/chat/completions (Ctrl+C to stop)")
    start_server().serve_forever()
