import { buildServer } from "../src/server";

describe("runtime routes", () => {
  it("proxies GET /runtime/provider-mode", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({ mode: "fake", is_live: false })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "GET",
      url: "/runtime/provider-mode"
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({ mode: "fake", is_live: false });

    global.fetch = originalFetch;
  });

  it("proxies POST /runtime/provider-mode", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({ mode: "openai_compatible", is_live: true })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/runtime/provider-mode",
      payload: { mode: "live" }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({ mode: "openai_compatible", is_live: true });

    global.fetch = originalFetch;
  });
});
