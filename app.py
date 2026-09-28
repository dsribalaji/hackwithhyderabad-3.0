"""Gradio demo UI.

The whole pitch in one screen:
  - chat with the agent
  - MEMORY ON/OFF toggle -> the before/after contrast judges score
  - "What the agent remembered" panel -> makes the memory layer VISIBLE

Run:
    python app.py
Then open the printed URL. Use scripts/seed_demo.py first for the full story.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import src.config  # noqa: F401 — must come first: sanitizes proxy env for httpx
import gradio as gr  # noqa: E402

from src.agent import Agent  # noqa: E402
from src.memory import MemoryBank  # noqa: E402  (imported for side-effect: env sanitizing)

BANK_ID = os.environ.get("BANK_ID", "shopmind-demo")


def make_agent(memory_on: bool) -> Agent:
    return Agent(bank_id=BANK_ID, memory_enabled=memory_on)


agent_on = make_agent(True)
agent_off = make_agent(False)


def chat_fn(message: str, history: list, memory_on: bool):
    agent = agent_on if memory_on else agent_off
    result = agent.respond(message)
    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": result.reply},
    ]
    if result.memories_used:
        mem_md = "\n".join(f"- {m}" for m in result.memories_used)
    else:
        mem_md = "_No memories recalled (memory off or bank empty)._"
    status = (
        f"Memory: **{'ON' if result.memory_enabled else 'OFF'}** · "
        f"recalled **{len(result.memories_used)}** memories · "
        f"LLM: `{agent.llm.name}`"
    )
    return history, mem_md, status


def reset_bank():
    # Fresh bank id each reset keeps the demo reproducible.
    global agent_on, agent_off
    import time

    new_bank = f"{BANK_ID}-reset-{int(time.time())}"
    os.environ["BANK_ID"] = new_bank
    agent_on = Agent(bank_id=new_bank, memory_enabled=True)
    agent_off = Agent(bank_id=new_bank, memory_enabled=False)
    return [], "_Bank reset. Seed it again with scripts/seed_demo.py._", ""


with gr.Blocks(title="Hindsight Agent Demo") as demo:
    gr.Markdown(
        """# Agent with a memory 🧠
        Built on **Hindsight** — the agent retains every interaction and recalls
        what matters. Flip the **Memory** switch to see the before/after judges score:
        the *same* question gets a generic answer with memory OFF and a
        personalized one with memory ON."""
    )
    with gr.Row():
        memory_toggle = gr.Checkbox(label="Memory ON", value=True)
        reset_btn = gr.Button("Reset bank", variant="secondary")
    status_md = gr.Markdown("")
    with gr.Row():
        chatbot = gr.Chatbot(label="Chat", height=420)
        memories_md = gr.Markdown(label="What the agent remembered")
    msg = gr.Textbox(label="Your message", placeholder="Hi, do you have atta?")

    def _submit(message, history, memory_on):
        history, mem_md, status = chat_fn(message, history, memory_on)
        return history, mem_md, status, ""

    msg.submit(
        _submit, [msg, chatbot, memory_toggle], [chatbot, memories_md, status_md, msg]
    )
    reset_btn.click(reset_bank, None, [chatbot, memories_md, status_md])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
