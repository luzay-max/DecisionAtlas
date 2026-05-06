from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENGINE_ROOT = ROOT / "services" / "engine"
sys.path.insert(0, str(ENGINE_ROOT))

from app.governance.diff_checker import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
