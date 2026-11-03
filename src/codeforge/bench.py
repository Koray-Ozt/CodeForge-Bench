"""Summaries of benchmark output produced inside the sandbox.

A task's `bench/*.py` script times its own workload (warmup, then N repeats) and writes
JSON of the form {"environment": {...}, "cases": {name: {"seconds": [..], "ops": int}}}.
This module only aggregates and renders those numbers; it never invents any.
"""

from __future__ import annotations

import statistics


def _stats(seconds: list[float]) -> dict[str, float]:
    ordered = sorted(seconds)
    q = (
        statistics.quantiles(ordered, n=4, method="inclusive")
        if len(ordered) >= 2
        else [ordered[0]] * 3
    )
    return {
        "median": statistics.median(ordered),
        "min": ordered[0],
        "max": ordered[-1],
        "iqr": q[2] - q[0],
        "n": len(ordered),
    }


def summarize(task_id: str, runs: list[dict]) -> str:
    by_label = {r["label"]: r for r in runs}
    base, ref = by_label["baseline"], by_label["reference"]
    env = ref.get("environment", {})
    lines = [
        f"# Benchmark: {task_id}",
        "",
        f"Python {env.get('python', '?')} in a container limited by Docker `--cpus` "
        f"({env.get('cpu_count', '?')} host CPUs visible), "
        f"repeats={ref.get('repeats', '?')}, warmup={ref.get('warmup', '?')}.",
        "",
        "| Case | Baseline median (s) | Reference median (s) | Speedup | Baseline IQR |"
        " Reference IQR | Output digest |",
        "|---|---|---|---|---|---|---|",
    ]
    for case, b in base["cases"].items():
        r = ref["cases"][case]
        bs, rs = _stats(b["seconds"]), _stats(r["seconds"])
        if b.get("digest") != r.get("digest"):
            raise ValueError(f"{case}: baseline and reference produced different output")
        speedup = bs["median"] / rs["median"] if rs["median"] else float("inf")
        lines.append(
            f"| {case} | {bs['median']:.4f} | {rs['median']:.4f} | {speedup:.1f}x | "
            f"{bs['iqr']:.4f} | {rs['iqr']:.4f} | `{r.get('digest', 'n/a')}` (identical) |"
        )
    lines += [
        "",
        "These are wall-clock timings from a single machine inside a CPU/memory-limited "
        "container. See the README for measurement limitations.",
        "",
    ]
    return "\n".join(lines)
