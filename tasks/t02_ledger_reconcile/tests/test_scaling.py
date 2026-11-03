"""Implementation-agnostic complexity check using executed-line counts.

Wall-clock time is noisy, so this test counts how many source lines of the `ledger`
package execute (via `sys.monitoring`, Python 3.12+). Quadrupling the input should about
quadruple the count for a near-linear algorithm and about 16x it for a quadratic one.
"""

import sys
from pathlib import Path

import ledger
from ledger import reconcile
from workload import make_workload

PACKAGE_DIR = str(Path(ledger.__file__).parent)
TOOL = sys.monitoring.PROFILER_ID


def executed_lines(n: int) -> int:
    transactions, entries = make_workload(n)
    count = 0

    def on_line(code, line):
        nonlocal count
        if code.co_filename.startswith(PACKAGE_DIR):
            count += 1
            return None
        return sys.monitoring.DISABLE

    sys.monitoring.use_tool_id(TOOL, "codeforge-scaling")
    sys.monitoring.register_callback(TOOL, sys.monitoring.events.LINE, on_line)
    sys.monitoring.set_events(TOOL, sys.monitoring.events.LINE)
    try:
        reconcile(transactions, entries)
    finally:
        sys.monitoring.set_events(TOOL, 0)
        sys.monitoring.register_callback(TOOL, sys.monitoring.events.LINE, None)
        sys.monitoring.free_tool_id(TOOL)
        sys.monitoring.restart_events()
    return count


def test_work_grows_near_linearly_with_input_size():
    small, large = executed_lines(200), executed_lines(800)
    ratio = large / small
    assert ratio < 7.0, f"4x input caused {ratio:.1f}x more executed lines (quadratic is ~16x)"
