import { authRoute } from "./routes/auth";
import { dashboardRoute } from "./routes/dashboard";
import { decisionsRoute } from "./routes/decisions";
import { driftRoute } from "./routes/drift";
import cors from "@fastify/cors";
import Fastify from "fastify";
import { getEnv } from "./plugins/env";
import { governanceRoute } from "./routes/governance";
import { healthRoute } from "./routes/health";
import { importsRoute } from "./routes/imports";
import { queryRoute } from "./routes/query";
import { runtimeRoute } from "./routes/runtime";
import { teamRoute } from "./routes/team";
import { timelineRoute } from "./routes/timeline";

export function buildServer() {
  const app = Fastify({ logger: true });
  const env = getEnv();
  const origins = new Set(
    env.CORS_ALLOWED_ORIGINS.split(",").map((origin) => origin.trim()).filter(Boolean)
  );
  // Local demo: explicit localhost allowlist. Production: no cross-origin access by default.
  if (env.APP_ENV !== "production") {
    origins.add("http://127.0.0.1:3000");
    origins.add("http://localhost:3000");
  }
  // CORS alone does not block state-changing browser requests; reject hostile Origin headers.
  app.addHook("onRequest", async (request, reply) => {
    const origin = request.headers.origin;
    if (origin && !origins.has(origin) && !["GET", "HEAD", "OPTIONS"].includes(request.method)) {
      return reply.status(403).send({ error: "Origin not allowed" });
    }
  });
  app.register(cors, {
    origin: (origin, callback) => callback(null, !origin || origins.has(origin)),
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    credentials: true,
  });
  app.register(authRoute);
  app.register(healthRoute);
  app.register(importsRoute);
  app.register(governanceRoute);
  app.register(decisionsRoute);
  app.register(queryRoute);
  app.register(runtimeRoute);
  app.register(teamRoute);
  app.register(timelineRoute);
  app.register(dashboardRoute);
  app.register(driftRoute);
  return app;
}

async function start() {
  const env = getEnv();
  const app = buildServer();

  try {
    await app.listen({ port: env.PORT, host: "0.0.0.0" });
  } catch (error) {
    app.log.error(error);
    process.exit(1);
  }
}

if (require.main === module) {
  void start();
}
