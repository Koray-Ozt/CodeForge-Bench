"""Command line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import report, review, runner, sandbox, verify
from .bench import summarize
from .task import Task, TaskError, discover, find_task

REPO_ROOT = Path(__file__).resolve().parents[2]
TASKS_DIR = REPO_ROOT / "tasks"


def _select(args: argparse.Namespace) -> list[Task]:
    if getattr(args, "all", False):
        return discover(TASKS_DIR)
    return [find_task(TASKS_DIR, args.task)]


def cmd_list(_: argparse.Namespace) -> int:
    for t in discover(TASKS_DIR):
        print(f"{t.id:28} {t.category:16} {t.title}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    task = find_task(TASKS_DIR, args.task)
    print(task.problem_path.read_text(encoding="utf-8"))
    return 0


def cmd_build_image(_: argparse.Namespace) -> int:
    sandbox.build_image(REPO_ROOT)
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    task = find_task(TASKS_DIR, args.task)
    patch = Path(args.patch) if args.patch else None
    result = runner.evaluate(task, patch, args.label or (patch.name if patch else "baseline"))
    out = Path(args.out)
    json_path, md_path = report.write_reports([result], out, f"{task.id}")
    print(f"{task.id}: {result.status} ({result.count('passed')}/{len(result.tests)} passed)")
    print(f"reports: {json_path} {md_path}")
    return 0 if result.status == "passed" else 1


def cmd_verify(args: argparse.Namespace) -> int:
    all_results, failed = [], False
    for task in _select(args):
        print(f"== {task.id}")
        for check in verify.verify_task(task):
            mark = "ok  " if check.ok else "FAIL"
            print(f"  [{mark}] {check.label}: {check.why}")
            if check.result:
                all_results.append(check.result)
            failed |= not check.ok
    if args.out:
        report.write_reports(all_results, Path(args.out), "verify")
    return 1 if failed else 0


def cmd_grade_review(args: argparse.Namespace) -> int:
    task = find_task(TASKS_DIR, args.task)
    expected = review.load_expected(task.expected_findings)
    submitted = review.load_submission(Path(args.review))
    graded = review.grade(task.id, expected, submitted)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(graded.to_dict(), indent=2) + "\n"
    (out / f"{task.id}_review.json").write_text(payload, encoding="utf-8")
    text = review.to_markdown(graded, expected)
    (out / f"{task.id}_review.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


def cmd_bench(args: argparse.Namespace) -> int:
    task = find_task(TASKS_DIR, args.task)
    runs = [
        runner.run_bench(task, None, "baseline"),
        runner.run_bench(task, task.reference_patch, "reference"),
    ]
    text = summarize(task.id, runs)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{task.id}_bench.json").write_text(json.dumps(runs, indent=2) + "\n", encoding="utf-8")
    (out / f"{task.id}_bench.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="codeforge", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list tasks").set_defaults(fn=cmd_list)
    sub.add_parser("build-image", help="build the sandbox image").set_defaults(fn=cmd_build_image)

    s = sub.add_parser("show", help="print a task's problem statement")
    s.add_argument("task")
    s.set_defaults(fn=cmd_show)

    s = sub.add_parser("run", help="evaluate a candidate patch")
    s.add_argument("task")
    s.add_argument("--patch", help="unified diff relative to the task's repo/ (omit for baseline)")
    s.add_argument("--label")
    s.add_argument("--out", default="runs")
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("verify", help="check baseline fails and reference passes")
    s.add_argument("task", nargs="?")
    s.add_argument("--all", action="store_true")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_verify)

    s = sub.add_parser("grade-review", help="score a review.json against known defects")
    s.add_argument("task")
    s.add_argument("review", help="path to the candidate's review.json")
    s.add_argument("--out", default="runs")
    s.set_defaults(fn=cmd_grade_review)

    s = sub.add_parser("bench", help="before/after measurements for performance tasks")
    s.add_argument("task")
    s.add_argument("--out", default="results")
    s.set_defaults(fn=cmd_bench)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "verify" and not (args.all or args.task):
        print("verify needs a task id or --all", file=sys.stderr)
        return 2
    try:
        return args.fn(args)
    except (TaskError, sandbox.SandboxError, review.ReviewError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
