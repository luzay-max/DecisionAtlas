import createClient from "openapi-fetch";
import type { paths, WhyRequest } from "@decisionatlas/engine-contract";
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
