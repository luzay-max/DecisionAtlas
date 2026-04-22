import type { FastifyBaseLogger, FastifyReply, FastifyRequest } from "fastify";

import { getEnv } from "./plugins/env";

export const SESSION_HEADER = "x-decisionatlas-session-token";

export function parseCookieHeader(header: string | undefined): Record<string, string> {
  if (!header) {
    return {};
  }
  return Object.fromEntries(
    header
      .split(";")
      .map((part) => part.trim())
      .filter(Boolean)
      .map((part) => {
        const [name, ...rest] = part.split("=");
        return [name, decodeURIComponent(rest.join("=") || "")];
      })
  );
}

function buildSessionCookie(name: string, value: string): string {
  return `${name}=${encodeURIComponent(value)}; Path=/; HttpOnly; SameSite=Lax`;
}

export function ensureSessionToken(request: FastifyRequest): string | null {
  const env = getEnv();
  const cookies = parseCookieHeader(request.headers.cookie);
  const existing = cookies[env.AUTH_COOKIE_NAME];
  return existing ?? null;
}

export async function authHeadersForRequest(request: FastifyRequest): Promise<Record<string, string>> {
  const token = ensureSessionToken(request);
  if (!token) {
    return {};
  }
  return { [SESSION_HEADER]: token };
}

export function setSessionCookie(reply: FastifyReply, sessionToken: string): void {
  const env = getEnv();
  reply.header("set-cookie", buildSessionCookie(env.AUTH_COOKIE_NAME, sessionToken));
}
