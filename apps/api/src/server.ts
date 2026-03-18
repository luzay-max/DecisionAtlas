import Fastify from "fastify";
import { getEnv } from "./plugins/env";
import { healthRoute } from "./routes/health";
import { importsRoute } from "./routes/imports";

export function buildServer() {
  const app = Fastify({ logger: true });
  app.register(healthRoute);
  app.register(importsRoute);
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
