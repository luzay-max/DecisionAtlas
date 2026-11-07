import createClient from "openapi-fetch";
import type { DecisionListQuery, DecisionReviewRequest, GitHubImportRequest, GitHubInstallationBindingRequest, GitHubPrivateAccessBindingRequest, GitSourceBindingRequest, ImportLookupQuery, paths, WhyRequest } from "@decisionatlas/engine-contract";
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

type ImportsPaths = Pick<
  paths,
  | "/imports/lookup"
  | "/imports/github"
  | "/imports/github/installations/bind"
  | "/imports/github/private-access/bind"
  | "/imports/git-sources/bind"
  | "/imports/github/webhook"
  | "/imports/capabilities"
  | "/imports/{job_id}"
  | "/imports/{job_id}/pause"
  | "/imports/{job_id}/resume"
>;

async function forwardImportRequest(request: Request): Promise<Response> {
  const headers = Object.fromEntries(
    [...request.headers.entries()].filter(([name]) => name.toLowerCase() !== "accept")
  );
  const init: RequestInit = { headers };
  if (request.method !== "GET") init.method = request.method;
  if (request.method !== "GET" && request.method !== "HEAD") {
    const body = await request.clone().text();
    if (body.length > 0) init.body = body;
  }
  // Keep a copy of the raw body before openapi-fetch consumes/parses the Response.
  // Its non-2xx parser may turn JSON strings such as "123" or "false" into scalars.
  const response = await globalThis.fetch(request.url, init);
  importsRawResponseBodies.set(response, response.clone().text());
  return response;
}

export function createImportsEngineClient(baseUrl: string) {
  return createClient<ImportsPaths>({
    baseUrl,
    fetch: forwardImportRequest,
  });
}

const importsRawResponseBodies = new WeakMap<Response, Promise<string>>();

function parseImportsPayload(response: Response, rawBody: string): unknown {
  if (rawBody.length === 0) return null;

  try {
    // Parse the original body exactly once, independent of Content-Type and
    // openapi-fetch's success/error parsing behavior.
    return JSON.parse(rawBody) as unknown;
  } catch {
    return response.ok ? { message: rawBody } : { error: rawBody };
  }
}

async function importsProxyResult(response: Response) {
  const rawBody = importsRawResponseBodies.get(response);
  if (!rawBody) {
    throw new Error("Imports Engine response is missing its captured raw body");
  }
  return { status: response.status, payload: parseImportsPayload(response, await rawBody) };
}

async function importRequest(
  request: Promise<{ response: Response; data?: unknown; error?: unknown }>,
  logger: FastifyBaseLogger,
  route: string,
) {
  try {
    const result = await request;
    return await importsProxyResult(result.response);
  } catch (error) {
    return fetchUpstreamPayload(Promise.reject(error), logger, route);
  }
}

export function fetchImportLookup(
  baseUrl: string,
  repo: string,
  headers: Record<string, string>,
  logger: FastifyBaseLogger,
) {
  const query: ImportLookupQuery = { repo };
  return importRequest(
    createImportsEngineClient(baseUrl).GET("/imports/lookup", { params: { query }, headers, parseAs: "text" }),
    logger,
    "GET /imports/lookup",
  );
}

export function createGitHubImport(
  baseUrl: string,
  body: GitHubImportRequest,
  headers: Record<string, string>,
  logger: FastifyBaseLogger,
) {
  return importRequest(
    createImportsEngineClient(baseUrl).POST("/imports/github", { body, headers, parseAs: "text" }),
    logger,
    "POST /imports/github",
  );
}

export function bindGitHubInstallation(
  baseUrl: string,
  body: GitHubInstallationBindingRequest,
  headers: Record<string, string>,
  logger: FastifyBaseLogger,
) {
  return importRequest(
    createImportsEngineClient(baseUrl).POST("/imports/github/installations/bind", { body, headers, parseAs: "text" }),
    logger,
    "POST /imports/github/installations/bind",
  );
}

export function bindGitHubPrivateAccess(
  baseUrl: string,
  body: GitHubPrivateAccessBindingRequest,
  headers: Record<string, string>,
  logger: FastifyBaseLogger,
) {
  return importRequest(
    createImportsEngineClient(baseUrl).POST("/imports/github/private-access/bind", { body, headers, parseAs: "text" }),
    logger,
    "POST /imports/github/private-access/bind",
  );
}

export function bindGitSource(
  baseUrl: string,
  body: GitSourceBindingRequest,
  headers: Record<string, string>,
  logger: FastifyBaseLogger,
) {
  return importRequest(
    createImportsEngineClient(baseUrl).POST("/imports/git-sources/bind", { body, headers, parseAs: "text" }),
    logger,
    "POST /imports/git-sources/bind",
  );
}

export function fetchImportCapabilities(
  baseUrl: string,
  headers: Record<string, string>,
  logger: FastifyBaseLogger,
) {
  return importRequest(
    createImportsEngineClient(baseUrl).GET("/imports/capabilities", { headers, parseAs: "text" }),
    logger,
    "GET /imports/capabilities",
  );
}

export function fetchImportJob(
  baseUrl: string,
  jobId: string,
  headers: Record<string, string>,
  logger: FastifyBaseLogger,
) {
  return importRequest(
    createImportsEngineClient(baseUrl).GET("/imports/{job_id}", {
      params: { path: { job_id: jobId } },
      headers,
      parseAs: "text",
    }),
    logger,
    "GET /imports/:jobId",
  );
}

export function updateImportJobControl(
  baseUrl: string,
  jobId: string,
  action: "pause" | "resume",
  headers: Record<string, string>,
  logger: FastifyBaseLogger,
) {
  const client = createImportsEngineClient(baseUrl);
  const request = action === "pause"
    ? client.POST("/imports/{job_id}/pause", { params: { path: { job_id: jobId } }, headers, parseAs: "text" })
    : client.POST("/imports/{job_id}/resume", { params: { path: { job_id: jobId } }, headers, parseAs: "text" });
  return importRequest(request, logger, `POST /imports/:jobId/${action}`);
}

