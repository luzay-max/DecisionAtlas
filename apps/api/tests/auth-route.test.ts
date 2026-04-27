import { buildServer } from "../src/server";

describe("authRoute", () => {
  const originalFetch = global.fetch;
  const originalAutoBootstrap = process.env.AUTO_BOOTSTRAP_AUTH;

  afterEach(() => {
    global.fetch = originalFetch;
    if (originalAutoBootstrap === undefined) {
      delete process.env.AUTO_BOOTSTRAP_AUTH;
    } else {
      process.env.AUTO_BOOTSTRAP_AUTH = originalAutoBootstrap;
    }
  });

  it("returns 401 for /auth/session without a cookie when auto bootstrap is disabled", async () => {
    process.env.AUTO_BOOTSTRAP_AUTH = "false";
    global.fetch = vi.fn();

    const app = buildServer();
    const response = await app.inject({
      method: "GET",
      url: "/auth/session",
    });

    expect(response.statusCode).toBe(401);
    expect(response.json()).toEqual({ detail: "Authentication required" });
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it("bootstraps /auth/session explicitly and sets the session cookie when enabled", async () => {
    process.env.AUTO_BOOTSTRAP_AUTH = "true";
    global.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        status: 200,
        ok: true,
        text: async () =>
          JSON.stringify({
            session_token: "boot-token",
            actor: { id: 1, username: "local-admin" },
            current_owner_scope: "local-default",
            role: "admin",
          }),
        json: async () => ({
          session_token: "boot-token",
          actor: { id: 1, username: "local-admin" },
          current_owner_scope: "local-default",
          role: "admin",
        }),
      } as Response)
      .mockResolvedValueOnce({
        status: 200,
        ok: true,
        text: async () =>
          JSON.stringify({
            session_token: "boot-token",
            actor: { id: 1, username: "local-admin", bootstrap: true },
            current_owner_scope: "local-default",
            role: "admin",
            available_scopes: [{ owner_scope: "local-default", role: "admin" }],
          }),
        json: async () => ({
          session_token: "boot-token",
          actor: { id: 1, username: "local-admin", bootstrap: true },
          current_owner_scope: "local-default",
          role: "admin",
          available_scopes: [{ owner_scope: "local-default", role: "admin" }],
        }),
      } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "GET",
      url: "/auth/session",
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toMatchObject({
      session_token: "boot-token",
      current_owner_scope: "local-default",
      role: "admin",
    });
    expect(String(response.headers["set-cookie"])).toContain("decisionatlas_session=boot-token");
    expect(global.fetch).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/auth/bootstrap",
      { method: "POST" }
    );
    expect(global.fetch).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/auth/session",
      { headers: { "x-decisionatlas-session-token": "boot-token" } }
    );
  });

  it("sets the session cookie after a successful login", async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      status: 200,
      ok: true,
      text: async () =>
        JSON.stringify({
          session_token: "login-token",
          actor: { id: 2, username: "admin@example.com" },
          current_owner_scope: "team-a",
          role: "admin",
          available_scopes: [{ owner_scope: "team-a", role: "admin" }],
        }),
      json: async () => ({}),
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/auth/login",
      payload: { username: "admin@example.com", password: "secret" },
    });

    expect(response.statusCode).toBe(200);
    expect(String(response.headers["set-cookie"])).toContain("decisionatlas_session=login-token");
    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/auth/login",
      {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ username: "admin@example.com", password: "secret" }),
      }
    );
  });

  it("forwards the session cookie when switching owner scope", async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      status: 200,
      ok: true,
      text: async () =>
        JSON.stringify({
          session_token: "existing-token",
          actor: { id: 2, username: "admin@example.com" },
          current_owner_scope: "team-b",
          role: "reviewer",
          available_scopes: [
            { owner_scope: "team-a", role: "admin" },
            { owner_scope: "team-b", role: "reviewer" },
          ],
        }),
      json: async () => ({}),
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/auth/scope",
      headers: { cookie: "decisionatlas_session=existing-token" },
      payload: { owner_scope: "team-b" },
    });

    expect(response.statusCode).toBe(200);
    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/auth/scope",
      {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-decisionatlas-session-token": "existing-token",
        },
        body: JSON.stringify({ owner_scope: "team-b" }),
      }
    );
  });
});
