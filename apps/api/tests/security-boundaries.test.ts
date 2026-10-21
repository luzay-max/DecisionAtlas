import { buildServer } from "../src/server";

describe("security boundaries", () => {
  const oldEnv = {
    APP_ENV: process.env.APP_ENV,
    CORS_ALLOWED_ORIGINS: process.env.CORS_ALLOWED_ORIGINS,
  };
  const oldFetch = global.fetch;
  afterEach(() => {
    for (const [key, value] of Object.entries(oldEnv)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
    global.fetch = oldFetch;
  });

  it("only exposes CORS response headers to allowed production origins", async () => {
    process.env.APP_ENV = "production";
    process.env.CORS_ALLOWED_ORIGINS = "https://atlas.example";
    const app = buildServer();
    const approved = await app.inject({
      method: "GET", url: "/health", headers: { origin: "https://atlas.example" },
    });
    expect(approved.headers["access-control-allow-origin"]).toBe("https://atlas.example");
    const blocked = await app.inject({
      method: "GET", url: "/health", headers: { origin: "https://untrusted.example" },
    });
    expect(blocked.headers["access-control-allow-origin"]).toBeUndefined();
    await app.close();
  });

  it("defaults to no arbitrary cross-origin access in production", async () => {
    process.env.APP_ENV = "production";
    delete process.env.CORS_ALLOWED_ORIGINS;
    const app = buildServer();
    const result = await app.inject({
      method: "GET", url: "/health", headers: { origin: "http://localhost:3000" },
    });
    expect(result.headers["access-control-allow-origin"]).toBeUndefined();
    await app.close();
  });

  it("marks session cookies secure in production and expires cookie on logout", async () => {
    process.env.APP_ENV = "production";
    global.fetch = vi.fn().mockResolvedValue({
      status: 200, ok: true,
      text: async () => JSON.stringify({ session_token: "test-token", status: "signed_out" }),
    } as Response);
    const app = buildServer();
    const login = await app.inject({
      method: "POST", url: "/auth/login", payload: { username: "member", password: "secret" },
    });
    expect(String(login.headers["set-cookie"])).toContain("HttpOnly");
    expect(String(login.headers["set-cookie"])).toContain("SameSite=Lax");
    expect(String(login.headers["set-cookie"])).toContain("Secure");
    const logout = await app.inject({
      method: "POST", url: "/auth/logout",
      headers: { cookie: "decisionatlas_session=test-token" },
    });
    expect(logout.statusCode).toBe(200);
    expect(String(logout.headers["set-cookie"])).toContain("Max-Age=0");
    expect(String(logout.headers["set-cookie"])).toContain("Secure");
    expect(global.fetch).toHaveBeenLastCalledWith(
      "http://localhost:8000/auth/logout",
      { method: "POST", headers: { "x-decisionatlas-session-token": "test-token" } },
    );
    await app.close();
  });
});
