import type { ApiErrorCode, ApiErrorResponse } from "@decisionatlas/engine-contract";

const DEFAULT_MESSAGES: Record<ApiErrorCode, string> = {
  unauthenticated: "Authentication required",
  forbidden: "Request is not allowed",
  invalid_request: "Request validation failed",
  not_found: "Resource not found",
  conflict: "Request conflicts with the current resource state",
  request_rejected: "Request was rejected",
  upstream_unavailable: "Upstream engine unavailable",
  service_unavailable: "Service temporarily unavailable",
  internal_error: "Internal server error",
};

function codeForStatus(status: number): ApiErrorCode {
  if (status === 401) return "unauthenticated";
  if (status === 403) return "forbidden";
  if (status === 400 || status === 422) return "invalid_request";
  if (status === 404) return "not_found";
  if (status === 409) return "conflict";
  if (status === 502 || status === 504) return "upstream_unavailable";
  if (status === 503) return "service_unavailable";
  if (status >= 500) return "internal_error";
  return "request_rejected";
}

function decodePayload(payload: unknown, contentType?: string): unknown {
  if (typeof payload === "string") {
    if (!contentType?.toLowerCase().includes("application/json")) return payload;
    try {
      return JSON.parse(payload) as unknown;
    } catch {
      return payload;
    }
  }
  if (typeof Buffer !== "undefined" && Buffer.isBuffer(payload)) {
    return decodePayload(payload.toString("utf8"), contentType);
  }
  if (payload instanceof Uint8Array) {
    return decodePayload(new TextDecoder().decode(payload), contentType);
  }
  return payload;
}

const SENSITIVE_KEY_FRAGMENTS = [
  "input",
  "password",
  "token",
  "authorization",
  "cookie",
  "apikey",
  "secret",
  "privatekey",
  "credential",
  "accesskey",
];

function isSensitiveKey(key: string): boolean {
  // Normalize snake_case, kebab-case and camelCase variants before matching.
  // Error payloads may use names such as access_token, refreshToken,
  // client_secret, apiKey, x-github-token or sessionCookie.
  const normalized = key.toLowerCase().replace(/[^a-z0-9]/g, "");
  return SENSITIVE_KEY_FRAGMENTS.some((fragment) => normalized.includes(fragment));
}

function redactSensitiveValues(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(redactSensitiveValues);
  }
  if (value && typeof value === "object") {
    const result: Record<string, unknown> = {};
    for (const [key, child] of Object.entries(value)) {
      if (!isSensitiveKey(key)) {
        result[key] = redactSensitiveValues(child);
      }
    }
    return result;
  }
  return value;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function messageFrom(value: Record<string, unknown>, fallback: string): string {
  if (typeof value.message === "string" && value.message.length > 0) return value.message;
  if (typeof value.detail === "string" && value.detail.length > 0) return value.detail;
  if (isRecord(value.detail) && typeof value.detail.message === "string") return value.detail.message;
  if (typeof value.error === "string" && value.error.length > 0) return value.error;
  return fallback;
}

/**
 * Normalize an already serialized Fastify error response. Existing HTTP status
 * codes remain authoritative. 4xx legacy detail/error/issues fields survive,
 * with sensitive validation inputs removed. 5xx bodies are deliberately
 * generic so upstream exception messages cannot leak to clients.
 */
export function normalizeApiErrorPayload(status: number, payload: unknown, contentType?: string): ApiErrorResponse {
  const code = codeForStatus(status);
  const decoded = decodePayload(payload, contentType);

  const legacy = isRecord(decoded)
    ? redactSensitiveValues(decoded) as Record<string, unknown>
    : decoded === undefined || decoded === null || decoded === ""
      ? {}
      : { detail: redactSensitiveValues(decoded) };

  if (status >= 500) {
    const detailMessage = messageFrom(legacy, DEFAULT_MESSAGES[code]);
    const isPauseResumeDisabled =
      status === 503
      && detailMessage === "Import pause/resume is disabled pending worker lifecycle validation";
    if (isPauseResumeDisabled) {
      return {
        ...legacy,
        code,
        message: detailMessage,
      } as ApiErrorResponse;
    }

    const message = DEFAULT_MESSAGES[code];
    return {
      code,
      message,
      error: status === 500
        ? "Internal Server Error"
        : status === 503
          ? "Service temporarily unavailable"
          : "Upstream engine request failed",
    };
  }

  return {
    ...legacy,
    code,
    message: messageFrom(legacy, DEFAULT_MESSAGES[code]),
  } as ApiErrorResponse;
}
