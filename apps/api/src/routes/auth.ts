import { FastifyInstance, FastifyReply, FastifyRequest } from "fastify";
import { z } from "zod";

import { parseCookieHeader, SESSION_HEADER, setSessionCookie } from "../auth";
import { getEnv } from "../plugins/env";
import { fetchUpstreamPayload } from "../proxy";

const loginSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
});

const scopeSchema = z.object({
  owner_scope: z.string().min(1),
});

function sessionHeadersFromRequest(request: FastifyRequest): Record<string, string> {
  const env = getEnv();
  const cookies = parseCookieHeader(request.headers.cookie);
  const token = cookies[env.AUTH_COOKIE_NAME];
  return token ? { [SESSION_HEADER]: token } : {};
}

export async function authRoute(app: FastifyInstance) {
  app.post("/auth/bootstrap", async (_request, reply) => {
    const env = getEnv();
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/auth/bootstrap`, { method: "POST" }),
      app.log,
      "POST /auth/bootstrap"
    );
    const payload = upstream.payload as { session_token?: string } | null;
    if (typeof payload?.session_token === "string") {
      setSessionCookie(reply, payload.session_token);
    }
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/auth/login", async (request, reply) => {
    const parsed = loginSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({ error: "Invalid login payload", issues: parsed.error.issues });
    }
    const env = getEnv();
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(parsed.data),
      }),
      app.log,
      "POST /auth/login"
    );
    const payload = upstream.payload as { session_token?: string } | null;
    if (typeof payload?.session_token === "string") {
      setSessionCookie(reply, payload.session_token);
    }
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.get("/auth/session", async (request, reply) => {
    const env = getEnv();
    let headers = sessionHeadersFromRequest(request);
    if (!headers[SESSION_HEADER] && !env.AUTO_BOOTSTRAP_AUTH) {
      return reply.status(401).send({ detail: "Authentication required" });
    }
    if (!headers[SESSION_HEADER] && env.AUTO_BOOTSTRAP_AUTH) {
      const bootstrap = await fetchUpstreamPayload(
        fetch(`${env.ENGINE_BASE_URL}/auth/bootstrap`, { method: "POST" }),
        app.log,
        "POST /auth/bootstrap"
      );
      const bootstrapPayload = bootstrap.payload as { session_token?: string } | null;
      if (typeof bootstrapPayload?.session_token === "string") {
        setSessionCookie(reply, bootstrapPayload.session_token);
        headers = { [SESSION_HEADER]: bootstrapPayload.session_token };
      }
    }
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/auth/session`, {
        headers,
      }),
      app.log,
      "GET /auth/session"
    );
    const payload = upstream.payload as { session_token?: string } | null;
    if (typeof payload?.session_token === "string") {
      setSessionCookie(reply, payload.session_token);
    }
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/auth/scope", async (request, reply) => {
    const parsed = scopeSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({ error: "Invalid scope payload", issues: parsed.error.issues });
    }
    const env = getEnv();
    const upstream = await fetchUpstreamPayload(
      fetch(`${env.ENGINE_BASE_URL}/auth/scope`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          ...sessionHeadersFromRequest(request),
        },
        body: JSON.stringify(parsed.data),
      }),
      app.log,
      "POST /auth/scope"
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
