"""Static checks on untrusted patches, run on the host before anything touches Docker.

The patch is never applied on the host: `git apply` runs inside the sandbox. These
checks only reject patches that try to escape the repo, tamper with test
infrastructure, or are too large to review.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath

MAX_PATCH_BYTES = 256 * 1024

# Files that would change how pytest or Python start up inside the sandbox.
PROTECTED_NAMES = {
    "conftest.py",
    "sitecustomize.py",
    "usercustomize.py",
    "pytest.ini",
    "tox.ini",
    "setup.cfg",
    "pyproject.toml",
}
PROTECTED_DIRS = {"tests", "hidden_tests", ".git"}

_DIFF_GIT = re.compile(r"^diff --git (?P<a>\S+) (?P<b>\S+)$")
_FILE_LINE = re.compile(r"^(?:---|\+\+\+) (?P<path>\S+)")
_RENAME = re.compile(r"^(?:rename|copy) (?:from|to) (?P<path>.+)$")


def _path_problem(raw: str) -> str | None:
    if raw == "/dev/null":
        return None
    if raw.startswith('"'):
        return f"quoted path not allowed: {raw}"
    path = raw
    if path.startswith(("a/", "b/")):
        path = path[2:]
    if "\\" in path or "\0" in path:
        return f"suspicious characters in path: {raw!r}"
    posix = PurePosixPath(path)
    if posix.is_absolute() or ".." in posix.parts:
        return f"path escapes repository: {raw}"
    if posix.name in PROTECTED_NAMES or posix.name.endswith(".pth"):
        return f"protected file: {raw}"
    if posix.parts and posix.parts[0] in PROTECTED_DIRS:
        return f"protected directory: {raw}"
    return None


def validate_patch(data: bytes) -> list[str]:
    """Return a list of violations; an empty list means the patch may proceed."""
    if not data.strip():
        return ["patch is empty"]
    if len(data) > MAX_PATCH_BYTES:
        return [f"patch larger than {MAX_PATCH_BYTES} bytes"]
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return ["patch is not valid UTF-8"]

    problems: list[str] = []
    for line in text.splitlines():
        if line.startswith(("new file mode 120000", "old mode 120000", "new mode 120000")):
            problems.append("symlinks are not allowed")
        elif line.startswith(("GIT binary patch", "Binary files")):
            problems.append("binary patches are not allowed")
        elif m := _DIFF_GIT.match(line):
            problems += [p for g in ("a", "b") if (p := _path_problem(m[g]))]
        elif ((m := _FILE_LINE.match(line)) or (m := _RENAME.match(line))) and (
            p := _path_problem(m["path"])
        ):
            problems.append(p)
    # Deduplicate, keep order.
    return list(dict.fromkeys(problems))
