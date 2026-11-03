"""Task self-validation: baseline must fail, reference must pass, candidates match expectations."""

from __future__ import annotations

from dataclasses import dataclass

from . import review, runner
from .results import RunResult
from .task import Task


@dataclass
class Check:
    label: str
    ok: bool
    why: str
    result: RunResult | None = None


def verify_task(task: Task) -> list[Check]:
    checks: list[Check] = []

    base = runner.evaluate(task, None, "baseline")
    genuine_fail = base.status == "failed_tests" and base.count("failed") > 0
    kept_passing = base.count("passed") > 0
    checks.append(
        Check(
            "baseline",
            genuine_fail and kept_passing,
            "fails some tests and passes others"
            if genuine_fail and kept_passing
            else f"expected assertion failures plus passing guards, got {base.status} "
            f"({base.count('passed')} passed, {base.count('failed')} failed, "
            f"{base.count('error')} error)",
            base,
        )
    )

    ref = runner.evaluate(task, task.reference_patch, "reference")
    checks.append(Check("reference", ref.status == "passed", f"status {ref.status}", ref))

    for cand in task.candidates:
        res = runner.evaluate(task, task.root / cand.patch, f"candidate:{cand.patch}")
        checks.append(
            Check(
                res.label,
                res.status == cand.expect,
                f"expected {cand.expect}, got {res.status}",
                res,
            )
        )

    if task.expected_findings.exists() and task.reference_review.exists():
        expected = review.load_expected(task.expected_findings)
        graded = review.grade(task.id, expected, review.load_submission(task.reference_review))
        checks.append(
            Check(
                "reference review",
                graded.f1 == 1.0,
                f"recall {graded.recall:.2f}, precision {graded.precision:.2f}",
            )
        )
    return checks
