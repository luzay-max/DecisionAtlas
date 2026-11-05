import type { NextConfig } from "next";
import path from "node:path";

// API_BASE_URL is server-only; the browser sees /backend on its own origin.
// Keep the rewrite target fixed by deployment config, never by request input.
const apiOrigin = (process.env.API_BASE_URL ?? "http://127.0.0.1:3001").replace(/\/$/, "");

const nextConfig: NextConfig = {
  outputFileTracingRoot: path.resolve(__dirname, "../.."),
  async rewrites() {
    return [
      {
        source: "/backend/:path*",
        destination: `${apiOrigin}/:path*`,
      },
    ];
  },
};

export default nextConfig;
