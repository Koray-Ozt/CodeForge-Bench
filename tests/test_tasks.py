"""Static invariants every task must satisfy (no Docker needed)."""

import pytest

from codeforge.cli import TASKS_DIR
from codeforge.patching import validate_patch
from codeforge.task import CATEGORIES, discover

TASKS = discover(TASKS_DIR)


def test_the_five_expected_categories_are_covered():
    assert {t.category for t in TASKS} == CATEGORIES
    assert len(TASKS) == 5


@pytest.mark.parametrize("task", TASKS, ids=lambda t: t.id)
def test_task_is_complete(task):
    assert task.problem_path.read_text(encoding="utf-8").strip()
    assert (task.root / "reference" / "EXPLANATION.md").exists()
    assert task.test_dirs["visible"].is_dir() and task.test_dirs["hidden"].is_dir()
    assert task.candidates, "each task ships at least one plausible-but-wrong patch"
    if task.bench:
        assert (task.root / "bench" / task.bench.script).exists()


@pytest.mark.parametrize("task", TASKS, ids=lambda t: t.id)
def test_every_shipped_patch_passes_static_validation(task):
    patches = [task.reference_patch, *(task.root / c.patch for c in task.candidates)]
    for patch in patches:
        assert validate_patch(patch.read_bytes()) == [], patch


@pytest.mark.parametrize("task", TASKS, ids=lambda t: t.id)
def test_patches_use_lf_line_endings(task):
    assert b"\r\n" not in task.reference_patch.read_bytes()
