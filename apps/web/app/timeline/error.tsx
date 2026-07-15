"use client";

import React from "react";

export default function TimelineError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="home" style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
      <div className="panel" style={{ maxWidth: "600px", textAlign: "center", padding: "48px" }}>
        <p className="eyebrow" style={{ color: "var(--danger)" }}>Timeline error</p>
        <h2 style={{ marginTop: "12px", marginBottom: "16px" }}>Failed to load decision timeline</h2>
        <p style={{ color: "var(--muted)", marginBottom: "24px", lineHeight: 1.6 }}>
          {error.message || "The decision timeline could not be loaded. Check the engine and API services."}
        </p>
        <div className="card" style={{ textAlign: "left", marginBottom: "24px", padding: "20px" }}>
          <p style={{ fontWeight: 600, marginBottom: "8px" }}>Try these steps:</p>
          <ol style={{ margin: 0, paddingLeft: "20px", color: "var(--muted)", lineHeight: 1.8 }}>
            <li>Ensure the workspace has accepted decisions</li>
            <li>Check that the Engine service is running on port 8000</li>
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
