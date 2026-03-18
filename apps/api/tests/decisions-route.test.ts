import { buildServer } from "../src/server";

describe("decision routes", () => {
  it("proxies GET /decisions", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => [{ id: 1, title: "Use Redis Cache", review_state: "candidate" }]
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "GET",
      url: "/decisions?workspace_slug=demo-workspace&review_state=candidate"
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual([{ id: 1, title: "Use Redis Cache", review_state: "candidate" }]);

    global.fetch = originalFetch;
  });

  it("proxies POST /decisions/:id/review", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({ id: 1, review_state: "accepted" })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/decisions/1/review",
      payload: { review_state: "accepted" }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({ id: 1, review_state: "accepted" });

    global.fetch = originalFetch;
  });
});
