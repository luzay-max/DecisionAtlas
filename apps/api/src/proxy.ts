import { FastifyBaseLogger } from "fastify";

type ProxyResult = {
  status: number;
  payload: unknown;
};

const UPSTREAM_ERROR_MESSAGE = "Upstream engine request failed";
const UNREADABLE_RESPONSE_MESSAGE = "Upstream engine returned an unreadable response";

export async function fetchUpstreamPayload(
  request: Promise<Response>,
  logger: FastifyBaseLogger,
  route: string
): Promise<ProxyResult> {
  try {
    const response = await request;
    const payload = await readUpstreamPayload(response);
    return {
      status: response.status,
      payload,
    };
  } catch (error) {
    logger.error({ err: error, route }, "engine proxy request failed");
    return {
      status: 502,
      payload: {
        error: UPSTREAM_ERROR_MESSAGE,
        detail: error instanceof Error ? error.message : String(error),
      },
    };
  }
}

async function readUpstreamPayload(response: Response): Promise<unknown> {
  if (typeof response.text === "function") {
    const raw = await response.text();
    if (!raw) {
      return null;
    }

    try {
      return JSON.parse(raw) as unknown;
    } catch {
      return response.ok ? { message: raw } : { error: raw };
    }
  }

  if (typeof response.json === "function") {
    try {
      return await response.json();
    } catch {
      return response.ok ? null : { error: UNREADABLE_RESPONSE_MESSAGE };
    }
  }

  return response.ok ? null : { error: UNREADABLE_RESPONSE_MESSAGE };
}
