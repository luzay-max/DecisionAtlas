import { askWhy, type WhyAnswerResponse } from "../lib/api";
import fixture from "../../../packages/engine-contract/fixtures/why-ok.json";

it("consumes the same Engine/BFF contract fixture through the existing same-origin transport", async () => {
  const originalFetch = global.fetch;
  global.fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => fixture } as Response);
  try {
    const response: WhyAnswerResponse = await askWhy("synthetic", fixture.question);
    expect(response).toEqual(fixture);
    expect(response.answer_context.retrieval?.structural_fit).toBe(21);
    const [url, init] = vi.mocked(global.fetch).mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/backend/query/why");
    expect(init.credentials).toBe("same-origin");
    expect(new Headers(init.headers).has("x-decisionatlas-session-token")).toBe(false);
  } finally { global.fetch = originalFetch; }
});
