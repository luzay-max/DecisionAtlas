import { vi } from "vitest";
import { askWhy, saveProductSessionToken, type RetrievalMode, type WhyAnswerResponse } from "../lib/api";

describe("B02 Why mode + B03 same-origin session transport in the same Web bundle", () => {
  const originalFetch = global.fetch;
  afterEach(() => {
    global.fetch = originalFetch;
    window.localStorage.clear();
  });

  it.each(["lexical_only", "lexical_fallback", "hybrid"] as RetrievalMode[])(
    "retains %s on Chinese Why while never sending localStorage tokens to BFF",
    async (mode) => {
      window.localStorage.setItem("decisionatlas-session-token", "legacy-untrusted-token");
      const payload: WhyAnswerResponse = {
        status: "evidence_limited",
        question: "为什么使用 PostgreSQL 主库？",
        answer: "Evidence requires independent review.",
        retrieval_mode: mode,
        answer_context: {
          workspace_mode: "demo",
          source_summary: "synthetic",
          retrieval_mode: mode,
        },
        citations: [],
      };
      global.fetch = vi.fn().mockResolvedValue({
        status: 200,
        ok: true,
        json: async () => payload,
      } as Response);

      const result: WhyAnswerResponse = await askWhy("public-synthetic", payload.question);
      expect(result.retrieval_mode).toBe(mode);
      expect(result.answer_context.retrieval_mode).toBe(mode);
      const [url, init] = vi.mocked(global.fetch).mock.calls[0] as [string, RequestInit];
      expect(url).toBe("/backend/query/why");
      expect(init.method).toBe("POST");
      expect(init.credentials).toBe("same-origin");
      expect(JSON.parse(String(init.body))).toEqual({
        workspace_slug: "public-synthetic",
        question: "为什么使用 PostgreSQL 主库？",
      });
      expect(new Headers(init.headers).has("x-decisionatlas-session-token")).toBe(false);
      expect(new Headers(init.headers).has("cookie")).toBe(false);
      saveProductSessionToken("not-js-readable");
      expect(window.localStorage.getItem("decisionatlas-session-token")).toBeNull();
    },
  );
});
