"""Test enforcing the Cardinal Constraint: Zero Forbidden Imports in core/engine/.

Scans all Python files in core/engine/ via Abstract Syntax Tree (AST) analysis
and verifies that no standard library collection utilities or external graph/collection libraries
(collections, heapq, bisect, networkx, queue, array, sortedcontainers, etc.) are imported.
"""

import ast
from pathlib import Path

# Absolute set of forbidden modules inside core/engine/
FORBIDDEN_MODULES = {
    "collections",
    "heapq",
    "bisect",
    "networkx",
    "queue",
    "array",
    "sortedcontainers",
    "scipy",
    "numpy",
    "pandas",
    "igraph",
}


def find_forbidden_imports(file_path: Path) -> list[tuple[int, str]]:
    """Parse a Python file with AST and return (line_number, imported_module) for any forbidden import."""
    with open(file_path, encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=str(file_path))
    violations: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_pkg = alias.name.split(".")[0]
                if root_pkg in FORBIDDEN_MODULES:
                    violations.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_pkg = node.module.split(".")[0]
                if root_pkg in FORBIDDEN_MODULES:
                    violations.append((node.lineno, node.module))

    return violations


def test_core_engine_has_zero_forbidden_imports():
    """Assert that core/engine/ has strictly zero imports from forbidden collection/graph libraries."""
    engine_dir = Path(__file__).resolve().parent.parent.parent / "core" / "engine"
    assert engine_dir.exists(), f"Engine directory does not exist: {engine_dir}"

    all_py_files = list(engine_dir.rglob("*.py"))
    assert len(all_py_files) >= 15, f"Expected at least 15 engine files, found {len(all_py_files)}"

    all_violations: list[str] = []

    for py_file in all_py_files:
        violations = find_forbidden_imports(py_file)
        for lineno, mod in violations:
            all_violations.append(f"{py_file.name}:{lineno} -> imported forbidden module '{mod}'")

    assert not all_violations, (
        f"CARDINAL CONSTRAINT VIOLATION: Found {len(all_violations)} forbidden imports in core/engine/:\n"
        + "\n".join(all_violations)
    )


def test_import_scanner_detects_violations():
    """Verify that the AST scanner genuinely catches forbidden imports and does not produce false negatives."""
    dummy_bad_code = """
import collections
from heapq import heappush, heappop
from bisect import bisect_left
import networkx as nx
import math
"""
    tree = ast.parse(dummy_bad_code)
    detected = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in FORBIDDEN_MODULES:
                    detected.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in FORBIDDEN_MODULES:
                detected.append(node.module)

    assert "collections" in detected
    assert "heapq" in detected
    assert "bisect" in detected
    assert "networkx" in detected
    assert "math" not in detected
