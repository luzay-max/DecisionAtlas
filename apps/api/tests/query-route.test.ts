import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { buildServer } from "../src/server";

const fixture = JSON.parse(readFileSync(resolve(__dirname, "../../../packages/engine-contract/fixtures/why-ok.json"), "utf8"));

describe("POST /query/why generated DTO client", () => {
  const originalFetch = global.fetch;
  afterEach(() => { global.fetch = originalFetch; });

  it("preserves the exact Engine-validated response including nullable URLs and chunk citations", async () => {
    global.fetch = vi.fn().mockResolvedValue(Response.json(fixture));
    const app = buildServer();
    try {
      const response = await app.inject({ method: "POST", url: "/query/why",
        payload: { workspace_slug: "synthetic", question: fixture.question } });
      expect(response.statusCode).toBe(200);
      expect(response.json()).toEqual(fixture);
      const upstream = vi.mocked(global.fetch).mock.calls[0][0] as Request;
      expect(upstream.url).toBe("http://localhost:8000/query/why");
      expect(upstream.method).toBe("POST");
      expect(await upstream.json()).toEqual({ workspace_slug: "synthetic", question: fixture.question });
    } finally { await app.close(); }
  });

  it.each([401, 403, 404, 422, 502, 503])("retains status %s and the existing Engine error envelope", async (status) => {
    const error = status === 422 ? { detail: [{ loc: ["body", "question"], msg: "Field required", type: "missing" }] }
      : { detail: "synthetic failure" };
    global.fetch = vi.fn().mockResolvedValue(Response.json(error, { status }));
    const app = buildServer();
    try {
      const response = await app.inject({ method: "POST", url: "/query/why", payload: { workspace_slug: "synthetic" } });
      expect(response.statusCode).toBe(status);
      expect(response.json()).toEqual(error);
    } finally { await app.close(); }
  });

  it("retains readable non-JSON upstream errors", async () => {
    global.fetch = vi.fn().mockResolvedValue(new Response("synthetic unavailable", { status: 503 }));
    const app = buildServer();
    try {
      const response = await app.inject({ method: "POST", url: "/query/why", payload: { workspace_slug: "synthetic", question: "why" } });
      expect(response.statusCode).toBe(503);
      expect(response.json()).toEqual({ error: "synthetic unavailable" });
    } finally { await app.close(); }
  });

  it.each(["network", "invalid-json"])("uses the existing 502 transport envelope for %s", async (failure) => {
    global.fetch = failure === "network" ? vi.fn().mockRejectedValue(new Error("synthetic offline"))
      : vi.fn().mockResolvedValue(new Response("not valid JSON", { status: 200 }));
    const app = buildServer();
    try {
      const response = await app.inject({ method: "POST", url: "/query/why", payload: { workspace_slug: "synthetic", question: "why" } });
      expect(response.statusCode).toBe(502);
      expect(response.json()).toMatchObject({ error: "Upstream engine request failed" });
    } finally { await app.close(); }
  });
});
