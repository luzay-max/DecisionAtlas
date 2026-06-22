import React from "react";

export default function Loading() {
  return (
    <main className="home" style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
      <div className="panel" style={{ maxWidth: "600px", textAlign: "center", padding: "48px" }}>
        <div
          style={{
            width: "40px",
            height: "40px",
            border: "3px solid var(--line)",
            borderTopColor: "var(--accent)",
            borderRadius: "50%",
            animation: "spin 0.8s linear infinite",
            margin: "0 auto 24px",
          }}
        />
        <p style={{ color: "var(--muted)" }}>Loading...</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    </main>
  );
}
