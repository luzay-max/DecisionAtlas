import { buildServer } from "../src/server";

describe("GET /health", () => {
  it("returns ok", async () => {
    const app = buildServer();

    const response = await app.inject({
      method: "GET",
      url: "/health"
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({ ok: true });
  });
});
