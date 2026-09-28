"""Minimal Hindsight spike: retain/recall round-trip + cross-process persistence.

Usage:
    python scripts/spike.py retain   # stores a unique fact (process 1)
    python scripts/spike.py recall   # recalls it in a SEPARATE process (process 2)

If recall (run 2) finds the fact stored by retain (run 1), memory persists
across sessions via the shared embedded daemon. No API keys needed:
embeddings are local, and the LLM provider defaults to llamacpp (local GGUF).
"""

import os
import sys
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.memory import MemoryBank  # noqa: E402

BANK = "spike-bank"
MARKER = uuid.uuid4().hex[:8]
FACT = (
    f"Spike fact {MARKER}: the customer's name is Lakshmi and she always "
    "buys 5kg whole wheat atta on the first Monday of the month."
)
QUERY = "What does the customer usually buy and when?"


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "retain"
    bank = MemoryBank(bank_id=BANK)

    if mode == "retain":
        bank.remember(FACT)
        print(f"[spike] retained: {FACT[:60]}...")
        print("[spike] now run: python scripts/spike.py recall   (separate process)")
        print(f"[spike] MARKER={MARKER}")
    elif mode == "recall":
        time.sleep(2)  # let async extraction settle
        hits = bank.recall(QUERY)
        print(f"[spike] recall returned {len(hits)} memories:")
        for h in hits:
            print("  -", h[:160])
        ok = any(MARKER in h or "Lakshmi" in h for h in hits)
        print("[spike] PERSISTENCE:", "OK ✅" if ok else "FAILED ❌")
        sys.exit(0 if ok else 1)
    else:
        print("usage: spike.py [retain|recall]")
        sys.exit(2)


if __name__ == "__main__":
    main()
