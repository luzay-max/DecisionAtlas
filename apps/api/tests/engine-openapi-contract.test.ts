import { describe, expect, it } from "vitest";
import { ENGINE_BFF_ROUTES } from "../src/contracts/engine-bff-routes";

describe("Engine OpenAPI / Fastify BFF route contract", () => {
  it("declares each Engine-backed BFF operation exactly once", () => {
    expect(ENGINE_BFF_ROUTES).toHaveLength(39);
    expect(new Set(ENGINE_BFF_ROUTES).size).toBe(ENGINE_BFF_ROUTES.length);
  });

  it("keeps local health and unexposed Engine lifecycle routes out of the proxy inventory", () => {
    expect(ENGINE_BFF_ROUTES).not.toContain("GET /health");
    expect(ENGINE_BFF_ROUTES).not.toContain("POST /governance/rules/{draft_id}/lifecycle");
  });
});
