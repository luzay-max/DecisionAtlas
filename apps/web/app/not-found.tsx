import Link from "next/link";
import React from "react";

export default function NotFound() {
  return (
    <main className="home" style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
      <div className="panel" style={{ maxWidth: "600px", textAlign: "center", padding: "48px" }}>
        <p className="eyebrow" style={{ color: "var(--warning)" }}>404</p>
        <h2 style={{ marginTop: "12px", marginBottom: "16px" }}>Page not found</h2>
        <p style={{ color: "var(--muted)", marginBottom: "24px", lineHeight: 1.6 }}>
          The page you are looking for does not exist or has been moved.
        </p>
        <div className="card" style={{ textAlign: "left", marginBottom: "24px", padding: "20px" }}>
          <p style={{ fontWeight: 600, marginBottom: "8px" }}>You can try:</p>
          <ul style={{ margin: 0, paddingLeft: "20px", color: "var(--muted)", lineHeight: 1.8 }}>
            <li>Go to the <Link href="/" style={{ color: "var(--accent)" }}>homepage</Link> and navigate from there</li>
            <li>Check the URL for typos</li>
            <li>Use the sidebar navigation to find what you need</li>
          </ul>
        </div>
        <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
          <Link
            href="/"
            className="action-link shimmer-btn"
            style={{ padding: "12px 24px", borderRadius: "99px", textDecoration: "none" }}
          >
            Go home
          </Link>
        </div>
      </div>
    </main>
  );
}
