import pytest

from codeforge.report import to_json, to_markdown
from codeforge.results import RunResult, TestOutcome, parse_junit, summarize_defects

JUNIT = """<?xml version="1.0"?>
<testsuites><testsuite name="pytest" tests="4">
<testcase classname="visible.test_a" name="test_ok" time="0.01"/>
<testcase classname="visible.test_a" name="test_defect_01_bad" time="0.02"><failure message="boom">tb</failure></testcase>
<testcase classname="hidden.test_b" name="test_defect_01_other" time="0.02"/>
<testcase classname="hidden.test_b" name="test_defect_02_err" time="0.02"><error message="oops"/></testcase>
<testcase classname="hidden.test_b" name="test_skipped" time="0"><skipped message="why"/></testcase>
</testsuite></testsuites>"""


@pytest.fixture
def outcomes(tmp_path):
    path = tmp_path / "junit.xml"
    path.write_text(JUNIT)
    return parse_junit(path)


def test_parse_junit_maps_outcomes(outcomes):
    assert [t.outcome for t in outcomes] == ["passed", "failed", "passed", "error", "skipped"]
    assert outcomes[1].message == "boom"


def test_defect_grouping_requires_every_test_of_a_defect_to_pass(outcomes):
    summary = summarize_defects(outcomes, r"test_defect_(\d+)")
    assert summary == {"total": 2, "resolved": 0, "unresolved": ["01", "02"]}


def test_oversized_junit_is_refused(tmp_path):
    path = tmp_path / "big.xml"
    path.write_bytes(b"<a>" + b"x" * (5 * 1024 * 1024) + b"</a>")
    with pytest.raises(ValueError):
        parse_junit(path)


def test_score_and_serialization(outcomes):
    result = RunResult("t", "run", "failed_tests", tests=outcomes)
    data = result.to_dict()
    assert data["summary"]["passed"] == 2 and data["summary"]["total"] == 5
    assert result.score == pytest.approx(0.4)
    assert RunResult("t", "x", "timeout").score == 0.0


def test_reports_render_every_status():
    results = [
        RunResult("t1", "ok", "passed", tests=[TestOutcome("a", "passed", 0.1)]),
        RunResult("t1", "bad", "patch_rejected", detail="protected file: conftest.py"),
        RunResult("t1", "slow", "timeout", output_tail="...", detail="exceeded 5s"),
    ]
    md = to_markdown(results)
    assert "patch_rejected" in md and "protected file" in md and "Output tail" in md
    assert '"status": "timeout"' in to_json(results)
