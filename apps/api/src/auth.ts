import type { FastifyReply, FastifyRequest } from "fastify";

import { getEnv } from "./plugins/env";

export const SESSION_HEADER = "x-decisionatlas-session-token";

export function parseCookieHeader(header: string | undefined): Record<string, string> {
  // A malformed or oversized cookie must never crash an authenticated BFF
  // route. Duplicate names are ambiguous (cookie tossing): reject both.
  const result: Record<string, string> = Object.create(null);
  if (!header || header.length > 8192) {
    return result;
  }
  const parts = header.split(";");
  if (parts.length > 64) {
    return result;
  }
  const duplicates = new Set<string>();
  for (const part of parts) {
    const index = part.indexOf("=");
    if (index <= 0) continue;
    const name = part.slice(0, index).trim();
    const encoded = part.slice(index + 1).trim();
    if (!/^[A-Za-z0-9_-]{1,128}$/.test(name) || encoded.length > 4096) continue;
    if (Object.hasOwn(result, name) || duplicates.has(name)) {
      delete result[name];
      duplicates.add(name);
      continue;
    }
    try {
      const value = decodeURIComponent(encoded);
      if (!value || /[\\u0000-\\u001f\\u007f]/.test(value)) continue;
      result[name] = value;
    } catch {
      // Invalid %-encoding fails closed for this cookie, not the whole request.
      duplicates.add(name);
    }
  }
  return result;
}

function buildSessionCookie(name: string, value: string, clear = false): string {
  const env = getEnv();
  const secure = env.APP_ENV === "production" || process.env.NODE_ENV === "production";
  const expiry = clear ? "; Max-Age=0" : "";
  return `${name}=${encodeURIComponent(value)}; Path=/; HttpOnly; SameSite=Lax${secure ? "; Secure" : ""}${expiry}`;
}

export function ensureSessionToken(request: FastifyRequest): string | null {
  const env = getEnv();
  const cookies = parseCookieHeader(request.headers.cookie);
  const existing = cookies[env.AUTH_COOKIE_NAME];
  // The token is forwarded in a protected header, never from an arbitrary
  // request header or browser localStorage. Do not accept control characters.
  return existing && existing.length <= 2048 ? existing : null;
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

export function clearSessionCookie(reply: FastifyReply): void {
  const env = getEnv();
  reply.header("set-cookie", buildSessionCookie(env.AUTH_COOKIE_NAME, "", true));
}
