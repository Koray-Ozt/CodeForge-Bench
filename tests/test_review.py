import json

import pytest

from codeforge.review import Expected, ReviewError, Submitted, grade, load_submission

EXPECTED = [
    Expected("D1", "a.py", 10, 10, "security", "one"),
    Expected("D2", "a.py", 11, 12, "security", "two"),
    Expected("D3", "b.py", 5, 5, "state", "three", alt_lines=(40,)),
]


def sub(file, line, category="security"):
    return Submitted(file, line, category, "")


def test_perfect_review():
    g = grade("t", EXPECTED, [sub("a.py", 10), sub("a.py", 12), sub("b.py", 5, "state")])
    assert (g.recall, g.precision, g.f1) == (1.0, 1.0, 1.0)


def test_adjacent_defects_need_separate_findings():
    g = grade("t", EXPECTED, [sub("a.py", 11)])
    assert len(g.matched) == 1 and set(g.missed) == {
        "D1" if g.matched[0]["expected"] != "D1" else "D2",
        "D3",
    }


def test_wrong_file_or_far_line_is_a_false_positive():
    g = grade("t", EXPECTED, [sub("c.py", 10), sub("a.py", 50)])
    assert g.matched == [] and g.false_positives == [0, 1] and g.precision == 0.0


def test_alt_lines_and_tolerance():
    assert grade("t", EXPECTED, [sub("b.py", 41, "state")]).recall == pytest.approx(1 / 3)
    assert grade("t", EXPECTED, [sub("b.py", 43, "state")]).recall == 0.0


def test_category_mismatch_still_matches_but_is_reported():
    g = grade("t", EXPECTED, [sub("a.py", 10, "style")])
    assert len(g.matched) == 1 and g.category_accuracy == 0.0


def test_matching_is_one_to_one():
    g = grade("t", EXPECTED, [sub("a.py", 10), sub("a.py", 10), sub("a.py", 10)])
    assert len(g.matched) == 2 and g.false_positives == [2]


def test_windows_style_paths_are_normalized(tmp_path):
    path = tmp_path / "r.json"
    path.write_text(json.dumps({"findings": [{"file": ".\\a.py", "line": 10}]}))
    assert load_submission(path)[0].file == "a.py"


@pytest.mark.parametrize(
    "payload",
    ['{"findings": "x"}', '{"findings": [1]}', '{"findings": [{"file": "a.py"}]}',
     '{"findings": [{"file": "a.py", "line": true}]}', "not json", '{"nope": []}'],
)  # fmt: skip
def test_malformed_submissions_are_rejected(tmp_path, payload):
    path = tmp_path / "r.json"
    path.write_text(payload)
    with pytest.raises(ReviewError):
        load_submission(path)
