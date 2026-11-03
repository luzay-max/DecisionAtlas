import { vi } from "vitest";

import { askWhy, loginProductSession, saveProductSessionToken } from "../lib/api";

describe("B03 same-origin browser API transport", () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
    window.localStorage.clear();
  });

  it("calls same-origin Next /backend with cookies rather than localStorage token headers", async () => {
    window.localStorage.setItem("decisionatlas-session-token", "obsolete-accessible-token");
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      json: async () => ({
        status: "evidence_limited",
        question: "why",
        answer: "No evidence",
        citations: [],
      }),
    } as Response);

    await askWhy("public-repo", "why");
    expect(global.fetch).toHaveBeenCalledTimes(1);
    const [url, init] = vi.mocked(global.fetch).mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/backend/query/why");
    expect(init.method).toBe("POST");
    expect(init.credentials).toBe("same-origin");
    const headers = new Headers(init.headers);
    expect(headers.get("content-type")).toBe("application/json");
    expect(headers.has("x-decisionatlas-session-token")).toBe(false);
    expect(headers.has("cookie")).toBe(false);
  });

  it("logs in through same-origin API and purges old JS-readable tokens", async () => {
    window.localStorage.setItem("decisionatlas-session-token", "old-token");
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      json: async () => ({
        session_token: "new-login-token",
        actor: { id: 1, username: "admin" },
        current_owner_scope: "local-default",
        role: "admin",
        available_scopes: [],
      }),
    } as Response);

    const session = await loginProductSession("admin", "test-password");
    expect(session.session_token).toBe("new-login-token");
    const [url, init] = vi.mocked(global.fetch).mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/backend/auth/login");
    expect(init.credentials).toBe("same-origin");
    expect(new Headers(init.headers).has("x-decisionatlas-session-token")).toBe(false);
    saveProductSessionToken(session.session_token);
    expect(window.localStorage.getItem("decisionatlas-session-token")).toBeNull();
  });
});
