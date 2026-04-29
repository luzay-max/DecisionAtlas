import { describe, expect, it, vi } from "vitest";
import { buildServer } from "../src/server";

describe("governance routes", () => {
  it("proxies governance document import", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          document: { id: 1, title: "Standards" },
          drafts: [{ id: 2, title: "Rule: tests" }],
        }),
        { status: 200, headers: { "content-type": "application/json" } }
      )
    );
    const app = buildServer();

    const response = await app.inject({
      method: "POST",
      url: "/governance/documents",
      payload: {
        title: "Standards",
        document_type: "coding_guideline",
        content: "## Rule: tests\n\nMust test changes.",
      },
    });

    expect(response.statusCode).toBe(200);
    expect(response.json().drafts[0].title).toBe("Rule: tests");
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/governance/documents",
      expect.objectContaining({ method: "POST" })
    );
    fetchMock.mockRestore();
  });

  it("proxies governance rule review", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ rule: { id: 7, review_state: "accepted" } }), {
        status: 200,
        headers: { "content-type": "application/json" },
      })
    );
    const app = buildServer();

    const response = await app.inject({
      method: "POST",
      url: "/governance/rules/7/review",
      payload: { review_state: "accepted" },
    });

    expect(response.statusCode).toBe(200);
    expect(response.json().rule.review_state).toBe("accepted");
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/governance/rules/7/review",
      expect.objectContaining({ method: "POST" })
    );
    fetchMock.mockRestore();
  });
});
