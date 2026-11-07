import createClient from "openapi-fetch";
import type { DecisionListQuery, DecisionReviewRequest, paths, WhyRequest } from "@decisionatlas/engine-contract";
import type { FastifyBaseLogger } from "fastify";
import { fetchUpstreamPayload } from "../proxy";

// Only audited, model-backed operations are admitted to this client. Other
// generated paths still have untyped dict responses and are not claimed safe.
export function createWhyEngineClient(baseUrl: string) {
  return createClient<Pick<paths, "/query/why">>({
    baseUrl,
    fetch: (request) => globalThis.fetch(request),
  });
}

export async function fetchWhy(
  baseUrl: string,
  body: WhyRequest,
  headers: Record<string, string>,
  logger: FastifyBaseLogger,
) {
  try {
    const result = await createWhyEngineClient(baseUrl).POST("/query/why", { body, headers });
    // Engine's response_model validates successful payloads at runtime. The
    // generated client supplies static types; it is not a second validator.
    const payload = result.response.ok ? result.data : result.error;
    return {
      status: result.response.status,
      payload: typeof payload === "string" ? { error: payload } : payload ?? null,
    };
  } catch (error) {
    // Preserve the existing transport-failure envelope and server-side logging.
    return fetchUpstreamPayload(Promise.reject(error), logger, "POST /query/why");
  }
}

type DecisionsPaths = Pick<
  paths,
  "/decisions" | "/decisions/{decision_id}" | "/decisions/{decision_id}/review"
>;

export function createDecisionsEngineClient(baseUrl: string) {
  return createClient<DecisionsPaths>({
    baseUrl,
    fetch: (request) => globalThis.fetch(request),
  });
}

function decisionsProxyResult(response: Response, data: unknown, error: unknown) {
  const payload = response.ok ? data : error;
  return {
    status: response.status,
    payload: typeof payload === "string" ? { error: payload } : payload ?? null,
  };
}

export async function fetchDecisionsList(
  baseUrl: string,
  query: DecisionListQuery,
  headers: Record<string, string>,
  logger: FastifyBaseLogger,
) {
  try {
    const result = await createDecisionsEngineClient(baseUrl).GET("/decisions", {
      params: { query },
      headers,
    });
    return decisionsProxyResult(result.response, result.data, result.error);
  } catch (error) {
    return fetchUpstreamPayload(Promise.reject(error), logger, "GET /decisions");
  }
}

export async function fetchDecisionDetail(
  baseUrl: string,
  decisionId: number,
  headers: Record<string, string>,
  logger: FastifyBaseLogger,
) {
  try {
    const result = await createDecisionsEngineClient(baseUrl).GET("/decisions/{decision_id}", {
      params: { path: { decision_id: decisionId } },
      headers,
    });
    return decisionsProxyResult(result.response, result.data, result.error);
  } catch (error) {
    return fetchUpstreamPayload(Promise.reject(error), logger, "GET /decisions/:id");
  }
}

export async function fetchDecisionReview(
  baseUrl: string,
  decisionId: number,
  body: DecisionReviewRequest,
  headers: Record<string, string>,
  logger: FastifyBaseLogger,
) {
  try {
    const result = await createDecisionsEngineClient(baseUrl).POST("/decisions/{decision_id}/review", {
      params: { path: { decision_id: decisionId } },
      body,
      headers,
    });
    return decisionsProxyResult(result.response, result.data, result.error);
  } catch (error) {
    return fetchUpstreamPayload(Promise.reject(error), logger, "POST /decisions/:id/review");
  }
}
