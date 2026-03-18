from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class PandocAdapter:
    def is_available(self) -> bool:
        return shutil.which("pandoc") is not None

    def convert_to_markdown(self, path: Path) -> str | None:
        if not self.is_available():
            return None
        result = subprocess.run(
            ["pandoc", str(path), "-t", "gfm"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout
