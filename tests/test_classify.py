"""Regression tests for how container outcomes map to a status (no Docker needed)."""

import pytest

from codeforge.results import RunResult
from codeforge.runner import _classify
from codeforge.sandbox import ContainerRun

LIMITS = {"timeout_s": 60, "memory": "256m"}


def junit(failures: int = 0, tests: int = 2) -> str:
    cases = "".join(f'<testcase classname="v.t" name="t{i}" time="0.1"/>' for i in range(tests))
    cases += "".join(
        f'<testcase classname="v.t" name="f{i}" time="0.1"><failure message="x"/></testcase>'
        for i in range(failures)
    )
    return f"<testsuites><testsuite>{cases}</testsuite></testsuites>"


def classify(tmp_path, exit_code, xml=None, timed_out=False, oom=False):
    if xml is not None:
        (tmp_path / "junit.xml").write_text(xml)
    run = ContainerRun(exit_code, timed_out, oom, 1.0)
    return _classify(RunResult("t", "x", "infra_error", limits=LIMITS), run, tmp_path)


def test_clean_run_passes(tmp_path):
    assert classify(tmp_path, 0, junit()).status == "passed"


def test_failures_are_failed_tests(tmp_path):
    assert classify(tmp_path, 1, junit(failures=1)).status == "failed_tests"


@pytest.mark.parametrize("code", [1, 2, 3, 4, 137, 139, 153])
def test_nonzero_exit_with_clean_junit_is_never_passed(tmp_path, code):
    result = classify(tmp_path, code, junit())
    assert result.status == "infra_error"
    assert f"exited {code}" in result.detail


def test_failures_with_exit_zero_are_flagged_but_still_failed(tmp_path):
    result = classify(tmp_path, 0, junit(failures=1))
    assert result.status == "failed_tests" and "exited 0" in result.detail


def test_no_tests_collected(tmp_path):
    result = classify(tmp_path, 5, junit(tests=0))
    assert result.status == "infra_error" and "no tests" in result.detail


def test_missing_or_corrupt_junit_is_infra_error(tmp_path):
    assert classify(tmp_path, 0).status == "infra_error"
    assert classify(tmp_path, 0, "<not xml").status == "infra_error"


def test_timeout_oom_and_patch_failure_take_precedence(tmp_path):
    assert classify(tmp_path, 137, junit(), timed_out=True).status == "timeout"
    assert classify(tmp_path, 137, junit(), oom=True).status == "oom"
    assert classify(tmp_path, 10, junit()).status == "patch_rejected"
