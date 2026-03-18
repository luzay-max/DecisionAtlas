import { dashboardRoute } from "./routes/dashboard";
import { decisionsRoute } from "./routes/decisions";
import { driftRoute } from "./routes/drift";
import Fastify from "fastify";
import { getEnv } from "./plugins/env";
import { healthRoute } from "./routes/health";
import { importsRoute } from "./routes/imports";
import { queryRoute } from "./routes/query";
import { timelineRoute } from "./routes/timeline";

export function buildServer() {
  const app = Fastify({ logger: true });
  app.register(healthRoute);
  app.register(importsRoute);
  app.register(decisionsRoute);
  app.register(queryRoute);
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
