import { FastifyInstance, FastifyRequest } from "fastify";
import { z } from "zod";

import type { LoginRequest, ScopeSwitchRequest } from "@decisionatlas/engine-contract";
import { clearSessionCookie, ensureSessionToken, SESSION_HEADER, setSessionCookie } from "../auth";
import { createAuthEngineClient, forwardContractTextRequest } from "../contracts/engine-client";
import { getEnv } from "../plugins/env";

const loginSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
});

const scopeSchema = z.object({
  owner_scope: z.string().min(1),
});

function sessionHeadersFromRequest(request: FastifyRequest): Record<string, string> {
  // Apply the same validated, bounded cookie-only session contract used by
  // every other BFF route; never accept a client-supplied auth header.
  const token = ensureSessionToken(request);
  return token ? { [SESSION_HEADER]: token } : {};
}

export async function authRoute(app: FastifyInstance) {
  app.post("/auth/bootstrap", async (_request, reply) => {
    const env = getEnv();
    const upstream = await forwardContractTextRequest(
      createAuthEngineClient(env.ENGINE_BASE_URL).POST("/auth/bootstrap", { parseAs: "text" }),
      app.log,
      "POST /auth/bootstrap",
    );
    const payload = upstream.payload as { session_token?: string } | null;
    if (typeof payload?.session_token === "string") {
      setSessionCookie(reply, payload.session_token);
    }
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/auth/logout", async (request, reply) => {
    const env = getEnv();
    const upstream = await forwardContractTextRequest(
      createAuthEngineClient(env.ENGINE_BASE_URL).POST("/auth/logout", {
        headers: sessionHeadersFromRequest(request),
        parseAs: "text",
      }),
      app.log,
      "POST /auth/logout",
    );
    clearSessionCookie(reply);
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.post("/auth/login", async (request, reply) => {
    const parsed = loginSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({ error: "Invalid login payload", issues: parsed.error.issues });
    }
    const env = getEnv();
    const body: LoginRequest = parsed.data;
    const upstream = await forwardContractTextRequest(
      createAuthEngineClient(env.ENGINE_BASE_URL).POST("/auth/login", {
        body,
        parseAs: "text",
      }),
      app.log,
      "POST /auth/login",
    );
    const payload = upstream.payload as { session_token?: string } | null;
    if (typeof payload?.session_token === "string") {
      setSessionCookie(reply, payload.session_token);
    }
    return reply.status(upstream.status).send(upstream.payload);
  });

  app.get("/auth/session", async (request, reply) => {
    const env = getEnv();
    const client = createAuthEngineClient(env.ENGINE_BASE_URL);
    let headers = sessionHeadersFromRequest(request);
    if (!headers[SESSION_HEADER] && !env.AUTO_BOOTSTRAP_AUTH) {
      return reply.status(401).send({ detail: "Authentication required" });
    }
    if (!headers[SESSION_HEADER] && env.AUTO_BOOTSTRAP_AUTH) {
      const bootstrap = await forwardContractTextRequest(
        client.POST("/auth/bootstrap", { parseAs: "text" }),
        app.log,
        "POST /auth/bootstrap",
      );
      const bootstrapPayload = bootstrap.payload as { session_token?: string } | null;
      if (typeof bootstrapPayload?.session_token === "string") {
        setSessionCookie(reply, bootstrapPayload.session_token);
        headers = { [SESSION_HEADER]: bootstrapPayload.session_token };
      }
    }
    const upstream = await forwardContractTextRequest(
      client.GET("/auth/session", { headers, parseAs: "text" }),
      app.log,
      "GET /auth/session",
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
    const body: ScopeSwitchRequest = parsed.data;
    const upstream = await forwardContractTextRequest(
      createAuthEngineClient(env.ENGINE_BASE_URL).POST("/auth/scope", {
        headers: sessionHeadersFromRequest(request),
        body,
        parseAs: "text",
      }),
      app.log,
      "POST /auth/scope",
    );
    return reply.status(upstream.status).send(upstream.payload);
  });
}
