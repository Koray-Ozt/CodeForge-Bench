"""Task definition loading."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CATEGORIES = {"race-condition", "performance", "refactoring", "code-review", "feature"}


class TaskError(Exception):
    pass


@dataclass(frozen=True)
class Candidate:
    """A hand-written patch with the outcome the runner is expected to report."""

    patch: str
    expect: str
    note: str = ""


@dataclass(frozen=True)
class BenchSpec:
    script: str
    repeats: int = 7
    warmup: int = 2


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    category: str
    root: Path
    timeout_s: int = 120
    memory: str = "256m"
    cpus: str = "1"
    pids: int = 128
    candidates: tuple[Candidate, ...] = field(default_factory=tuple)
    bench: BenchSpec | None = None
    defect_pattern: str | None = None

    @property
    def repo_dir(self) -> Path:
        return self.root / "repo"

    @property
    def test_dirs(self) -> dict[str, Path]:
        return {"visible": self.root / "tests", "hidden": self.root / "hidden_tests"}

    @property
    def problem_path(self) -> Path:
        return self.root / "PROBLEM.md"

    @property
    def reference_patch(self) -> Path:
        return self.root / "reference" / "solution.patch"

    @property
    def expected_findings(self) -> Path:
        return self.root / "review" / "expected_findings.json"

    @property
    def reference_review(self) -> Path:
        return self.root / "reference" / "review.json"


def load_task(root: Path) -> Task:
    manifest = root / "task.toml"
    try:
        data = tomllib.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise TaskError(f"cannot read {manifest}: {exc}") from exc

    try:
        category = data["category"]
        if category not in CATEGORIES:
            raise TaskError(f"{manifest}: unknown category {category!r}")
        limits = data.get("limits", {})
        bench = data.get("bench")
        task = Task(
            id=data["id"],
            title=data["title"],
            category=category,
            root=root,
            timeout_s=int(limits.get("timeout_s", 120)),
            memory=str(limits.get("memory", "256m")),
            cpus=str(limits.get("cpus", "1")),
            pids=int(limits.get("pids", 128)),
            candidates=tuple(Candidate(**c) for c in data.get("candidates", [])),
            bench=BenchSpec(**bench) if bench else None,
            defect_pattern=data.get("scoring", {}).get("defect_pattern"),
        )
    except (KeyError, TypeError) as exc:
        raise TaskError(f"{manifest}: invalid manifest ({exc!r})") from exc

    for required in (task.repo_dir, task.problem_path, task.reference_patch):
        if not required.exists():
            raise TaskError(f"task {task.id}: missing {required.relative_to(root)}")
    if task.id != root.name:
        raise TaskError(f"task id {task.id!r} does not match directory {root.name!r}")
    return task


def discover(tasks_dir: Path) -> list[Task]:
    return [load_task(p.parent) for p in sorted(tasks_dir.glob("*/task.toml"))]


def find_task(tasks_dir: Path, task_id: str) -> Task:
    root = tasks_dir / task_id
    if not (root / "task.toml").exists():
        known = ", ".join(t.id for t in discover(tasks_dir)) or "none"
        raise TaskError(f"unknown task {task_id!r} (known: {known})")
    return load_task(root)
