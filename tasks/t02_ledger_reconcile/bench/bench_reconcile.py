"""Benchmark for ledger.reconcile; runs inside the sandbox via `codeforge bench`.

Each case: build a deterministic workload, run `warmup` untimed iterations, then
`repeats` timed iterations with time.perf_counter. A digest of the result is recorded so
before/after runs can be checked for identical output.
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time

sys.path.insert(0, "/in/tests/visible")  # shared workload generator

from ledger import reconcile  # noqa: E402
from workload import make_workload  # noqa: E402

SIZES = (2000, 5000, 10000)
REPEATS = 5
WARMUP = 1


def digest(result) -> str:
    h = hashlib.sha256()
    for m in result.matches:
        h.update(f"{m.transaction_id}|{m.entry_id}|{m.day_diff}|{m.reference_hit};".encode())
    h.update(",".join(t.id for t in result.unmatched_transactions).encode())
    h.update(",".join(e.id for e in result.unmatched_entries).encode())
    return h.hexdigest()[:16]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    cases = {}
    for n in SIZES:
        txns, entries = make_workload(n)
        for _ in range(WARMUP):
            reconcile(txns, entries)
        seconds = []
        for _ in range(REPEATS):
            start = time.perf_counter()
            result = reconcile(txns, entries)
            seconds.append(time.perf_counter() - start)
        cases[f"{n}x{n}"] = {"seconds": seconds, "digest": digest(result)}

    payload = {
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "cpu_count": len(os.sched_getaffinity(0)),
            "machine": platform.machine(),
        },
        "repeats": REPEATS,
        "warmup": WARMUP,
        "cases": cases,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)


if __name__ == "__main__":
    main()
