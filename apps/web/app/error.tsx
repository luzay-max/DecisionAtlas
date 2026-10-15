"use client";

import React from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="home" style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
      <div className="panel" style={{ maxWidth: "600px", textAlign: "center", padding: "48px" }}>
        <p className="eyebrow" style={{ color: "var(--danger)" }}>Something went wrong</p>
        <h2 style={{ marginTop: "12px", marginBottom: "16px" }}>Unexpected error</h2>
        <p style={{ color: "var(--muted)", marginBottom: "24px", lineHeight: 1.6 }}>
          {error.message || "An unexpected error occurred."}
        </p>
        {error.digest && (
          <p style={{ color: "var(--muted)", fontSize: "0.8rem", fontFamily: "var(--font-mono)", marginBottom: "24px" }}>
            Error ID: {error.digest}
          </p>
        )}
        <div className="card" style={{ textAlign: "left", marginBottom: "24px", padding: "20px" }}>
          <p style={{ fontWeight: 600, marginBottom: "8px" }}>Try these steps:</p>
          <ol style={{ margin: 0, paddingLeft: "20px", color: "var(--muted)", lineHeight: 1.8 }}>
            <li>Click &quot;Try again&quot; to retry the failed operation</li>
            <li>Check that the Engine (port 8000) and API (port 3001) services are running</li>
            <li>Refresh the page to reload from scratch</li>
            <li>If the problem persists, check the browser console for details</li>
          </ol>
        </div>
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
