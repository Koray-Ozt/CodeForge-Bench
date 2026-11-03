"""Stage a task, run it in the sandbox, and classify the outcome."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from . import patching, sandbox
from .results import RunResult, parse_junit, summarize_defects
from .task import Task

_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", ".ruff_cache")
PATCH_APPLY_FAILED = 10


def _make_readable(root: Path) -> None:
    """The container user has a different uid than the host user."""
    for dirpath, dirnames, filenames in os.walk(root):
        os.chmod(dirpath, 0o755)
        for name in filenames:
            os.chmod(Path(dirpath) / name, 0o644)
        for name in dirnames:
            os.chmod(Path(dirpath) / name, 0o755)


@contextmanager
def _staging(task: Task, patch: bytes | None, with_bench: bool) -> Iterator[tuple[Path, Path]]:
    """Yield (in_dir, out_dir): isolated copies, nothing shared with the task tree."""
    with tempfile.TemporaryDirectory(prefix="codeforge-") as tmp:
        base = Path(tmp)
        in_dir, out_dir = base / "in", base / "out"
        shutil.copytree(task.repo_dir, in_dir / "repo", ignore=_IGNORE)
        for label, src in task.test_dirs.items():
            if src.is_dir():
                shutil.copytree(src, in_dir / "tests" / label, ignore=_IGNORE)
        if with_bench and task.bench:
            bench_src = task.root / "bench"
            shutil.copytree(bench_src, in_dir / "bench", ignore=_IGNORE)
        if patch is not None:
            (in_dir / "candidate.patch").write_bytes(patch)
        out_dir.mkdir()
        _make_readable(in_dir)
        os.chmod(out_dir, 0o777)
        yield in_dir, out_dir


def _limits(task: Task) -> sandbox.Limits:
    return sandbox.Limits(task.memory, task.cpus, task.pids, task.timeout_s)


def evaluate(task: Task, patch_path: Path | None, label: str) -> RunResult:
    """Run the task's tests against the repo with an optional candidate patch applied."""
    limits = _limits(task)
    result = RunResult(task.id, label, "infra_error", limits=limits.as_dict())
    patch = patch_path.read_bytes() if patch_path else None

    if patch is not None:
        result.patch_sha256 = hashlib.sha256(patch).hexdigest()
        if problems := patching.validate_patch(patch):
            result.status = "patch_rejected"
            result.detail = "; ".join(problems)
            return result

    try:
        result.image_id = sandbox.image_id()
        with _staging(task, patch, with_bench=False) as (in_dir, out_dir):
            run = sandbox.run_container(["test"], in_dir, out_dir, limits)
            result.exit_code = run.exit_code
            result.duration_s = round(run.duration_s, 3)
            result.output_tail = sandbox.tail(out_dir / "output.log")
            return _classify(result, run, out_dir, task.defect_pattern)
    except sandbox.SandboxError as exc:
        result.detail = str(exc)
        return result


def _classify(
    result: RunResult, run: sandbox.ContainerRun, out_dir: Path, defect_pattern: str | None = None
) -> RunResult:
    if run.timed_out:
        result.status, result.detail = "timeout", f"exceeded {result.limits['timeout_s']}s"
    elif run.oom:
        result.status, result.detail = "oom", f"exceeded {result.limits['memory']} memory"
    elif run.exit_code == PATCH_APPLY_FAILED:
        result.status = "patch_rejected"
        result.detail = "git apply failed: " + sandbox.tail(out_dir / "patch.log", 800).strip()
    else:
        junit = out_dir / "junit.xml"
        try:
            result.tests = parse_junit(junit)
        except (OSError, ValueError, ET.ParseError) as exc:
            result.detail = f"no usable junit.xml (exit {run.exit_code}): {exc}"
            return result
        if defect_pattern:
            result.defects = summarize_defects(result.tests, defect_pattern)
        bad = result.count("failed") + result.count("error")
        if not result.tests:
            result.detail = "no tests were collected"
        elif bad:
            result.status = "failed_tests"
            if run.exit_code == 0:
                result.detail = "junit.xml reports failures but pytest exited 0"
        elif run.exit_code != 0:
            # A clean junit.xml is not enough: pytest crashed, was killed, or the report
            # is stale or forged. Never report "passed" without a zero exit code.
            result.detail = f"pytest exited {run.exit_code} although junit.xml shows no failures"
        else:
            result.status = "passed"
    return result


def run_bench(task: Task, patch_path: Path | None, label: str) -> dict:
    """Run the task's benchmark script in the sandbox and return its JSON."""
    if not task.bench:
        raise sandbox.SandboxError(f"task {task.id} defines no benchmark")
    limits = _limits(task)
    patch = patch_path.read_bytes() if patch_path else None
    if patch is not None and (problems := patching.validate_patch(patch)):
        raise sandbox.SandboxError("patch rejected: " + "; ".join(problems))
    image = sandbox.image_id()
    with _staging(task, patch, with_bench=True) as (in_dir, out_dir):
        run = sandbox.run_container(["bench", task.bench.script], in_dir, out_dir, limits)
        if run.timed_out or run.oom or run.exit_code != 0:
            tail = sandbox.tail(out_dir / "output.log", 800)
            raise sandbox.SandboxError(
                f"benchmark {label} failed (exit {run.exit_code}, timeout={run.timed_out}, "
                f"oom={run.oom}): {tail}"
            )
        data = json.loads((out_dir / "bench.json").read_text(encoding="utf-8"))
    data["label"] = label
    data["image_id"] = image
    return data
