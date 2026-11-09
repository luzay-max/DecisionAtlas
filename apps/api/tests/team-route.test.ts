import { buildServer } from "../src/server";

describe("teamRoute", () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("forwards admin account creation with the session cookie and strips owner scope overrides", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      text: async () =>
        JSON.stringify({
          account: {
            id: 3,
            username: "reviewer-user",
            display_name: null,
            status: "active",
            bootstrap: false,
            role: "reviewer",
          },
        }),
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/team/accounts",
      headers: { cookie: "decisionatlas_session=admin-token" },
      payload: {
        username: "reviewer-user",
        password: "password123",
        role: "reviewer",
        owner_scope: "malicious-scope",
      },
    });

    expect(response.statusCode).toBe(200);
    expect(global.fetch).toHaveBeenCalledWith("http://localhost:8000/team/accounts", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-decisionatlas-session-token": "admin-token",
      },
      body: JSON.stringify({
        username: "reviewer-user",
        password: "password123",
        role: "reviewer",
      }),
    });
  });

  it("forwards disabled-user denials from the engine", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      status: 401,
      ok: false,
      text: async () => JSON.stringify({ detail: "User account is disabled" }),
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "GET",
      url: "/team/accounts",
      headers: { cookie: "decisionatlas_session=disabled-token" },
    });

    expect(response.statusCode).toBe(401);
    expect(response.json()).toEqual({ detail: "User account is disabled" });
  });

  it("forwards workspace member assignment with session cookies", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      text: async () =>
        JSON.stringify({
          member: {
            workspace_id: 1,
            actor: { id: 2, username: "viewer-user", status: "active", bootstrap: false, role: "viewer" },
            role: "viewer",
          },
        }),
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "PUT",
      url: "/team/workspaces/demo-workspace/members/2",
      headers: { cookie: "decisionatlas_session=admin-token" },
      payload: { role: "viewer" },
    });

    expect(response.statusCode).toBe(200);
    expect(global.fetch).toHaveBeenCalledWith("http://localhost:8000/team/workspaces/demo-workspace/members/2", {
      method: "PUT",
      headers: {
        "content-type": "application/json",
        "x-decisionatlas-session-token": "admin-token",
      },
      body: JSON.stringify({ role: "viewer" }),
    });
  });
  it("forwards password reset, role update and member removal through generated Team operations", async () => {
    const payloads = [
      { account: { id: 2, username: "viewer-user", display_name: null, status: "active", bootstrap: false, role: "viewer" } },
      { account: { id: 2, username: "viewer-user", display_name: null, status: "active", bootstrap: false, role: "reviewer" } },
      { removed: true },
    ];
    global.fetch = vi.fn().mockImplementation(async () => {
      const payload = payloads.shift();
      return new Response(JSON.stringify(payload), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    });

    const app = buildServer();
    const reset = await app.inject({
      method: "POST",
      url: "/team/accounts/2/reset-password",
      headers: { cookie: "decisionatlas_session=admin-token" },
      payload: { password: "new-password-123" },
    });
    expect(reset.statusCode).toBe(200);
    expect(reset.json().account.role).toBe("viewer");
    expect(global.fetch).toHaveBeenNthCalledWith(1, "http://localhost:8000/team/accounts/2/reset-password", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-decisionatlas-session-token": "admin-token",
      },
      body: JSON.stringify({ password: "new-password-123" }),
    });

    const role = await app.inject({
      method: "POST",
      url: "/team/accounts/2/role",
      headers: { cookie: "decisionatlas_session=admin-token" },
      payload: { role: "reviewer" },
    });
    expect(role.statusCode).toBe(200);
    expect(role.json().account.role).toBe("reviewer");

    const removed = await app.inject({
      method: "DELETE",
      url: "/team/workspaces/demo-workspace/members/2",
      headers: { cookie: "decisionatlas_session=admin-token" },
    });
    expect(removed.statusCode).toBe(200);
    expect(removed.json()).toEqual({ removed: true });
    expect(global.fetch).toHaveBeenNthCalledWith(3, "http://localhost:8000/team/workspaces/demo-workspace/members/2", {
      method: "DELETE",
      headers: { "x-decisionatlas-session-token": "admin-token" },
    });

    await app.close();
  });

});
