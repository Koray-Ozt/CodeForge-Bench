"""JSON and Markdown report rendering."""

from __future__ import annotations

import json
import platform
from datetime import UTC, datetime
from pathlib import Path

from . import __version__
from .results import RunResult


def environment() -> dict[str, str]:
    return {
        "codeforge": __version__,
        "python": platform.python_version(),
        "host_os": platform.platform(),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }


def to_json(results: list[RunResult]) -> str:
    payload = {"environment": environment(), "results": [r.to_dict() for r in results]}
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def to_markdown(results: list[RunResult]) -> str:
    env = environment()
    lines = [
        "# CodeForge Bench report",
        "",
        f"Generated {env['generated_at']} on `{env['host_os']}` (codeforge {env['codeforge']}).",
        "",
        "| Task | Run | Status | Passed | Failed | Error | Score | Time (s) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.task_id} | {r.label} | **{r.status}** | {r.count('passed')} | "
            f"{r.count('failed')} | {r.count('error')} | {r.score:.2f} | {r.duration_s:.1f} |"
        )
    for r in results:
        lines += ["", f"## {r.task_id} / {r.label}", ""]
        if r.detail:
            lines += [f"- Detail: {r.detail}"]
        lines += [
            f"- Limits: `{json.dumps(r.limits)}`",
            f"- Image: `{r.image_id or 'n/a'}`",
        ]
        if r.defects:
            d = r.defects
            lines.append(
                f"- Defects resolved: {d['resolved']}/{d['total']}"
                + (f" (unresolved: {', '.join(d['unresolved'])})" if d["unresolved"] else "")
            )
        if r.patch_sha256:
            lines.append(f"- Patch sha256: `{r.patch_sha256}`")
        bad = [t for t in r.tests if t.outcome in ("failed", "error")]
        if bad:
            lines += ["", "Failing tests:", ""]
            for t in bad:
                first_line = t.message.splitlines()[0] if t.message else ""
                lines.append(f"- `{t.name}` ({t.outcome}): {first_line}")
        if r.status in ("infra_error", "timeout", "oom") and r.output_tail:
            lines += ["", "Output tail:", "", "```", r.output_tail.rstrip(), "```"]
    return "\n".join(lines) + "\n"


def write_reports(
    results: list[RunResult], out_dir: Path, stem: str = "report"
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path, md_path = out_dir / f"{stem}.json", out_dir / f"{stem}.md"
    json_path.write_text(to_json(results), encoding="utf-8")
    md_path.write_text(to_markdown(results), encoding="utf-8")
    return json_path, md_path
