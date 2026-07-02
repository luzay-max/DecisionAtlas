"use client";

import React, { useEffect, useState } from "react";

import { GlobalSidebar } from "../../components/navigation/global-sidebar";
import { getGovernanceGuardrail } from "../../lib/api";

interface EvidenceEntry {
  id: string;
  label: string;
  status: string;
  generatedAt: string;
  type: string;
}

export default function EvidencePage() {
  const [evidence, setEvidence] = useState<EvidenceEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadEvidence() {
      try {
        const data = await getGovernanceGuardrail();
        setEvidence([
          {
            id: "guardrail",
            label: "Governance Guardrail Status",
            status: data.agent_status || "unknown",
            generatedAt: new Date().toISOString(),
            type: "guardrail",
          },
        ]);
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
            Answer the operator question: can this build be released, demonstrated, or handed off with enough evidence?
          </p>

          <section className="stack">
            <div className="card">
              <p className="eyebrow">Operator readiness</p>
              <h2>Release evidence checklist</h2>
              <div className="flow-grid">
                <div className="card flow-card">
                  <h3>Guardrail summary</h3>
                  <p className="muted">Governance status and required human decisions.</p>
                  <span className="badge">{evidence.find((entry) => entry.type === "guardrail")?.status ?? "missing"}</span>
                </div>
                <div className="card flow-card">
                  <h3>Benchmark comparison</h3>
                  <p className="muted">Trend evidence for real repository quality across releases.</p>
                  <span className="badge">collect evidence</span>
                </div>
                <div className="card flow-card">
                  <h3>Hosted readiness</h3>
                  <p className="muted">Operator-guided deployment, recovery, and demo evidence.</p>
                  <span className="badge">collect evidence</span>
                </div>
                <div className="card flow-card">
                  <h3>Release evidence</h3>
                  <p className="muted">JSON/Markdown evidence package for release notes and handoff.</p>
                  <span className="badge">collect evidence</span>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="card">
                <p className="muted">Loading evidence...</p>
              </div>
            ) : evidence.length === 0 ? (
              <div className="card">
                <p className="eyebrow">Missing evidence</p>
                <h3>Generate readiness evidence before release</h3>
                <p className="muted">
                  No evidence entries found. Start the real stack, run governance checks, benchmark comparison, and hosted readiness collection.
                </p>
                <div className="action-row">
                  <a href="#evidence-commands" className="action-link action-link-primary">
                    Show evidence commands
                  </a>
                  <a href="/settings" className="action-link">
                    Check system settings
                  </a>
                </div>
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

            <div id="evidence-commands" className="card">
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
