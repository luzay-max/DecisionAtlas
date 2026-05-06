from __future__ import annotations

import ast
from pathlib import Path


def test_alembic_revision_ids_fit_default_version_table() -> None:
    versions_dir = Path(__file__).resolve().parents[2] / "alembic" / "versions"
    revision_ids: list[tuple[str, str]] = []
    for path in sorted(versions_dir.glob("*.py")):
        module = ast.parse(path.read_text(encoding="utf-8"))
        for node in module.body:
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(target, ast.Name) and target.id == "revision" for target in node.targets):
                continue
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                revision_ids.append((path.name, node.value.value))

    too_long = [(name, revision) for name, revision in revision_ids if len(revision) > 32]
    assert too_long == []
