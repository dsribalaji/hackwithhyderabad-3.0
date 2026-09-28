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
QUERY = "What does the customer usually buy and when?"
MARKER_FILE = os.path.join(os.path.dirname(__file__), ".spike_marker")


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "retain"
    bank = MemoryBank(bank_id=BANK)

    if mode == "retain":
        # Marker is written to a file so the separate recall process can
        # verify the EXACT fact (a fresh uuid per process would never match).
        marker = uuid.uuid4().hex[:8]
        fact = (
            f"Spike fact {marker}: the customer's name is Lakshmi and she always "
            "buys 5kg whole wheat atta on the first Monday of the month."
        )
        with open(MARKER_FILE, "w") as f:
            f.write(marker)
        bank.remember(fact)
        print(f"[spike] retained: {fact[:60]}...")
        print("[spike] now run: python scripts/spike.py recall   (separate process)")
        print(f"[spike] MARKER={marker}")
    elif mode == "recall":
        marker = ""
        if os.path.exists(MARKER_FILE):
            with open(MARKER_FILE, "r") as f:
                marker = f.read().strip()
        time.sleep(2)  # let async extraction settle
        hits = bank.recall(QUERY)
        print(f"[spike] recall returned {len(hits)} memories:")
        for h in hits:
            print("  -", h[:160])
        ok = any((marker and marker in h) or "Lakshmi" in h for h in hits)
        print("[spike] PERSISTENCE:", "OK ✅" if ok else "FAILED ❌")
        sys.exit(0 if ok else 1)
    else:
        print("usage: spike.py [retain|recall]")
        sys.exit(2)


if __name__ == "__main__":
    main()
