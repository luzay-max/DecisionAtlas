import { buildServer } from "../src/server";

describe("security boundaries", () => {
  const oldEnv = {
    APP_ENV: process.env.APP_ENV,
    CORS_ALLOWED_ORIGINS: process.env.CORS_ALLOWED_ORIGINS,
    ENGINE_BASE_URL: process.env.ENGINE_BASE_URL,
    AUTO_BOOTSTRAP_AUTH: process.env.AUTO_BOOTSTRAP_AUTH,
  };
  const oldFetch = global.fetch;
  beforeEach(() => {
    process.env.ENGINE_BASE_URL = "http://localhost:8000";
    process.env.AUTO_BOOTSTRAP_AUTH = "false";
    process.env.CORS_ALLOWED_ORIGINS = "https://atlas.example";
  });

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

  it("fails closed when the production CORS allowlist is missing", () => {
    process.env.APP_ENV = "production";
    delete process.env.CORS_ALLOWED_ORIGINS;
    expect(() => buildServer()).toThrow("CORS_ALLOWED_ORIGINS");
  });

  it("rejects state-changing requests from untrusted browser Origins", async () => {
    process.env.APP_ENV = "production";
    process.env.CORS_ALLOWED_ORIGINS = "https://atlas.example";
    const app = buildServer();
    const blocked = await app.inject({
      method: "POST", url: "/auth/login",
      headers: { origin: "https://untrusted.example" },
      payload: { username: "alice", password: "secret" },
    });
    expect(blocked.statusCode).toBe(403);
    expect(blocked.json()).toMatchObject({ error: "Origin not allowed", code: "forbidden", message: "Origin not allowed" });
    await app.close();
  });

  it("marks session cookies secure in production and expires cookie on logout", async () => {
    process.env.APP_ENV = "production";
    global.fetch = vi.fn()
      .mockResolvedValueOnce(Response.json({
        session_token: "test-token",
        actor: { id: 1, username: "member", bootstrap: false, status: "active" },
        current_owner_scope: "team-a",
        role: "viewer",
        available_scopes: [{ owner_scope: "team-a", role: "viewer" }],
      }))
      .mockResolvedValue(Response.json({ status: "signed_out" }));
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
