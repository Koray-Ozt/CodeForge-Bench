"""Deterministic grading of a code review against a ground-truth defect list.

A submitted finding matches an expected defect when it names the same file and a line
within `tolerance` of the defect's line range. Matching is one-to-one; when several
submitted findings qualify, the one with the right category and the closest line wins.
There is no LLM judge: category is a fixed vocabulary and wording is not graded.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

CATEGORIES = ("security", "correctness", "reliability", "error-handling", "state", "performance")
MAX_REVIEW_BYTES = 256 * 1024
MAX_FINDINGS = 200


class ReviewError(Exception):
    pass


@dataclass(frozen=True)
class Expected:
    id: str
    file: str
    start: int
    end: int
    category: str
    title: str
    alt_lines: tuple[int, ...] = ()  # other lines where the same defect is visible


@dataclass(frozen=True)
class Submitted:
    file: str
    line: int
    category: str
    summary: str


@dataclass
class ReviewGrade:
    task_id: str
    expected: int
    submitted: int
    matched: list[dict] = field(default_factory=list)
    missed: list[str] = field(default_factory=list)
    false_positives: list[int] = field(default_factory=list)

    @property
    def recall(self) -> float:
        return len(self.matched) / self.expected if self.expected else 1.0

    @property
    def precision(self) -> float:
        return len(self.matched) / self.submitted if self.submitted else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if p + r else 0.0

    @property
    def category_accuracy(self) -> float:
        if not self.matched:
            return 0.0
        return sum(1 for m in self.matched if m["category_match"]) / len(self.matched)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["recall"] = round(self.recall, 4)
        data["precision"] = round(self.precision, 4)
        data["f1"] = round(self.f1, 4)
        data["category_accuracy"] = round(self.category_accuracy, 4)
        return data


def _normalize(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def load_expected(path: Path) -> list[Expected]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [
            Expected(**{**item, "alt_lines": tuple(item.get("alt_lines", ()))})
            for item in raw["findings"]
        ]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ReviewError(f"cannot read expected findings {path}: {exc}") from exc


def load_submission(path: Path) -> list[Submitted]:
    """Parse a candidate's review.json strictly; it is untrusted data, never executed."""
    try:
        if path.stat().st_size > MAX_REVIEW_BYTES:
            raise ReviewError("review.json is larger than 256 KB")
        raw = json.loads(path.read_text(encoding="utf-8"))
        items = raw["findings"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ReviewError(f"invalid review file: {exc}") from exc
    if not isinstance(items, list) or len(items) > MAX_FINDINGS:
        raise ReviewError(f"'findings' must be a list of at most {MAX_FINDINGS} items")
    out = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ReviewError(f"finding {i} is not an object")
        file, line = item.get("file"), item.get("line")
        if not isinstance(file, str) or not isinstance(line, int) or isinstance(line, bool):
            raise ReviewError(f"finding {i} needs string 'file' and integer 'line'")
        out.append(
            Submitted(
                _normalize(file),
                line,
                str(item.get("category", "")),
                str(item.get("summary", ""))[:500],
            )
        )
    return out


def grade(
    task_id: str, expected: list[Expected], submitted: list[Submitted], tolerance: int = 1
) -> ReviewGrade:
    pairs = []
    for e in expected:
        for index, s in enumerate(submitted):
            if _normalize(e.file) != s.file:
                continue
            distance = min(
                [max(e.start - s.line, s.line - e.end, 0)]
                + [abs(s.line - alt) for alt in e.alt_lines]
            )
            if distance <= tolerance:
                pairs.append((s.category != e.category, distance, e.id, index))
    pairs.sort()

    result = ReviewGrade(task_id, len(expected), len(submitted))
    used_expected: set[str] = set()
    used_submitted: set[int] = set()
    for category_miss, distance, expected_id, index in pairs:
        if expected_id in used_expected or index in used_submitted:
            continue
        used_expected.add(expected_id)
        used_submitted.add(index)
        result.matched.append(
            {"expected": expected_id, "submitted_index": index,
             "category_match": not category_miss, "line_distance": distance}
        )  # fmt: skip
    result.missed = [e.id for e in expected if e.id not in used_expected]
    result.false_positives = [i for i in range(len(submitted)) if i not in used_submitted]
    return result


def to_markdown(g: ReviewGrade, expected: list[Expected]) -> str:
    titles = {e.id: e.title for e in expected}
    lines = [
        f"# Review grade: {g.task_id}",
        "",
        f"- Recall: **{g.recall:.2f}** ({len(g.matched)}/{g.expected} defects found)",
        f"- Precision: **{g.precision:.2f}** ({len(g.matched)}/{g.submitted} findings were real)",
        f"- F1: {g.f1:.2f}, category accuracy on matches: {g.category_accuracy:.2f}",
    ]
    if g.missed:
        lines += ["", "Missed defects:", ""] + [f"- {i}: {titles[i]}" for i in g.missed]
    if g.false_positives:
        lines += ["", f"False-positive finding indexes: {g.false_positives}"]
    return "\n".join(lines) + "\n"
