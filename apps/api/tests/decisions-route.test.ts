import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { buildServer } from "../src/server";

const fixtures = resolve(__dirname, "../../../packages/engine-contract/fixtures");
const listFixture = JSON.parse(readFileSync(resolve(fixtures, "decisions-list.json"), "utf8"));
const detailFixture = JSON.parse(readFileSync(resolve(fixtures, "decision-detail.json"), "utf8"));
const reviewFixture = JSON.parse(readFileSync(resolve(fixtures, "decision-review.json"), "utf8"));

describe("Decisions generated DTO client", () => {
  const originalFetch = global.fetch;
  afterEach(() => { global.fetch = originalFetch; });

  it("proxies the typed list query and preserves citations, review state, and nullable fields", async () => {
    global.fetch = vi.fn().mockResolvedValue(Response.json(listFixture));
    const app = buildServer();
    try {
      const response = await app.inject({
        method: "GET",
        url: "/decisions?workspace_slug=imported-workspace&review_state=candidate",
      });
      expect(response.statusCode).toBe(200);
      expect(response.json()).toEqual(listFixture);
      const upstream = vi.mocked(global.fetch).mock.calls[0][0] as Request;
      expect(upstream.url).toBe("http://localhost:8000/decisions?workspace_slug=imported-workspace&review_state=candidate");
      expect(upstream.method).toBe("GET");
    } finally {
      await app.close();
    }
  });

  it("proxies the typed detail path and preserves empty and audit collections", async () => {
    global.fetch = vi.fn().mockResolvedValue(Response.json(detailFixture));
    const app = buildServer();
    try {
      const response = await app.inject({ method: "GET", url: "/decisions/1" });
      expect(response.statusCode).toBe(200);
      expect(response.json()).toEqual(detailFixture);
      const upstream = vi.mocked(global.fetch).mock.calls[0][0] as Request;
      expect(upstream.url).toBe("http://localhost:8000/decisions/1");
      expect(upstream.method).toBe("GET");
    } finally {
      await app.close();
    }
  });

  it("proxies the typed review body without changing the returned audit event", async () => {
    global.fetch = vi.fn().mockResolvedValue(Response.json(reviewFixture));
    const app = buildServer();
    try {
      const payload = { review_state: "accepted", review_rationale: "Reviewed synthetic evidence." };
      const response = await app.inject({ method: "POST", url: "/decisions/1/review", payload });
      expect(response.statusCode).toBe(200);
      expect(response.json()).toEqual(reviewFixture);
      const upstream = vi.mocked(global.fetch).mock.calls[0][0] as Request;
      expect(upstream.url).toBe("http://localhost:8000/decisions/1/review");
      expect(upstream.method).toBe("POST");
      expect(await upstream.json()).toEqual(payload);
    } finally {
      await app.close();
    }
  });

  it.each([400, 401, 403, 404, 422])("retains Engine error status %s and its body", async (status) => {
    const error = { detail: "synthetic failure" };
    global.fetch = vi.fn().mockResolvedValue(Response.json(error, { status }));
    const app = buildServer();
    try {
      const response = await app.inject({ method: "GET", url: "/decisions/1" });
      expect(response.statusCode).toBe(status);
      expect(response.json()).toEqual(error);
    } finally {
      await app.close();
    }
  });

  it("keeps the existing 502 envelope for upstream transport failures", async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error("synthetic offline"));
    const app = buildServer();
    try {
      const response = await app.inject({ method: "GET", url: "/decisions/1" });
      expect(response.statusCode).toBe(502);
      expect(response.json()).toMatchObject({ error: "Upstream engine request failed" });
    } finally {
      await app.close();
    }
  });
});
