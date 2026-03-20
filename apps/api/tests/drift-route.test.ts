import { buildServer } from "../src/server";

describe("drift routes", () => {
  it("proxies GET /drift", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({
        workspace_mode: "demo",
        source_summary: "This workspace is using seeded demo data for a guided product walkthrough.",
        alerts: [{ id: 1, alert_type: "possible_drift", status: "open" }]
      })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "GET",
      url: "/drift?workspace_slug=demo-workspace"
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({
      workspace_mode: "demo",
      source_summary: "This workspace is using seeded demo data for a guided product walkthrough.",
      alerts: [{ id: 1, alert_type: "possible_drift", status: "open" }]
    });

    global.fetch = originalFetch;
  });

  it("proxies POST /drift/evaluate", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({ status: "ok", created_alerts: 1, evaluated_rules: 1 })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/drift/evaluate",
      payload: { workspace_slug: "demo-workspace" }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({ status: "ok", created_alerts: 1, evaluated_rules: 1 });

    global.fetch = originalFetch;
  });
});
