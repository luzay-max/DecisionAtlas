import { getEnv } from "../src/plugins/env";

const asEnv = (value: Record<string, string | undefined>) => value as NodeJS.ProcessEnv;

describe("Fastify API environment validation", () => {
  it("preserves safe development defaults and accepted boolean spellings", () => {
    expect(getEnv(asEnv({}))).toMatchObject({
      PORT: 3001,
      ENGINE_BASE_URL: "http://localhost:8000",
      AUTH_COOKIE_NAME: "decisionatlas_session",
      AUTO_BOOTSTRAP_AUTH: false,
      APP_ENV: "development",
      CORS_ALLOWED_ORIGINS: "",
    });
    expect(getEnv(asEnv({ AUTO_BOOTSTRAP_AUTH: "yes" })).AUTO_BOOTSTRAP_AUTH).toBe(true);
    expect(getEnv(asEnv({ AUTO_BOOTSTRAP_AUTH: "off" })).AUTO_BOOTSTRAP_AUTH).toBe(false);
  });

  it.each(["0", "-1", "65536", "1.5", "not-a-port"])("rejects invalid PORT %s without echoing the value", (value) => {
    let message = "";
    try {
      getEnv(asEnv({ PORT: value }));
    } catch (error) {
      message = error instanceof Error ? error.message : String(error);
    }
    expect(message).toContain("PORT");
    expect(message).not.toContain(value);
  });

  it.each([
    "ftp://engine.example",
    "https://user:password@engine.example",
    "https://engine.example?token=secret",
    "https://engine.example?",
    "https://engine.example#fragment",
    "https://engine.example#",
    " https://engine.example ",
    "/relative-engine",
  ])("rejects unsafe ENGINE_BASE_URL values", (value) => {
    let message = "";
    try {
      getEnv(asEnv({ ENGINE_BASE_URL: value }));
    } catch (error) {
      message = error instanceof Error ? error.message : String(error);
    }
    expect(message).toContain("ENGINE_BASE_URL");
    expect(message).not.toContain(value);
    expect(message).not.toContain("secret");
  });

  it("rejects cookie names containing separators or whitespace", () => {
    expect(() => getEnv(asEnv({ AUTH_COOKIE_NAME: "bad;name" }))).toThrow("AUTH_COOKIE_NAME");
    expect(() => getEnv(asEnv({ AUTH_COOKIE_NAME: "bad name" }))).toThrow("AUTH_COOKIE_NAME");
  });

  it.each([
    "*",
    "https://atlas.example/path",
    "https://atlas.example/",
    "https://user:password@atlas.example",
    "ftp://atlas.example",
    "not-an-origin",
  ])("rejects non-origin CORS entries", (value) => {
    let message = "";
    try {
      getEnv(asEnv({ CORS_ALLOWED_ORIGINS: value }));
    } catch (error) {
      message = error instanceof Error ? error.message : String(error);
    }
    expect(message).toContain("CORS_ALLOWED_ORIGINS");
    expect(message).not.toContain(value);
  });

  it("accepts an explicit list of exact HTTP(S) origins", () => {
    expect(getEnv(asEnv({
      CORS_ALLOWED_ORIGINS: "https://atlas.example, http://localhost:3000",
    })).CORS_ALLOWED_ORIGINS).toBe("https://atlas.example, http://localhost:3000");
  });

  it("requires an explicit Engine URL in production", () => {
    expect(() => getEnv(asEnv({ APP_ENV: "production" }))).toThrow("ENGINE_BASE_URL");
    expect(getEnv(asEnv({
      APP_ENV: "production",
      ENGINE_BASE_URL: "http://engine:8000",
      CORS_ALLOWED_ORIGINS: "https://atlas.example",
    })).APP_ENV).toBe("production");
  });

  it("requires at least one explicit CORS origin in production", () => {
    expect(() => getEnv(asEnv({
      APP_ENV: "production",
      ENGINE_BASE_URL: "http://engine:8000",
    }))).toThrow("CORS_ALLOWED_ORIGINS");
    expect(() => getEnv(asEnv({
      APP_ENV: "production",
      ENGINE_BASE_URL: "http://engine:8000",
      CORS_ALLOWED_ORIGINS: ", ,",
    }))).toThrow("CORS_ALLOWED_ORIGINS");
  });

  it("rejects anonymous auto-bootstrap in production", () => {
    expect(() => getEnv(asEnv({
      APP_ENV: "production",
      ENGINE_BASE_URL: "http://engine:8000",
      AUTO_BOOTSTRAP_AUTH: "true",
    }))).toThrow("AUTO_BOOTSTRAP_AUTH");
  });

  it("does not echo an invalid boolean value", () => {
    let message = "";
    try {
      getEnv(asEnv({ AUTO_BOOTSTRAP_AUTH: "super-secret-value" }));
    } catch (error) {
      message = error instanceof Error ? error.message : String(error);
    }
    expect(message).toContain("AUTO_BOOTSTRAP_AUTH");
    expect(message).not.toContain("super-secret-value");
  });
});
