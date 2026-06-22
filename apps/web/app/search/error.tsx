"use client";

import React from "react";

export default function SearchError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="home" style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
      <div className="panel" style={{ maxWidth: "600px", textAlign: "center", padding: "48px" }}>
        <p className="eyebrow" style={{ color: "var(--danger)" }}>Search error</p>
        <h2 style={{ marginTop: "12px", marginBottom: "16px" }}>Failed to load why-search</h2>
        <p style={{ color: "var(--muted)", marginBottom: "24px", lineHeight: 1.6 }}>
          {error.message || "Why-search could not be loaded. Check the engine, API, and LLM provider configuration."}
        </p>
        <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
          <button
            onClick={reset}
            className="action-link shimmer-btn"
            style={{ padding: "12px 24px", borderRadius: "99px", cursor: "pointer" }}
          >
            Try again
          </button>
          <a
            href="/"
            className="action-link shimmer-btn"
            style={{ padding: "12px 24px", borderRadius: "99px", textDecoration: "none" }}
          >
            Go home
          </a>
        </div>
      </div>
    </main>
  );
}
