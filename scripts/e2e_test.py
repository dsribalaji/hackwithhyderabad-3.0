"""End-to-end check: same question with memory OFF vs ON.

Proves the demo's core contrast without a browser:
  - memory OFF -> generic answer, no memories recalled
  - memory ON  -> personalized answer grounded in recalled memories

Usage: python scripts/e2e_test.py [--bank shopmind-demo]
Requires the bank to be seeded (see scripts/seed_demo.py).
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import Agent  # noqa: E402

QUESTION = "Hi, do you have atta?"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", default=os.environ.get("BANK_ID", "shopmind-demo"))
    args = ap.parse_args()

    off = Agent(bank_id=args.bank, memory_enabled=False).respond(QUESTION)
    on = Agent(bank_id=args.bank, memory_enabled=True).respond(QUESTION)

    print("=== MEMORY OFF ===")
    print(off.reply)
    print()
    print("=== MEMORY ON (recalled %d) ===" % len(on.memories_used))
    for m in on.memories_used:
        print("  [memory]", m[:110])
    print()
    print(on.reply)

    assert not off.memories_used, "memory OFF should recall nothing"
    assert on.memories_used, "memory ON should recall seeded memories"
    print()
    print("E2E: OK ✅")


if __name__ == "__main__":
    main()
