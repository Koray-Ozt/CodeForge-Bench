"""Integration tests that run hostile patches in the real sandbox (need Docker).

Each patch appends code to a task's `__init__.py`, so it runs at import time inside the
container. A probe that finds the sandbox too permissive raises, which fails the task's
tests, so `status == "passed"` means the restriction held.
"""

import dataclasses
import difflib
import shutil
import subprocess

import pytest

from codeforge import runner, sandbox
from codeforge.cli import TASKS_DIR
from codeforge.task import find_task

TASK = find_task(TASKS_DIR, "t01_inventory_race")
TARGET = "inventory/__init__.py"


def docker_ready() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        sandbox.image_id()
        return subprocess.run(["docker", "info"], capture_output=True, timeout=20).returncode == 0
    except (sandbox.SandboxError, subprocess.TimeoutExpired):
        return False


pytestmark = [
    pytest.mark.docker,
    pytest.mark.skipif(not docker_ready(), reason="Docker or the runner image is unavailable"),
]


def hostile_patch(tmp_path, code: str):
    """Reference solution plus a payload appended to TARGET, as one patch against baseline."""
    base, work = tmp_path / "base", tmp_path / "work"
    shutil.copytree(TASK.repo_dir, base, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(base, work)
    subprocess.run(
        ["git", "apply", str(TASK.reference_patch)], cwd=work, check=True, capture_output=True
    )
    target = work / TARGET
    target.write_text(
        target.read_text(encoding="utf-8") + "\n" + code.strip() + "\n",
        encoding="utf-8",
        newline="\n",
    )

    chunks = []
    for path in sorted(work.rglob("*.py")):
        rel = path.relative_to(work).as_posix()
        before = (base / rel).read_text(encoding="utf-8").splitlines(keepends=True)
        after = path.read_text(encoding="utf-8").splitlines(keepends=True)
        chunks += difflib.unified_diff(before, after, f"a/{rel}", f"b/{rel}")
    patch = tmp_path / "hostile.patch"
    patch.write_text("".join(chunks), encoding="utf-8", newline="\n")
    return patch


def run(tmp_path, code: str, task=TASK):
    return runner.evaluate(task, hostile_patch(tmp_path, code), "hostile")


def test_reference_solution_still_passes(tmp_path):
    assert runner.evaluate(TASK, TASK.reference_patch, "reference").status == "passed"


def test_network_is_unreachable(tmp_path):
    code = """
import socket
try:
    socket.create_connection(("1.1.1.1", 53), timeout=3).close()
except OSError:
    pass
else:
    raise RuntimeError("NETWORK REACHABLE")
"""
    assert run(tmp_path, code).status == "passed"


def test_root_filesystem_is_read_only_and_user_is_unprivileged(tmp_path):
    code = """
import os
if os.getuid() == 0:
    raise RuntimeError("RUNNING AS ROOT")
try:
    open("/etc/cf_probe", "w").close()
except OSError:
    pass
else:
    raise RuntimeError("ROOTFS WRITABLE")
"""
    assert run(tmp_path, code).status == "passed"


def test_host_filesystem_is_not_visible(tmp_path):
    code = """
import os
for path in ("/mnt/c", "/Users", "/host_mnt", "/var/run/docker.sock"):
    if os.path.exists(path):
        raise RuntimeError("HOST PATH VISIBLE: " + path)
"""
    assert run(tmp_path, code).status == "passed"


def test_process_count_is_limited(tmp_path):
    code = """
import os, signal, time
children = []
try:
    for _ in range(400):
        pid = os.fork()
        if pid == 0:
            time.sleep(20)
            os._exit(0)
        children.append(pid)
    limited = False
except OSError:
    limited = True
finally:
    for pid in children:
        try:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)  # reap, or zombies keep counting against the pids limit
        except OSError:
            pass
if not limited:
    raise RuntimeError("PIDS NOT LIMITED (forked %d)" % len(children))
"""
    assert run(tmp_path, code).status == "passed"


def test_memory_bomb_is_killed(tmp_path):
    result = run(tmp_path, "x = bytearray(2 * 1024**3)\nx[::4096] = b'a' * len(x[::4096])")
    assert result.status in {"oom", "failed_tests", "infra_error"}
    assert result.status != "passed"


def test_infinite_loop_times_out(tmp_path):
    short = dataclasses.replace(TASK, timeout_s=5)
    result = run(tmp_path, "while True:\n    pass", task=short)
    assert result.status == "timeout"


def test_output_flood_is_bounded(tmp_path):
    result = run(
        tmp_path, "import sys\nfor _ in range(200000):\n    sys.stderr.write('x' * 500 + '\\n')"
    )
    assert len(result.output_tail) <= sandbox.MAX_OUTPUT_TAIL
