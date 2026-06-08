import { buildServer } from "../src/server";

describe("drift routes", () => {
  it("proxies GET /drift", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({
        workspace_mode: "demo",
        source_summary: "This workspace is using seeded demo data for a guided product walkthrough.",
        evaluation: null,
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
      evaluation: null,
      alerts: [{ id: 1, alert_type: "possible_drift", status: "open" }]
    });

    global.fetch = originalFetch;
  });

  it("proxies POST /drift/evaluate", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({
        status: "ok",
        created_alerts: 1,
        evaluated_rules: 1,
        evaluation: { state: "alerts_present", can_evaluate: true, next_action: "inspect_alerts", last_evaluated_at: null }
      })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/drift/evaluate",
      payload: { workspace_slug: "demo-workspace" }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({
      status: "ok",
      created_alerts: 1,
      evaluated_rules: 1,
      evaluation: { state: "alerts_present", can_evaluate: true, next_action: "inspect_alerts", last_evaluated_at: null }
    });

    global.fetch = originalFetch;
  });

  it("proxies POST /drift/alerts/:alertId/disposition", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({
        alert: { id: 1, status: "resolved", handled_by: "local-admin" },
        audit_event: { id: 9, action: "drift_alert_disposition_resolved" }
      })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/drift/alerts/1/disposition",
      payload: { status: "resolved", rationale: "Handled during release review." }
    });

    expect(response.statusCode).toBe(200);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/drift/alerts/1/disposition"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ status: "resolved", rationale: "Handled during release review." })
      })
    );
    expect(response.json()).toEqual({
      alert: { id: 1, status: "resolved", handled_by: "local-admin" },
      audit_event: { id: 9, action: "drift_alert_disposition_resolved" }
    });

    global.fetch = originalFetch;
  });
});
