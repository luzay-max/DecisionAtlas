from __future__ import annotations

from pathlib import Path


def load_prompt(name: str) -> str:
    prompt_path = Path(__file__).resolve().parents[4] / "packages" / "prompts" / f"{name}.md"
    return prompt_path.read_text(encoding="utf-8")
