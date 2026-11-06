import { describe, expect, it } from "vitest";
import { buildServer } from "../src/server";
import { ENGINE_BFF_ROUTES } from "../src/contracts/engine-bff-routes";

describe("Engine OpenAPI / Fastify BFF route contract", () => {
  it("maps each Engine-backed operation to a registered Fastify route", async () => {
    expect(ENGINE_BFF_ROUTES).toHaveLength(39);
    expect(new Set(ENGINE_BFF_ROUTES.map((route) => route.engine)).size).toBe(ENGINE_BFF_ROUTES.length);

    const app = buildServer();
    try {
      await app.ready();
      for (const route of ENGINE_BFF_ROUTES) {
        expect(
          app.hasRoute({ method: route.bffMethod, url: route.bffPath }),
          `${route.bffMethod} ${route.bffPath} should be registered by the Fastify BFF`
        ).toBe(true);
      }
    } finally {
      await app.close();
    }
  });

  it("keeps local health and unexposed Engine lifecycle routes out of the proxy inventory", async () => {
    expect(ENGINE_BFF_ROUTES.map((route) => route.engine)).not.toContain("GET /health");
    expect(ENGINE_BFF_ROUTES.map((route) => route.engine)).not.toContain("POST /governance/rules/{draft_id}/lifecycle");

    const app = buildServer();
    try {
      await app.ready();
      expect(app.hasRoute({ method: "GET", url: "/health" })).toBe(true);
      expect(app.hasRoute({ method: "POST", url: "/governance/rules/:draftId/lifecycle" })).toBe(false);
    } finally {
      await app.close();
    }
  });
});
