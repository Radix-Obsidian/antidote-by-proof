"""Deterministic AST-based scanner using Tree-sitter. No LLM involved."""

import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from engine.rules.auth_decorator import (
    ROUTE_DECORATORS, AUTH_DECORATORS, RULE_NAME, SEVERITY,
)

PY_LANGUAGE = Language(tspython.language())


def scan_file(filepath: str) -> list[dict]:
    """Scan a Python file for ALL unprotected routes. Returns list of findings."""
    parser = Parser(PY_LANGUAGE)

    with open(filepath, "rb") as f:
        source = f.read()

    tree = parser.parse(source)
    findings = []

    for node in _walk(tree.root_node):
        if node.type == "decorated_definition":
            finding = _check_decorated(node, filepath)
            if finding:
                findings.append(finding)

    return findings


def _walk(node):
    """Recursively yield all nodes in the AST."""
    yield node
    for child in node.children:
        yield from _walk(child)


def _check_decorated(node, filepath: str) -> dict | None:
    """Check if a decorated_definition has a route but no auth decorator."""
    has_route = False
    has_auth = False
    func_node = None

    for child in node.children:
        if child.type == "decorator":
            text = child.text.decode("utf-8").lstrip("@").strip()
            base = text.split("(")[0].strip()

            if base in ROUTE_DECORATORS:
                has_route = True
            if base in AUTH_DECORATORS:
                has_auth = True

        if child.type == "function_definition":
            func_node = child

    if has_route and not has_auth and func_node:
        name_node = func_node.child_by_field_name("name")
        func_name = name_node.text.decode("utf-8") if name_node else "unknown"
        return {
            "file": filepath,
            "function": func_name,
            "line": func_node.start_point[0] + 1,
            "rule": RULE_NAME,
            "severity": SEVERITY,
        }

    return None
