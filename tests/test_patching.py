import pytest

from codeforge.patching import MAX_PATCH_BYTES, validate_patch

GOOD = b"""diff --git a/pkg/mod.py b/pkg/mod.py
--- a/pkg/mod.py
+++ b/pkg/mod.py
@@ -1 +1 @@
-x = 1
+x = 2
"""


def test_plain_patch_is_accepted():
    assert validate_patch(GOOD) == []


@pytest.mark.parametrize(
    "path",
    [
        "../outside.py",
        "pkg/../../outside.py",
        "/etc/passwd",
        "tests/test_x.py",
        "hidden_tests/test_x.py",
        "pkg/conftest.py",
        "sitecustomize.py",
        "pytest.ini",
        "pyproject.toml",
        "evil.pth",
        ".git/hooks/pre-commit",
        "back\\slash.py",
    ],
)
def test_dangerous_paths_are_rejected(path):
    patch = GOOD.replace(b"pkg/mod.py", path.encode())
    assert validate_patch(patch), path


def test_symlink_and_binary_patches_are_rejected():
    link = (
        b"diff --git a/l b/l\nnew file mode 120000\n--- /dev/null\n+++ b/l\n@@ -0,0 +1 @@\n+/etc\n"
    )
    assert any("symlink" in p for p in validate_patch(link))
    binary = b"diff --git a/x.bin b/x.bin\nGIT binary patch\nliteral 0\n"
    assert any("binary" in p for p in validate_patch(binary))


def test_rename_targets_are_checked():
    patch = b"diff --git a/a.py b/b.py\nrename from a.py\nrename to ../b.py\n"
    assert validate_patch(patch)


def test_empty_oversized_and_non_utf8_patches_are_rejected():
    assert validate_patch(b"  \n")
    assert validate_patch(b"x" * (MAX_PATCH_BYTES + 1))
    assert validate_patch(b"\xff\xfe\x00")


def test_new_files_from_dev_null_are_allowed():
    patch = b"--- /dev/null\n+++ b/pkg/new.py\n@@ -0,0 +1 @@\n+x = 1\n"
    assert validate_patch(patch) == []
