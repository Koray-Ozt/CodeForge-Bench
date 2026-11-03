"""Coarse wall-clock guard in a child process, so a runaway baseline is killed, not awaited.

The budget is ~20x above what a linear-ish solution needs on the reference machine, so
it only trips for algorithms that are still quadratic. It is a backstop; the precise
scaling check lives in tests/test_scaling.py.
"""

import os
import subprocess
import sys
from pathlib import Path

CHILD = """
import time
from ledger import reconcile
from workload import make_workload
txns, entries = make_workload(20000)
start = time.perf_counter()
reconcile(txns, entries)
print(time.perf_counter() - start)
"""
BUDGET_S = 2.0


def test_twenty_thousand_by_twenty_thousand_within_budget():
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(sys.path[1:] + [str(Path(__file__).parent)])
    try:
        proc = subprocess.run(
            [sys.executable, "-c", CHILD],
            capture_output=True, text=True, timeout=BUDGET_S * 5, env=env, check=False,
        )  # fmt: skip
    except subprocess.TimeoutExpired:
        raise AssertionError(f"reconcile still running after {BUDGET_S * 5:.0f}s") from None
    assert proc.returncode == 0, proc.stderr
    elapsed = float(proc.stdout.strip())
    assert elapsed < BUDGET_S, f"took {elapsed:.2f}s, budget {BUDGET_S:.1f}s"
