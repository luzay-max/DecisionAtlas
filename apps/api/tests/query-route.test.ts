import { buildServer } from "../src/server";

describe("POST /query/why", () => {
  it("proxies why queries", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({
        status: "ok",
        answer: "Use Redis Cache: Use Redis as cache only",
        answer_context: {
          workspace_mode: "demo",
          source_summary: "This workspace is using seeded demo data for a guided product walkthrough."
        },
        citations: [{ quote: "We decided to use Redis as cache" }]
      })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/query/why",
      payload: {
        workspace_slug: "demo-workspace",
        question: "why use redis cache"
      }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toHaveProperty("status", "ok");

    global.fetch = originalFetch;
  });
});
