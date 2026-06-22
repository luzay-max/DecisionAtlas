"use client";

import React, { useEffect, useState } from "react";

import { GlobalSidebar } from "../../components/navigation/global-sidebar";
import { useI18n } from "../../components/i18n/language-provider";

interface EvidenceEntry {
  id: string;
  label: string;
  status: string;
  generatedAt: string;
  type: string;
}

export default function EvidencePage() {
  const { messages } = useI18n();
  const [evidence, setEvidence] = useState<EvidenceEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadEvidence() {
      try {
        const res = await fetch("http://localhost:8000/api/v1/runtime/guardrail?summary=true");
        if (res.ok) {
          const data = await res.json();
          setEvidence([
            {
              id: "guardrail",
              label: "Governance Guardrail Status",
              status: data.status || "unknown",
              generatedAt: new Date().toISOString(),
              type: "guardrail",
            },
          ]);
        }
      } catch {
        setEvidence([]);
      } finally {
        setLoading(false);
      }
    }
    loadEvidence();
  }, []);

  return (
    <>
      <GlobalSidebar />
      <main className="page-with-sidebar">
        <div className="panel">
          <p className="eyebrow">Evidence &amp; Reports</p>
          <h1>Evidence Dashboard</h1>
          <p className="lede">
            View release evidence, governance guardrail status, and audit reports.
          </p>

          <section className="stack">
            {loading ? (
              <div className="card">
                <p className="muted">Loading evidence...</p>
              </div>
            ) : evidence.length === 0 ? (
              <div className="card">
                <p className="muted">
                  No evidence entries found. Start the real stack and run governance checks to generate evidence.
                </p>
              </div>
            ) : (
              evidence.map((entry) => (
                <div key={entry.id} className="card">
                  <div className="card-head">
                    <h3>{entry.label}</h3>
                    <span className={`badge ${entry.status === "continue" ? "compact-badge" : ""}`}>
                      {entry.status}
                    </span>
                  </div>
                  <p className="muted" style={{ marginTop: "8px" }}>
                    Generated: {new Date(entry.generatedAt).toLocaleString()}
                  </p>
                </div>
              ))
            )}

            <div className="card">
              <h3>Available Reports</h3>
              <p className="muted" style={{ marginBottom: "16px" }}>
                Generate detailed reports using the CLI scripts:
              </p>
              <div style={{ display: "grid", gap: "8px", fontFamily: "var(--font-mono)", fontSize: "0.85rem" }}>
                <code className="card" style={{ padding: "12px 16px" }}>
                  python scripts/governance/agent_guardrail.py --summary
                </code>
                <code className="card" style={{ padding: "12px 16px" }}>
                  python scripts/ci/collect_code_decision_audit_report.py
                </code>
                <code className="card" style={{ padding: "12px 16px" }}>
                  python scripts/ci/collect_team_handoff_report.py
                </code>
              </div>
            </div>

            <div className="card">
              <h3>Self-Hosted Package</h3>
              <p className="muted" style={{ marginBottom: "12px" }}>
                Build and verify the self-hosted deployment package:
              </p>
              <div style={{ display: "grid", gap: "8px", fontFamily: "var(--font-mono)", fontSize: "0.85rem" }}>
                <code className="card" style={{ padding: "12px 16px" }}>
                  python scripts/ci/build_self_hosted_package.py
                </code>
                <code className="card" style={{ padding: "12px 16px" }}>
                  python scripts/ci/verify_self_hosted_package.py
                </code>
              </div>
            </div>
          </section>
        </div>
      </main>
    </>
  );
}
