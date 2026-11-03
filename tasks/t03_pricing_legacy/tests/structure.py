"""Small AST-based maintainability metrics (no third-party tools needed)."""

import ast
from dataclasses import dataclass
from pathlib import Path

FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
BRANCHES = (
    ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.IfExp, ast.match_case,
)  # fmt: skip


@dataclass(frozen=True)
class FunctionMetrics:
    where: str
    complexity: int
    lines: int


def _own_nodes(fn):
    """Walk a function body without descending into nested function definitions."""
    stack = list(ast.iter_child_nodes(fn))
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, (*FUNCTIONS, ast.Lambda)):
            stack.extend(ast.iter_child_nodes(node))


def cyclomatic(fn) -> int:
    score = 1
    for node in _own_nodes(fn):
        if isinstance(node, BRANCHES):
            score += 1
        elif isinstance(node, ast.BoolOp):
            score += len(node.values) - 1
        elif isinstance(node, ast.comprehension):
            score += 1 + len(node.ifs)
    return score


def measure(package_dir: Path) -> list[FunctionMetrics]:
    metrics = []
    for path in sorted(package_dir.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, FUNCTIONS):
                lines = node.end_lineno - node.lineno + 1
                metrics.append(FunctionMetrics(f"{path.name}:{node.name}", cyclomatic(node), lines))
    return metrics
