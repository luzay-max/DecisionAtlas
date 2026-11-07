// Compiled by pnpm typecheck, never executed. An unused @ts-expect-error fails
// CI if generation or client inference silently widens any of these types.
import type { WhyRequest, WhyResponse } from "@decisionatlas/engine-contract";
import { createWhyEngineClient } from "../src/contracts/engine-client";

export async function contractMustRejectDrift() {
  const client = createWhyEngineClient("http://engine.invalid");
  // @ts-expect-error wrong path
  client.POST("/query/whyy", { body: { workspace_slug: "synthetic", question: "why" } });
  // @ts-expect-error wrong method
  client.GET("/query/why");
  // @ts-expect-error missing required question
  client.POST("/query/why", { body: { workspace_slug: "synthetic" } });
  // @ts-expect-error wrong request field type
  const badRequest: WhyRequest = { workspace_slug: 42, question: "why" };
  const { data, error } = await client.POST("/query/why", {
    body: { workspace_slug: "synthetic", question: "why" },
  });
  if (data) {
    const response: WhyResponse = data;
    const answer: string = response.answer;
    // @ts-expect-error response type is generated, not any
    const wrong: number = response.answer;
    // @ts-expect-error unsupported retrieval mode
    response.retrieval_mode = "invented-vector-mode";
    // @ts-expect-error nullable citation URL cannot be assumed to be a string
    const url: string = response.citations[0].url;
    void [answer, wrong, url];
  }
  if (error) {
    // @ts-expect-error error DTO must not be consumed as successful answer
    const answer: string = error.answer;
    void answer;
  }
  void badRequest;
}
