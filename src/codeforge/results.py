"""Result records and JUnit parsing."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

STATUSES = ("passed", "failed_tests", "patch_rejected", "timeout", "oom", "infra_error")
MAX_JUNIT_BYTES = 5 * 1024 * 1024
MAX_MESSAGE_CHARS = 600


@dataclass
class TestOutcome:
    __test__ = False  # not a pytest class

    name: str
    outcome: str  # passed | failed | error | skipped
    duration_s: float
    message: str = ""


@dataclass
class RunResult:
    task_id: str
    label: str
    status: str
    exit_code: int | None = None
    duration_s: float = 0.0
    tests: list[TestOutcome] = field(default_factory=list)
    patch_sha256: str | None = None
    detail: str = ""
    output_tail: str = ""
    limits: dict[str, Any] = field(default_factory=dict)
    image_id: str = ""
    defects: dict[str, Any] | None = None

    def count(self, outcome: str) -> int:
        return sum(1 for t in self.tests if t.outcome == outcome)

    @property
    def score(self) -> float:
        """Fraction of tests passed; 0.0 when no tests ran."""
        return self.count("passed") / len(self.tests) if self.tests else 0.0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["summary"] = {
            "total": len(self.tests),
            "passed": self.count("passed"),
            "failed": self.count("failed"),
            "error": self.count("error"),
            "skipped": self.count("skipped"),
            "score": round(self.score, 4),
        }
        return data


def summarize_defects(tests: list[TestOutcome], pattern: str) -> dict[str, Any]:
    """Group tests by the defect id captured by `pattern`; a defect is resolved if all pass."""
    groups: dict[str, list[bool]] = {}
    for t in tests:
        if m := re.search(pattern, t.name):
            groups.setdefault(m.group(1), []).append(t.outcome == "passed")
    unresolved = sorted(k for k, v in groups.items() if not all(v))
    return {
        "total": len(groups),
        "resolved": len(groups) - len(unresolved),
        "unresolved": unresolved,
    }


def parse_junit(path: Path) -> list[TestOutcome]:
    """Parse pytest's JUnit XML. The file is written by the sandbox, so treat it as untrusted."""
    if path.stat().st_size > MAX_JUNIT_BYTES:
        raise ValueError("junit.xml exceeds size limit")
    root = ET.parse(path).getroot()  # noqa: S314 - size-capped, stdlib expat has entity limits
    outcomes: list[TestOutcome] = []
    for case in root.iter("testcase"):
        name = f"{case.get('classname', '')}::{case.get('name', '')}".strip(":")
        # Strip the staging directory prefix so names are stable.
        name = name.replace("_cf_tests.", "")
        outcome, message = "passed", ""
        for child in case:
            if child.tag == "failure":
                outcome, message = "failed", child.get("message", "")
            elif child.tag == "error":
                outcome, message = "error", child.get("message", "")
            elif child.tag == "skipped":
                outcome, message = "skipped", child.get("message", "")
        outcomes.append(
            TestOutcome(
                name=name,
                outcome=outcome,
                duration_s=float(case.get("time", 0) or 0),
                message=message[:MAX_MESSAGE_CHARS],
            )
        )
    return outcomes
