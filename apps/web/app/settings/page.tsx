"use client";

import React from "react";

import { GlobalSidebar } from "../../components/navigation/global-sidebar";
import { useI18n } from "../../components/i18n/language-provider";
import { ProviderModeToggle } from "../../components/runtime/provider-mode-toggle";

export default function SettingsPage() {
  const { messages } = useI18n();

  return (
    <>
      <GlobalSidebar />
      <main className="page-with-sidebar">
        <div className="panel">
          <p className="eyebrow">Settings</p>
          <h1>Configuration</h1>
          <p className="lede">
            Manage provider mode, workspace settings, and system configuration.
          </p>

          <section className="stack">
            <div className="card">
              <h3>LLM Provider</h3>
              <p className="muted" style={{ marginBottom: "16px" }}>
                Control whether the engine uses a live LLM provider or fake data for extraction runs.
              </p>
              <ProviderModeToggle />
            </div>

            <div className="card">
              <h3>System Status</h3>
              <div style={{ display: "grid", gap: "12px", marginTop: "12px" }}>
                <div className="action-row" style={{ justifyContent: "space-between" }}>
                  <span className="muted">Engine API</span>
                  <span className="badge">http://localhost:8000</span>
                </div>
                <div className="action-row" style={{ justifyContent: "space-between" }}>
                  <span className="muted">Gateway API</span>
                  <span className="badge">http://localhost:3001</span>
                </div>
                <div className="action-row" style={{ justifyContent: "space-between" }}>
                  <span className="muted">Web UI</span>
                  <span className="badge">http://localhost:3000</span>
                </div>
              </div>
            </div>

            <div className="card">
              <h3>Database</h3>
              <p className="muted" style={{ marginBottom: "12px" }}>
                PostgreSQL with pgvector for durable storage and vector search.
              </p>
              <div className="action-row" style={{ justifyContent: "space-between" }}>
                <span className="muted">PostgreSQL</span>
                <span className="badge">localhost:5432</span>
              </div>
            </div>

            <div className="card">
              <h3>Cache &amp; Queue</h3>
              <p className="muted" style={{ marginBottom: "12px" }}>
                Redis for background job coordination and caching.
              </p>
              <div className="action-row" style={{ justifyContent: "space-between" }}>
                <span className="muted">Redis</span>
                <span className="badge">localhost:6379</span>
              </div>
            </div>
          </section>
        </div>
      </main>
    </>
  );
}
