import { spawnSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import openapiTS, { astToString } from "openapi-typescript";

const root = fileURLToPath(new URL("../../../", import.meta.url));
const result = spawnSync("uv", [
  "run", "--frozen", "--project", "services/engine", "python",
  "services/engine/scripts/export_openapi_route_contract.py", "--schema-json",
], { cwd: root, encoding: "utf8", maxBuffer: 8 * 1024 * 1024 });
if (result.error || result.status !== 0) {
  throw result.error ?? new Error(result.stderr || "OpenAPI export failed");
}
const schema = JSON.parse(result.stdout);
const ast = await openapiTS(schema, { defaultNonNullable: false });
const outputs = [
  [new URL("../openapi.generated.json", import.meta.url), JSON.stringify(schema, null, 2) + "\n"],
  [new URL("../src/openapi.generated.d.ts", import.meta.url),
    "// Generated from Engine OpenAPI. Run pnpm contract:generate; do not edit.\n" + astToString(ast)],
];
let stale = false;
for (const [path, content] of outputs) {
  if (process.argv.includes("--check")) {
    let current;
    try { current = readFileSync(path, "utf8").replace(/\r\n/g, "\n"); } catch { current = undefined; }
    if (current !== content) {
      console.error(`${fileURLToPath(path)} is stale; run pnpm contract:generate`);
      stale = true;
    }
  } else {
    writeFileSync(path, content);
  }
}
if (stale) process.exitCode = 1;
else console.log("Engine OpenAPI schema and TypeScript DTOs are up to date.");
