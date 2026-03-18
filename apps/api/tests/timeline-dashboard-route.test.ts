import { buildServer } from "../src/server";

describe("timeline and dashboard routes", () => {
  it("proxies GET /timeline", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => [{ id: 1, title: "Use Redis Cache" }]
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "GET",
      url: "/timeline?workspace_slug=demo-workspace"
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual([{ id: 1, title: "Use Redis Cache" }]);

    global.fetch = originalFetch;
  });

  it("proxies GET /dashboard/summary", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({
        import_status: "ready",
        artifact_count: 12,
        decision_counts: { candidate: 2, accepted: 5, rejected: 0, superseded: 0 },
        recent_alerts: []
      })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "GET",
      url: "/dashboard/summary?workspace_slug=demo-workspace"
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toHaveProperty("artifact_count", 12);

    global.fetch = originalFetch;
  });
});
