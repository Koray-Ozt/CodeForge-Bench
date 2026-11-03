"""Docker invocation for untrusted candidate code."""

from __future__ import annotations

import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

IMAGE = "codeforge-runner:1"
TMPFS_WORK_MB = 64
TMPFS_TMP_MB = 32
MAX_OUTPUT_TAIL = 4000


class SandboxError(Exception):
    pass


@dataclass(frozen=True)
class Limits:
    memory: str = "256m"
    cpus: str = "1"
    pids: int = 128
    timeout_s: int = 120

    def as_dict(self) -> dict[str, object]:
        return {
            "memory": self.memory,
            "cpus": self.cpus,
            "pids": self.pids,
            "timeout_s": self.timeout_s,
            "network": "none",
        }


@dataclass
class ContainerRun:
    exit_code: int | None
    timed_out: bool
    oom: bool
    duration_s: float


def _docker(*args: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["docker", *args], capture_output=True, text=True, timeout=timeout, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SandboxError(f"docker {args[0]} failed: {exc}") from exc


def image_id() -> str:
    proc = _docker("image", "inspect", "--format", "{{.Id}}", IMAGE)
    if proc.returncode != 0:
        raise SandboxError(f"image {IMAGE} not found; build it with `codeforge build-image`")
    return proc.stdout.strip()


def build_image(repo_root: Path) -> None:
    docker_dir = repo_root / "docker"
    proc = subprocess.run(
        [
            "docker",
            "build",
            "-t",
            IMAGE,
            "-f",
            str(docker_dir / "Dockerfile.runner"),
            str(docker_dir),
        ],
        check=False,
    )
    if proc.returncode != 0:
        raise SandboxError("docker build failed")


def run_container(
    mode_args: list[str], in_dir: Path, out_dir: Path, limits: Limits
) -> ContainerRun:
    """Run the entrypoint with strict resource limits and no network."""
    name = f"cf-{uuid.uuid4().hex[:12]}"
    cmd = [
        "docker", "run",
        "--name", name,
        "--network", "none",
        "--memory", limits.memory,
        "--memory-swap", limits.memory,
        "--cpus", limits.cpus,
        "--pids-limit", str(limits.pids),
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--read-only",
        "--tmpfs", f"/work:rw,size={TMPFS_WORK_MB}m,uid=1000,gid=1000,mode=755",
        "--tmpfs", f"/tmp:rw,size={TMPFS_TMP_MB}m,uid=1000,gid=1000,mode=1777",
        "-v", f"{in_dir}:/in:ro",
        "-v", f"{out_dir}:/out:rw",
        "--user", "1000:1000",
        IMAGE, *mode_args,
    ]  # fmt: skip
    start = time.monotonic()
    timed_out = False
    exit_code: int | None = None
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=limits.timeout_s, check=False
        )
        exit_code = proc.returncode
        if exit_code == 125:  # docker daemon error, not the workload
            raise SandboxError(f"docker run failed: {proc.stderr.strip()[:500]}")
    except subprocess.TimeoutExpired:
        timed_out = True
        _docker("kill", name)
    duration = time.monotonic() - start
    try:
        inspect = _docker("inspect", "--format", "{{.State.OOMKilled}}", name)
        oom = inspect.stdout.strip() == "true"
    finally:
        _docker("rm", "-f", name)
    return ContainerRun(exit_code, timed_out, oom, duration)


def tail(path: Path, limit: int = MAX_OUTPUT_TAIL) -> str:
    try:
        data = path.read_bytes()[-limit:]
    except OSError:
        return ""
    return data.decode("utf-8", errors="replace")
