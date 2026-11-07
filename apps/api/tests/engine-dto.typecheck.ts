// Compiled by pnpm typecheck, never executed. Unused @ts-expect-error directives fail CI
// if generated contracts or client inference silently widen any of these types.
import type {
  DecisionDetail,
  DecisionListItem,
  DecisionListQuery,
  DecisionReviewRequest,
  DecisionReviewResponse,
  WhyRequest,
  WhyResponse,
} from "@decisionatlas/engine-contract";
import { createDecisionsEngineClient, createWhyEngineClient } from "../src/contracts/engine-client";

export async function whyContractMustRejectDrift() {
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

export async function decisionsContractMustRejectDrift() {
  const client = createDecisionsEngineClient("http://engine.invalid");
  // @ts-expect-error wrong path
  client.GET("/decisions/{id}");
  // @ts-expect-error wrong method
  client.POST("/decisions");
  // @ts-expect-error required workspace_slug query is missing
  client.GET("/decisions");
  const query: DecisionListQuery = { workspace_slug: "synthetic", review_state: "candidate" };
  const list = await client.GET("/decisions", { params: { query } });
  if (list.data) {
    const item: DecisionListItem = list.data[0];
    const match: boolean | null = item.review_evidence.source_ref_preview[0].current_quote_match;
    const integrity: string = item.review_evidence.current_quote_integrity.status;
    // @ts-expect-error a nullable URL cannot be assumed to be a string
    const url: string = item.review_evidence.primary_artifact.url;
    // @ts-expect-error confidence is a number, not text
    const confidence: string = item.confidence;
    void [match, integrity, url, confidence];
  }

  const detail = await client.GET("/decisions/{decision_id}", {
    params: { path: { decision_id: 1 } },
  });
  if (detail.data) {
    const response: DecisionDetail = detail.data;
    const auditCount: number = response.review_history.length;
    const sourceCount: number = response.source_refs.length;
    void [auditCount, sourceCount];
  }
  // @ts-expect-error required path parameter is missing
  client.GET("/decisions/{decision_id}");

  const body: DecisionReviewRequest = { review_state: "accepted", review_rationale: null };
  const reviewed = await client.POST("/decisions/{decision_id}/review", {
    params: { path: { decision_id: 1 } },
    body,
  });
  if (reviewed.data) {
    const response: DecisionReviewResponse = reviewed.data;
    const action: string = response.audit_event.action;
    // @ts-expect-error audit history is an array, not a string
    const history: string = response.review_history;
    void [action, history];
  }
  // @ts-expect-error review_state is a string, not a number
  const invalidBody: DecisionReviewRequest = { review_state: 42 };
  // @ts-expect-error required review_state is missing
  client.POST("/decisions/{decision_id}/review", { params: { path: { decision_id: 1 } }, body: {} });
  void invalidBody;
}
