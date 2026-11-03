import { parseCookieHeader } from "../src/auth";
import { buildServer } from "../src/server";

describe("B03: session-cookie parsing and forwarding boundaries", () => {
  const oldFetch = global.fetch;
  const originalBootstrap = process.env.AUTO_BOOTSTRAP_AUTH;

  afterEach(() => {
    global.fetch = oldFetch;
    if (originalBootstrap === undefined) {
      delete process.env.AUTO_BOOTSTRAP_AUTH;
    } else {
      process.env.AUTO_BOOTSTRAP_AUTH = originalBootstrap;
    }
  });

  it("decodes a single valid session cookie, retaining embedded equals", () => {
    const parsed = parseCookieHeader("theme=dark; decisionatlas_session=a%2Bb%3D%3D; ignored");
    expect(parsed["decisionatlas_session"]).toBe("a+b==");
    expect(parsed.theme).toBe("dark");
  });

  it("fails closed on malformed percent sequences, duplicate names and control bytes", () => {
    const broken = parseCookieHeader("decisionatlas_session=%ZZ; theme=ok");
    expect(broken["decisionatlas_session"]).toBeUndefined();
    expect(broken.theme).toBe("ok");

    const duplicate = parseCookieHeader("decisionatlas_session=first; decisionatlas_session=second");
    expect(duplicate["decisionatlas_session"]).toBeUndefined();
    const invalidThenValid = parseCookieHeader("decisionatlas_session=%ZZ; decisionatlas_session=valid");
    expect(invalidThenValid["decisionatlas_session"]).toBeUndefined();
    const controlThenValid = parseCookieHeader("decisionatlas_session=%0A; decisionatlas_session=valid");
    expect(controlThenValid["decisionatlas_session"]).toBeUndefined();

    const encodedControl = parseCookieHeader("decisionatlas_session=%0D%0AInjected");
    expect(encodedControl["decisionatlas_session"]).toBeUndefined();

    expect(parseCookieHeader("decisionatlas_session=x".repeat(900))["decisionatlas_session"]).toBeUndefined();
    expect(({} as Record<string, unknown>).polluted).toBeUndefined();
    parseCookieHeader("__proto__=polluted; constructor=x");
    expect(({} as Record<string, unknown>).polluted).toBeUndefined();
  });

  it("does not crash or authenticate on malformed and duplicate cookies", async () => {
    process.env.AUTO_BOOTSTRAP_AUTH = "false";
    global.fetch = vi.fn();
    const app = buildServer();
    for (const cookie of [
      "decisionatlas_session=%",
      "decisionatlas_session=first; decisionatlas_session=second",
      "decisionatlas_session=%0Aheader",
    ]) {
      const response = await app.inject({
        method: "GET",
        url: "/auth/session",
        headers: { cookie },
      });
      expect(response.statusCode).toBe(401);
    }
    expect(global.fetch).not.toHaveBeenCalled();
    await app.close();
  });

  it("forwards only the cookie-derived token to Engine and never client token header", async () => {
    process.env.AUTO_BOOTSTRAP_AUTH = "false";
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      text: async () => JSON.stringify({ role: "viewer", current_owner_scope: "local-default" }),
    } as Response);
    const app = buildServer();
    const response = await app.inject({
      method: "GET",
      url: "/auth/session",
      headers: {
        cookie: "decisionatlas_session=real%2Dcookie",
        "x-decisionatlas-session-token": "untrusted-browser-header",
      },
    });
    expect(response.statusCode).toBe(200);
    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/auth/session",
      { headers: { "x-decisionatlas-session-token": "real-cookie" } },
    );
    await app.close();
  });
});
