# Hindsight Agent — Hack With Hyderabad 3.0

An AI agent that **learns using Hindsight** (Vectorize's agent-memory system).
Every interaction is retained; every reply is grounded in recalled memories.
The demo makes the learning curve visible: flip memory OFF and the agent is
generic — flip it ON and the same question gets a personalized answer built
from weeks of history.

Built for **Hack With Hyderabad 3.0** — *"AI Agents That Learn Using Hindsight"*.

## The 60-second demo

1. `python scripts/seed_demo.py` — seeds 30 days of customer history (Lakshmi,
   her monthly atta order, home-delivery preference, a mixer grinder she asked
   about when it was out of stock).
2. `python app.py` — open the chat UI.
3. Ask **"Hi, do you have atta?"** with **Memory OFF** → generic answer.
4. Ask it again with **Memory ON** → *"Your usual 5kg bag, Lakshmi? Fresh batch
   just arrived — and the mixer grinder you asked about on Day 15 is back in
   stock."*
5. The side panel shows **exactly which memories were recalled** for each turn —
   the memory layer is visible, not a black box.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 1. Spike — prove retain/recall works and persists across processes (no keys needed)
python scripts/spike.py retain
python scripts/spike.py recall   # separate process -> persistence proof

# 2. Seed the demo story
python scripts/seed_demo.py

# 3. Run the demo UI
python app.py   # -> http://127.0.0.1:7860
```

Copy `.env.example` to `.env` to configure. **Never commit `.env`.**

### Bring your own LLM (optional)

Without a key, the agent runs on a transparent stub LLM — the full memory
before/after demo works with zero signup. To use a real model, set in `.env`:

```
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=<your key>
LLM_MODEL=qwen/qwen3-32b
```

Any OpenAI-compatible endpoint works (Groq, OpenAI, Ollama, LiteLLM...).

## How it works

```
user message
    │
    ▼
recall() ── Hindsight TEMPR search over the bank ──► relevant memories
    │                    (semantic + keyword + graph + temporal)
    ▼
LLM chat (system prompt + memories + message) ──► reply
    │
    ▼
retain() ── the exchange is stored ──► the NEXT turn is smarter
```

- `src/memory.py` — `MemoryBank`: the only module that talks to Hindsight.
  `remember()` / `recall()` / `reflect()`. Swap backends here, nowhere else.
- `src/agent.py` — idea-agnostic agent loop: recall → chat → retain.
- `src/llm.py` — OpenAI-compatible client; stub when no key is configured.
- `src/config.py` — everything via env vars.
- `scripts/spike.py` — minimal retain/recall + cross-process persistence proof.
- `scripts/seed_demo.py` — seeds the 30-day learning-curve story.
- `app.py` — Gradio demo UI with memory ON/OFF toggle + memory inspector.

### Hindsight, self-hosted, zero signup

The embedded daemon (`HindsightEmbedded`) runs a background Hindsight server
shared by all Python processes — memory persists across runs with no server
to manage. Defaults are fully local:

| Piece | Default | External calls |
|---|---|---|
| Database | embedded pg0 (PostgreSQL) | none |
| Embeddings | local `bge-small-en-v1.5` | none |
| Reranker | local | none |
| LLM (fact extraction) | `llamacpp` — auto-downloads a small GGUF on first run | none (after download) |

Point `HINDSIGHT_MODE=server` + `HINDSIGHT_URL` at a hosted Hindsight if you
prefer, and set `HINDSIGHT_LLM_PROVIDER` to `groq`/`openai`/etc. with a key.

## Project ideas

See [IDEAS.md](IDEAS.md) — three concrete proposals (ShopMind recommended):
a WhatsApp shopkeeper that never forgets, a sales assistant that remembers
every objection, and an on-call copilot with institutional memory.

## Rules of the road

- No API keys or secrets in files or git history. Ever.
- No account signups required to run the demo.
- Scan-only research; no PRs/comments on other people's repos.
