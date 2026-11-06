from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ENGINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_ROOT))

from app.main import create_app  # noqa: E402

OUTPUT = REPO_ROOT / "apps" / "api" / "src" / "contracts" / "engine-routes.generated.ts"
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def render_contract() -> str:
    schema = create_app().openapi()
    routes: list[str] = []
    for path, operations in sorted(schema.get("paths", {}).items()):
        for method in sorted(operations):
            if method in HTTP_METHODS:
                routes.append(f'  | "{method.upper()} {path}"')
    if not routes:
        raise RuntimeError("Engine OpenAPI contains no HTTP operations")
    return "\n".join([
        "// Generated from FastAPI app.openapi() by services/engine/scripts/export_openapi_route_contract.py.",
        "// Do not edit by hand; run the generator after changing Engine routes.",
        "export type EngineRoute =",
        *routes,
        ";",
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the Engine OpenAPI path/method TypeScript contract.")
    parser.add_argument("--check", action="store_true", help="Fail if the committed TypeScript contract is stale.")
    args = parser.parse_args()
    generated = render_contract()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != generated:
            print(f"{OUTPUT.relative_to(REPO_ROOT)} is stale; regenerate it with this script.", file=sys.stderr)
            return 1
        print("Engine OpenAPI route contract is up to date.")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(generated, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
